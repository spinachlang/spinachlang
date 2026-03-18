"""Tests for all extended gates:
  • New 1-qubit: SX, SXDG, V, VDG, U1, U2, U3, TK1, PX/PHASEDX
  • New 2-qubit: CRX, CRY, CRZ, ECR, ISWAP, ISWAPMAX, ZZMAX, ZZPH, XXPH, YYPH,
                 FSIM, TK2, PHISWAP
  • New 3-qubit: CSWAP / FREDKIN, XXP3
  • Global phase: PHASE
  • CircBox: CIRCBOX
  • Float angles through the full grammar → circuit pipeline
"""

import unittest

from pytket import Qubit, Bit
from pytket.circuit import OpType

from spinachlang.spinach import Spinach
from spinachlang.backend import Backend
from spinachlang.spinach_types import (
    QubitDeclaration,
    Action,
    GatePipeline,
    GateCall,
    InstructionDeclaration,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ast_action(target, gate_name: str, args=None):
    """Return a minimal one-gate Action AST node."""
    return Action(
        target=target,
        instruction=GatePipeline(parts=[GateCall(name=gate_name, args=args or [])]),
    )


def _qubits(*indices):
    """Return a list of QubitDeclaration AST nodes for the given indices."""
    return [QubitDeclaration(name=f"q{i}", qubit=Qubit("q", i)) for i in indices]


def _compile(*ast_nodes):
    return Backend.compile_to_circuit(list(ast_nodes))


def _op_types(circuit):
    return [cmd.op.type for cmd in circuit.get_commands()]


def _source_circuit(code: str):
    return Spinach.create_circuit(code)


# ---------------------------------------------------------------------------
# 1-qubit gates (AST path)
# ---------------------------------------------------------------------------

class TestNew1QubitGates(unittest.TestCase):
    """Verify each new 1-qubit gate is wired up to the correct TKET OpType."""

    def _gate(self, gate_name, args=None):
        circuit = _compile(*_qubits(0), _ast_action(0, gate_name, args))
        return circuit.get_commands()

    # ── no-param gates ────────────────────────────────────────────────────

    def test_sx(self):
        cmds = self._gate("SX")
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.SX)
        self.assertEqual(cmds[0].qubits, [Qubit("q", 0)])

    def test_sxdg(self):
        cmds = self._gate("SXDG")
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.SXdg)

    def test_v(self):
        cmds = self._gate("V")
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.V)

    def test_vdg(self):
        cmds = self._gate("VDG")
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.Vdg)

    # ── parametric gates ──────────────────────────────────────────────────

    def test_u1(self):
        cmds = self._gate("U1", [0.5])
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.U1)

    def test_u2(self):
        cmds = self._gate("U2", [0.5, 0.25])
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.U2)

    def test_u3(self):
        cmds = self._gate("U3", [0.5, 0.25, 0.1])
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.U3)

    def test_tk1(self):
        cmds = self._gate("TK1", [0.5, 0.25, 0.1])
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.TK1)

    def test_px_phasedx(self):
        """PX and PHASEDX are aliases for PhasedX."""
        for name in ("PX", "PHASEDX"):
            with self.subTest(gate=name):
                cmds = self._gate(name, [0.5, 0.25])
                self.assertEqual(len(cmds), 1)
                self.assertEqual(cmds[0].op.type, OpType.PhasedX)

    # ── arity errors ──────────────────────────────────────────────────────

    def test_u1_wrong_arity(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0), _ast_action(0, "U1", []))

    def test_u2_wrong_arity(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0), _ast_action(0, "U2", [0.5]))

    def test_u3_wrong_arity(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0), _ast_action(0, "U3", [0.5, 0.25]))

    def test_tk1_wrong_arity(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0), _ast_action(0, "TK1", [0.5]))

    def test_phasedx_wrong_arity(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0), _ast_action(0, "PX", [0.5]))


# ---------------------------------------------------------------------------
# 2-qubit gates (AST path)
# ---------------------------------------------------------------------------

class TestNew2QubitGates(unittest.TestCase):
    """Each new 2-qubit gate resolves to the expected TKET OpType.

    Convention: `target -> GATE(angle?, ctrl_or_other)`
    i.e. target = qubit 0, the qubit arg = qubit 1.
    """

    def _gate2(self, gate_name, args):
        """args must include the 'other' qubit index as last element."""
        circuit = _compile(*_qubits(0, 1), _ast_action(0, gate_name, args))
        cmds = circuit.get_commands()
        self.assertEqual(len(cmds), 1)
        return cmds[0]

    # Controlled rotations

    def test_crx(self):
        cmd = self._gate2("CRX", [0.5, 1])
        self.assertEqual(cmd.op.type, OpType.CRx)

    def test_cry(self):
        cmd = self._gate2("CRY", [0.5, 1])
        self.assertEqual(cmd.op.type, OpType.CRy)

    def test_crz(self):
        cmd = self._gate2("CRZ", [0.5, 1])
        self.assertEqual(cmd.op.type, OpType.CRz)

    # Cross-resonance

    def test_ecr(self):
        cmd = self._gate2("ECR", [1])
        self.assertEqual(cmd.op.type, OpType.ECR)

    # iSWAP family

    def test_iswap(self):
        cmd = self._gate2("ISWAP", [1, 1])
        self.assertEqual(cmd.op.type, OpType.ISWAP)

    def test_iswapmax(self):
        cmd = self._gate2("ISWAPMAX", [1])
        self.assertEqual(cmd.op.type, OpType.ISWAPMax)

    # ZZ/XX/YY family

    def test_zzmax(self):
        cmd = self._gate2("ZZMAX", [1])
        self.assertEqual(cmd.op.type, OpType.ZZMax)

    def test_zzph(self):
        cmd = self._gate2("ZZPH", [0.5, 1])
        self.assertEqual(cmd.op.type, OpType.ZZPhase)

    def test_xxph(self):
        cmd = self._gate2("XXPH", [0.5, 1])
        self.assertEqual(cmd.op.type, OpType.XXPhase)

    def test_yyph(self):
        cmd = self._gate2("YYPH", [0.5, 1])
        self.assertEqual(cmd.op.type, OpType.YYPhase)

    # Parametric 2-qubit

    def test_fsim(self):
        circuit = _compile(*_qubits(0, 1), _ast_action(0, "FSIM", [0.5, 0.25, 1]))
        cmds = circuit.get_commands()
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.FSim)

    def test_tk2(self):
        circuit = _compile(*_qubits(0, 1), _ast_action(0, "TK2", [0.5, 0.25, 0.1, 1]))
        cmds = circuit.get_commands()
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.TK2)

    def test_phiswap(self):
        circuit = _compile(*_qubits(0, 1), _ast_action(0, "PHISWAP", [0.5, 0.25, 1]))
        cmds = circuit.get_commands()
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.PhasedISWAP)

    # Arity errors

    def test_crx_wrong_arity(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0), _ast_action(0, "CRX", [0.5]))

    def test_ecr_wrong_arity(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0), _ast_action(0, "ECR", []))

    def test_iswap_wrong_arity(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0), _ast_action(0, "ISWAP", [0.5]))

    def test_fsim_wrong_arity(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0, 1), _ast_action(0, "FSIM", [0.5, 0.25]))

    def test_tk2_wrong_arity(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0, 1), _ast_action(0, "TK2", [0.5, 0.25, 0.1]))


# ---------------------------------------------------------------------------
# 3-qubit gates (AST path)
# ---------------------------------------------------------------------------

class TestNew3QubitGates(unittest.TestCase):

    def test_cswap_fredkin(self):
        """CSWAP(ctrl, other): target↔other when ctrl=|1⟩."""
        for name in ("CSWAP", "FREDKIN"):
            with self.subTest(gate=name):
                circuit = _compile(*_qubits(0, 1, 2), _ast_action(0, name, [1, 2]))
                cmds = circuit.get_commands()
                self.assertEqual(len(cmds), 1)
                self.assertEqual(cmds[0].op.type, OpType.CSWAP)

    def test_cswap_qubit_set(self):
        """All three qubits (ctrl, tgt0, tgt1) appear in the command."""
        circuit = _compile(*_qubits(0, 1, 2), _ast_action(0, "CSWAP", [1, 2]))
        cmd = circuit.get_commands()[0]
        self.assertEqual(set(cmd.qubits), {Qubit("q", 0), Qubit("q", 1), Qubit("q", 2)})

    def test_xxp3(self):
        circuit = _compile(*_qubits(0, 1, 2), _ast_action(0, "XXP3", [0.5, 1, 2]))
        cmds = circuit.get_commands()
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.XXPhase3)

    def test_cswap_wrong_arity(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0, 1, 2), _ast_action(0, "CSWAP", [1]))

    def test_xxp3_wrong_arity(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0, 1, 2), _ast_action(0, "XXP3", [0.5, 1]))


# ---------------------------------------------------------------------------
# Global phase (AST path)
# ---------------------------------------------------------------------------

class TestGlobalPhase(unittest.TestCase):

    def test_phase_changes_circuit_phase(self):
        """PHASE(0.5) increments circuit.phase by 0.5."""
        circuit = _compile(*_qubits(0), _ast_action(0, "PHASE", [0.5]))
        # add_phase accumulates; starting from 0 we expect 0.5
        self.assertAlmostEqual(float(circuit.phase), 0.5)

    def test_phase_accumulates(self):
        """Two PHASE(0.5) calls give circuit.phase ≈ 1.0."""
        ast = [
            *_qubits(0),
            _ast_action(0, "PHASE", [0.5]),
            _ast_action(0, "PHASE", [0.5]),
        ]
        circuit = Backend.compile_to_circuit(ast)
        self.assertAlmostEqual(float(circuit.phase), 1.0)

    def test_phase_missing_arg_raises(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0), _ast_action(0, "PHASE", []))

    def test_phase_does_not_add_gates(self):
        """Global phase should not add any gate commands."""
        circuit = _compile(*_qubits(0), _ast_action(0, "PHASE", [1]))
        self.assertEqual(circuit.get_commands(), [])


# ---------------------------------------------------------------------------
# CircBox (AST path)
# ---------------------------------------------------------------------------

class TestCircBox(unittest.TestCase):

    def test_circbox_bell_state(self):
        """[q0, q1] -> CIRCBOX(bell) wraps H|CX into a CircBox."""
        bell_pipeline = GatePipeline(parts=[
            GateCall(name="H"),
            GateCall(name="CX", args=[1]),  # ctrl = qubit index 1 in the box
        ])
        bell_instr = InstructionDeclaration(name="bell", pipeline=bell_pipeline)
        action = Action(
            target=[0, 1],
            instruction=GatePipeline(parts=[GateCall(name="CIRCBOX", args=["bell"])]),
        )
        circuit = Backend.compile_to_circuit([
            *_qubits(0, 1),
            bell_instr,
            action,
        ])
        cmds = circuit.get_commands()
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.CircBox)

    def test_circbox_single_qubit(self):
        """Single-qubit CircBox wraps an H gate."""
        h_instr = InstructionDeclaration(
            name="myh",
            pipeline=GatePipeline(parts=[GateCall(name="H")]),
        )
        action = Action(
            target=[0],
            instruction=GatePipeline(parts=[GateCall(name="CIRCBOX", args=["myh"])]),
        )
        circuit = Backend.compile_to_circuit([*_qubits(0), h_instr, action])
        cmds = circuit.get_commands()
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.CircBox)

    def test_circbox_missing_arg_raises(self):
        with self.assertRaises(ValueError):
            _compile(*_qubits(0), _ast_action(0, "CIRCBOX", []))

    def test_circbox_non_pipeline_arg_raises(self):
        """Passing a raw integer instead of a pipeline name must raise."""
        with self.assertRaises(ValueError):
            _compile(*_qubits(0), _ast_action(0, "CIRCBOX", [42]))

    def test_circbox_no_qubit_targets_is_noop(self):
        """An empty target list means the action loop never fires — CIRCBOX is a no-op."""
        bell_pipeline = GatePipeline(parts=[GateCall(name="H")])
        bell_instr = InstructionDeclaration(name="b", pipeline=bell_pipeline)
        action = Action(
            target=[],
            instruction=GatePipeline(parts=[GateCall(name="CIRCBOX", args=["b"])]),
        )
        circuit = Backend.compile_to_circuit([*_qubits(0), bell_instr, action])
        # No gate commands emitted – target list was empty
        self.assertEqual(circuit.get_commands(), [])


# ---------------------------------------------------------------------------
# CY bug regression (was using DEFAULT_BIT_REGISTER for controller)
# ---------------------------------------------------------------------------

class TestCYBugRegression(unittest.TestCase):

    def test_cy_uses_qubit_register(self):
        """CY gate should add ctrl as a Qubit (not a Bit) to the circuit."""
        circuit = _compile(*_qubits(0, 1), _ast_action(0, "CY", [1]))
        cmds = circuit.get_commands()
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.CY)
        # Both operands must be Qubits, not Bits
        self.assertIn(Qubit("q", 0), circuit.qubits)
        self.assertIn(Qubit("q", 1), circuit.qubits)


# ---------------------------------------------------------------------------
# Grammar + float angles (end-to-end via Spinach source)
# ---------------------------------------------------------------------------

class TestGrammarDigitsAndFloats(unittest.TestCase):
    """End-to-end tests that go through the full grammar → circuit pipeline."""

    def test_u3_from_source(self):
        """U3(0.5, 0.25, 0.1) is valid source syntax after grammar fix."""
        code = "0 -> U3(0.5, 0.25, 0.1)"
        circuit = _source_circuit(code)
        types = _op_types(circuit)
        self.assertIn(OpType.U3, types)

    def test_tk1_from_source(self):
        """TK1 has a digit in its name – needs UPPER_NAME regex fix."""
        code = "0 -> TK1(0.5, 0.25, 0.1)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.TK1, _op_types(circuit))

    def test_tk2_from_source(self):
        code = "0 -> TK2(0.5, 0.25, 0.1, 1)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.TK2, _op_types(circuit))

    def test_u1_from_source(self):
        code = "0 -> U1(1)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.U1, _op_types(circuit))

    def test_u2_from_source(self):
        code = "0 -> U2(0.5, 0.25)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.U2, _op_types(circuit))

    def test_sx_from_source(self):
        code = "0 -> SX"
        circuit = _source_circuit(code)
        self.assertIn(OpType.SX, _op_types(circuit))

    def test_sxdg_from_source(self):
        code = "0 -> SXDG"
        circuit = _source_circuit(code)
        self.assertIn(OpType.SXdg, _op_types(circuit))

    def test_v_from_source(self):
        code = "0 -> V"
        circuit = _source_circuit(code)
        self.assertIn(OpType.V, _op_types(circuit))

    def test_vdg_from_source(self):
        code = "0 -> VDG"
        circuit = _source_circuit(code)
        self.assertIn(OpType.Vdg, _op_types(circuit))

    def test_crx_from_source(self):
        code = "0 -> CRX(0.5, 1)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.CRx, _op_types(circuit))

    def test_ecr_from_source(self):
        code = "0 -> ECR(1)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.ECR, _op_types(circuit))

    def test_iswap_from_source(self):
        code = "0 -> ISWAP(1, 1)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.ISWAP, _op_types(circuit))

    def test_iswapmax_from_source(self):
        code = "0 -> ISWAPMAX(1)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.ISWAPMax, _op_types(circuit))

    def test_zzmax_from_source(self):
        code = "0 -> ZZMAX(1)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.ZZMax, _op_types(circuit))

    def test_zzph_from_source(self):
        code = "0 -> ZZPH(0.5, 1)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.ZZPhase, _op_types(circuit))

    def test_xxph_from_source(self):
        code = "0 -> XXPH(0.5, 1)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.XXPhase, _op_types(circuit))

    def test_yyph_from_source(self):
        code = "0 -> YYPH(0.5, 1)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.YYPhase, _op_types(circuit))

    def test_fsim_from_source(self):
        code = "0 -> FSIM(0.5, 0.25, 1)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.FSim, _op_types(circuit))

    def test_phiswap_from_source(self):
        code = "0 -> PHISWAP(0.5, 0.25, 1)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.PhasedISWAP, _op_types(circuit))

    def test_cswap_from_source(self):
        code = "0 -> CSWAP(1, 2)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.CSWAP, _op_types(circuit))

    def test_fredkin_alias_from_source(self):
        code = "0 -> FREDKIN(1, 2)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.CSWAP, _op_types(circuit))

    def test_xxp3_from_source(self):
        code = "0 -> XXP3(0.5, 1, 2)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.XXPhase3, _op_types(circuit))

    def test_phase_from_source(self):
        code = "0 -> PHASE(1)"
        circuit = _source_circuit(code)
        self.assertAlmostEqual(float(circuit.phase), 1.0)

    def test_phasedx_alias_from_source(self):
        code = "0 -> PHASEDX(0.5, 0.25)"
        circuit = _source_circuit(code)
        self.assertIn(OpType.PhasedX, _op_types(circuit))

    def test_float_rx_angle(self):
        """RX(0.5) — decimal angle parsed correctly."""
        code = "0 -> RX(0.5)"
        circuit = _source_circuit(code)
        cmds = circuit.get_commands()
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.Rx)
        self.assertAlmostEqual(float(cmds[0].op.params[0]), 0.5)

    def test_integer_rx_angle(self):
        """RX(1) — integer angle still works."""
        code = "0 -> RX(1)"
        circuit = _source_circuit(code)
        cmds = circuit.get_commands()
        self.assertEqual(cmds[0].op.type, OpType.Rx)
        self.assertAlmostEqual(float(cmds[0].op.params[0]), 1.0)

    def test_circbox_from_source(self):
        """End-to-end CIRCBOX test through the grammar."""
        code = """
        bell : H | CX(1)
        q0 : q 0
        q1 : q 1
        [q0, q1] -> CIRCBOX(bell)
        """
        circuit = _source_circuit(code)
        cmds = circuit.get_commands()
        self.assertEqual(len(cmds), 1)
        self.assertEqual(cmds[0].op.type, OpType.CircBox)


if __name__ == "__main__":
    unittest.main()


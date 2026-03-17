"""backend of spinach"""

import json
from typing import Optional, Union
from pytket import Circuit, Qubit, Bit
from pytket.qasm import circuit_to_qasm_str

from .spinach_types import (
    GateCall,
    GatePipeByName,
    GatePipeline,
    QubitDeclaration,
    BitDeclaration,
    InstructionDeclaration,
    ListDeclaration,
    Action,
    ConditionalAction,
)


class Backend:
    """backend of spinach"""

    DEFAULT_QUBIT_REGISTER = "q"
    DEFAULT_BIT_REGISTER = "c"

    @staticmethod
    def __handle_x_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """X gate"""
        c.X(target, **(cond or {}))

    @staticmethod
    def __handle_y_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """Y gate"""
        c.Y(target, **(cond or {}))

    @staticmethod
    def __handle_z_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """Z gate"""
        c.Z(target, **(cond or {}))

    @staticmethod
    def __handle_h_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """H gate"""
        c.H(target, **(cond or {}))

    @staticmethod
    def __handle_s_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """S gate"""
        c.S(target, **(cond or {}))

    @staticmethod
    def __handle_t_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """T gate"""
        c.T(target, **(cond or {}))

    @staticmethod
    def __handle_sdg_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """S dagger gate"""
        c.Sdg(target, **(cond or {}))

    @staticmethod
    def __handle_tdg_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """T dagger gate"""
        c.Tdg(target, **(cond or {}))

    @staticmethod
    def __handle_rx_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """RX gate"""
        c.Rx(args[0], target, **(cond or {}))

    @staticmethod
    def __handle_ry_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """RY gate"""
        c.Ry(args[0], target, **(cond or {}))

    @staticmethod
    def __handle_rz_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """RZ gate"""
        c.Rz(args[0], target, **(cond or {}))

    @staticmethod
    def __handle_cx_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """CX gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        )
        Backend.__ensure_qubit(c, controller)
        c.CX(controller, target, **(cond or {}))

    @staticmethod
    def __handle_fliped_cx_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """FCX gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        )
        Backend.__ensure_qubit(c, controller)
        c.CX(target, controller, **(cond or {}))

    @staticmethod
    def __handle_cy_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """CY gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(Backend.DEFAULT_BIT_REGISTER, args[0])
        )
        Backend.__ensure_qubit(c, controller)
        c.CY(controller, target, **(cond or {}))

    @staticmethod
    def __handle_fliped_cy_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """FCY gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        )
        Backend.__ensure_qubit(c, controller)
        c.CY(target, controller, **(cond or {}))

    @staticmethod
    def __handle_cz_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """CZ gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        )
        Backend.__ensure_qubit(c, controller)
        c.CZ(controller, target, **(cond or {}))

    @staticmethod
    def __handle_fliped_cz_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """FCZ gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        )
        Backend.__ensure_qubit(c, controller)
        c.CZ(target, controller, **(cond or {}))

    @staticmethod
    def __handle_ch_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """CH gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        )
        Backend.__ensure_qubit(c, controller)
        c.CH(controller, target, **(cond or {}))

    @staticmethod
    def __handle_fliped_ch_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """FCH gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        )
        Backend.__ensure_qubit(c, controller)
        c.CH(target, controller, **(cond or {}))

    @staticmethod
    def __handle_cu1_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """CU1 gate"""
        controller = (
            args[1]
            if isinstance(args[1], Qubit)
            else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[1])
        )
        Backend.__ensure_qubit(c, controller)
        c.CU1(args[0], controller, target, **(cond or {}))

    @staticmethod
    def __handle_swap_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """SWAP gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        )
        Backend.__ensure_qubit(c, controller)
        c.SWAP(target, controller, **(cond or {}))

    @staticmethod
    def __handle_ccx_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """CCX gate"""
        controller1 = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        )
        controller2 = (
            args[1]
            if isinstance(args[1], Qubit)
            else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[1])
        )
        Backend.__ensure_qubit(c, controller1)
        Backend.__ensure_qubit(c, controller2)
        c.CCX(controller1, controller2, target, **(cond or {}))

    @staticmethod
    def __handle_measure_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """measure gate"""
        if len(args) < 1:
            bit = Bit(Backend.DEFAULT_BIT_REGISTER, target.index[0])
        else:
            bit = (
                args[0]
                if isinstance(args[0], Bit)
                else Bit(Backend.DEFAULT_BIT_REGISTER, args[0])
            )
        Backend.__ensure_bit(c, bit)
        c.Measure(target, bit, **(cond or {}))

    @staticmethod
    def __handle_reset_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """reset gate"""
        c.Reset(target, **(cond or {}))

    @staticmethod
    def __apply_gate(target: Qubit, gate_call: GateCall, c: Circuit, index: dict, cond: Optional[dict] = None):
        """apply a gate to a qubit, optionally wrapping it in a classical condition"""
        gate_dispatch = {
            "N": Backend.__handle_x_gate,
            "X": Backend.__handle_x_gate,
            "Y": Backend.__handle_y_gate,
            "Z": Backend.__handle_z_gate,
            "H": Backend.__handle_h_gate,
            "S": Backend.__handle_s_gate,
            "ST": Backend.__handle_sdg_gate,
            "TT": Backend.__handle_tdg_gate,
            "T": Backend.__handle_t_gate,
            "RX": Backend.__handle_rx_gate,
            "RY": Backend.__handle_ry_gate,
            "RZ": Backend.__handle_rz_gate,
            "CNOT": Backend.__handle_cx_gate,
            "FCNOT": Backend.__handle_fliped_cx_gate,
            "CX": Backend.__handle_cx_gate,
            "FCX": Backend.__handle_fliped_cx_gate,
            "CY": Backend.__handle_cy_gate,
            "FCY": Backend.__handle_fliped_cy_gate,
            "CZ": Backend.__handle_cz_gate,
            "FCZ": Backend.__handle_fliped_cz_gate,
            "CH": Backend.__handle_ch_gate,
            "FCH": Backend.__handle_fliped_ch_gate,
            "CU1": Backend.__handle_cu1_gate,
            "SWAP": Backend.__handle_swap_gate,
            "TOFFOLI": Backend.__handle_ccx_gate,
            "CCX": Backend.__handle_ccx_gate,
            "M": Backend.__handle_measure_gate,
            "MEASURE": Backend.__handle_measure_gate,
            "RESET": Backend.__handle_reset_gate,
            "R": Backend.__handle_reset_gate,
        }
        fn = gate_dispatch.get(gate_call.name)
        if fn is None:
            raise ValueError(f"Unknown gate {gate_call.name!r}")
        number_args = list(
            map(
                lambda x: index[x] if isinstance(x, str) else x,
                gate_call.args,
            )
        )
        fn(c, target, number_args, cond=cond)

    @staticmethod
    def __ensure_qubit(c: Circuit, qb: Union[int, Qubit]):
        """Ensure the qubits is in the circuit."""
        q = Qubit(Backend.DEFAULT_QUBIT_REGISTER, qb) if isinstance(qb, int) else qb
        if q not in c.qubits:
            c.add_qubit(q)
            Backend.__ensure_bit(c, Bit(Backend.DEFAULT_BIT_REGISTER, q.index[0]))

    @staticmethod
    def __ensure_bit(c: Circuit, b: Union[int, Bit]):
        """Ensure the bit is in the circuit (no registers yet)."""
        bit = Bit("d", b) if isinstance(b, int) else b
        if bit not in c.bits:
            c.add_bit(bit)

    @staticmethod
    def __handle_pipeline(
        target: Qubit, pipeline: GatePipeline, c: Circuit, index: dict,
        cond: Optional[dict] = None,
    ):
        """apply a gate pipeline to a qubit, propagating any classical condition"""
        for part in pipeline.parts:
            if isinstance(part, GatePipeByName):
                Backend.__handle_pipeline(
                    target=target,
                    pipeline=GatePipeline(parts=index[part.name].parts[::-1])
                    if part.rev
                    else index[part.name],
                    c=c,
                    index=index,
                    cond=cond,
                )
            else:
                Backend.__apply_gate(target, part, c, index, cond=cond)

    @staticmethod
    def __handle_action(action: Action, c: Circuit, index: dict):
        """handle an action statement"""
        if isinstance(action.target, list):
            targets = action.target
        elif isinstance(action.target, str) and action.target == "*":
            targets = list(c.qubits)
        else:
            targets = [action.target]
        for target in targets:
            match target:
                case Qubit():
                    targeted_qubit = target
                case str():
                    targeted_qubit = index[target]
                case int():
                    targeted_qubit = Qubit(Backend.DEFAULT_QUBIT_REGISTER, target)
                case _:
                    raise TypeError(f"Unsupported target type: {type(target).__name__}")
            Backend.__ensure_qubit(c, targeted_qubit)
            for _ in range(action.count or 1):
                pipeline = (
                    index[action.instruction]
                    if isinstance(action.instruction, str)
                    else action.instruction
                )
                if not isinstance(pipeline, GatePipeline):
                    raise TypeError(
                        f"pipeline is not a GatePipeline (got {type(pipeline).__name__})"
                    )
                if not isinstance(targeted_qubit, Qubit):
                    raise TypeError(
                        f"target is not a qubit (got {type(target).__name__})"
                    )
                Backend.__handle_pipeline(targeted_qubit, pipeline, c, index)

    @staticmethod
    def __handle_conditional_action(action: ConditionalAction, c: Circuit, index: dict):
        """Handle a classically conditioned action.

        Each gate in the if_pipeline is emitted with condition_value=1 (fires
        when the bit is set).  Each gate in the optional else_pipeline is
        emitted with condition_value=0 (fires when the bit is clear).
        Both translate to TKET's Conditional optype.
        """
        condition_bit = index.get(action.condition_bit)
        if condition_bit is None:
            raise ValueError(
                f"Unknown classical bit '{action.condition_bit}' used as condition. "
                "Declare it first with '<name> : b <index>'."
            )
        if not isinstance(condition_bit, Bit):
            raise ValueError(
                f"'{action.condition_bit}' is not a classical Bit "
                f"(got {type(condition_bit).__name__}). "
                "Only declared bits can be used as conditions."
            )

        Backend.__ensure_bit(c, condition_bit)

        # Resolve targets — same logic as __handle_action
        if isinstance(action.target, list):
            targets = action.target
        elif isinstance(action.target, str) and action.target == "*":
            targets = list(c.qubits)
        else:
            targets = [action.target]

        for target in targets:
            match target:
                case Qubit():
                    targeted_qubit = target
                case str():
                    targeted_qubit = index[target]
                case int():
                    targeted_qubit = Qubit(Backend.DEFAULT_QUBIT_REGISTER, target)
                case _:
                    raise TypeError(f"Unsupported target type: {type(target).__name__}")

            Backend.__ensure_qubit(c, targeted_qubit)

            if not isinstance(targeted_qubit, Qubit):
                raise TypeError(
                    f"Conditional action target is not a Qubit "
                    f"(got {type(targeted_qubit).__name__})"
                )

            # if-branch: fires when condition_bit == 1
            if_cond = {"condition_bits": [condition_bit], "condition_value": 1}
            Backend.__handle_pipeline(targeted_qubit, action.if_pipeline, c, index, cond=if_cond)

            # else-branch: fires when condition_bit == 0
            if action.else_pipeline is not None:
                else_cond = {"condition_bits": [condition_bit], "condition_value": 0}
                Backend.__handle_pipeline(targeted_qubit, action.else_pipeline, c, index, cond=else_cond)

    @staticmethod
    def compile_to_circuit(ast_nodes):
        """generate a tket circuit from ast nodes"""
        c = Circuit()
        index = {}
        for node in ast_nodes:
            match node:
                case QubitDeclaration(name=name, qubit=qubit):
                    index[name] = qubit
                case BitDeclaration(name=name, bit=bit):
                    index[name] = bit
                case ListDeclaration(name=name, items=items):
                    index[name] = items
                case InstructionDeclaration(name=name, pipeline=pipeline):
                    index[name] = pipeline
                case Action():
                    Backend.__handle_action(node, c, index)
                case ConditionalAction():
                    Backend.__handle_conditional_action(node, c, index)
        return c

    @staticmethod
    def compile_to_openqasm(circuit: Circuit) -> str:
        """create a qasm code representation of a tket circuit"""
        return circuit_to_qasm_str(circuit)

    @staticmethod
    def compile_to_json(circuit: Circuit) -> str:
        """create a json representation of a tket circuit"""
        return json.dumps(circuit.to_dict(), indent=2, sort_keys=True)

    @staticmethod
    def compile_to_cirq_python(circuit: Circuit) -> str:
        """create a python with cirq code representation of a tket circuit"""
        try:
            from pytket.extensions.cirq import tk_to_cirq  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "Cirq output requires pytket-cirq. "
                "Install it with: pip install 'spinachlang[backends]'"
            ) from exc
        cirq_circ = tk_to_cirq(circuit)
        return f"import cirq\n\ncircuit = {repr(cirq_circ)}\nprint(circuit)"

    @staticmethod
    def compile_to_quil(circuit: Circuit) -> str:
        """create a quil code representation of a tket circuit"""
        try:
            from pytket.extensions.pyquil import tk_to_pyquil  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "Quil output requires pytket-pyquil. "
                "Install it with: pip install 'spinachlang[backends]'"
            ) from exc
        pyquil_prog = tk_to_pyquil(circuit)
        return pyquil_prog.out()

"""backend of spinach"""

import json
import os
import tempfile
from functools import reduce
from typing import Callable, Optional, Union
from pytket import Circuit, Qubit, Bit
from pytket.qasm import circuit_to_qasm_str

from .spinach_types import (
    GatePipeByName,
    GatePipeline,
    QubitDeclaration,
    BitDeclaration,
    InstructionDeclaration,
    ListDeclaration,
    Action,
    ConditionalAction,
)


def _per_target(fn: Callable) -> Callable:
    """Lift a single-target handler to the uniform multi-target dispatch interface.

    Every function stored in a dispatch table must have the same signature:

        fn(c: Circuit, targets: list, args: list, cond: Optional[dict]) -> None

    Individual gate handlers are simpler to write as single-target:

        fn(c: Circuit, target, args: list, cond: Optional[dict]) -> None

    _per_target wraps the latter to produce the former, driving the per-element
    loop here so that handlers never need to think about iteration.
    Group handlers (BARRIER, MEASURE) are NOT wrapped — they already accept a
    list and decide for themselves how to map targets to TKET calls.
    """
    def wrapped(c: Circuit, targets: list, args: list, cond: Optional[dict] = None) -> None:
        list(map(lambda target: fn(c, target, args, cond), targets))
    wrapped.__doc__ = fn.__doc__
    return wrapped


class Backend:
    """backend of spinach"""

    DEFAULT_QUBIT_REGISTER = "q"
    DEFAULT_BIT_REGISTER = "c"

    # ── Single-target qubit handlers ──────────────────────────────────────
    # Signature: fn(c, target: Qubit, args, cond)
    # Stored in the dispatch table via _per_target().

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
        controller = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        Backend.__ensure_qubit(c, controller)
        c.CX(controller, target, **(cond or {}))

    @staticmethod
    def __handle_fliped_cx_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """FCX gate"""
        controller = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        Backend.__ensure_qubit(c, controller)
        c.CX(target, controller, **(cond or {}))

    @staticmethod
    def __handle_cy_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """CY gate"""
        controller = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        Backend.__ensure_qubit(c, controller)
        c.CY(controller, target, **(cond or {}))

    @staticmethod
    def __handle_fliped_cy_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """FCY gate"""
        controller = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        Backend.__ensure_qubit(c, controller)
        c.CY(target, controller, **(cond or {}))

    @staticmethod
    def __handle_cz_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """CZ gate"""
        controller = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        Backend.__ensure_qubit(c, controller)
        c.CZ(controller, target, **(cond or {}))

    @staticmethod
    def __handle_fliped_cz_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """FCZ gate"""
        controller = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        Backend.__ensure_qubit(c, controller)
        c.CZ(target, controller, **(cond or {}))

    @staticmethod
    def __handle_ch_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """CH gate"""
        controller = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        Backend.__ensure_qubit(c, controller)
        c.CH(controller, target, **(cond or {}))

    @staticmethod
    def __handle_fliped_ch_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """FCH gate"""
        controller = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        Backend.__ensure_qubit(c, controller)
        c.CH(target, controller, **(cond or {}))

    @staticmethod
    def __handle_cu1_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """CU1 gate"""
        controller = args[1] if isinstance(args[1], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[1])
        Backend.__ensure_qubit(c, controller)
        c.CU1(args[0], controller, target, **(cond or {}))

    @staticmethod
    def __handle_swap_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """SWAP gate"""
        controller = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        Backend.__ensure_qubit(c, controller)
        c.SWAP(target, controller, **(cond or {}))

    @staticmethod
    def __handle_ccx_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """CCX gate"""
        c1 = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        c2 = args[1] if isinstance(args[1], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[1])
        Backend.__ensure_qubit(c, c1)
        Backend.__ensure_qubit(c, c2)
        c.CCX(c1, c2, target, **(cond or {}))

    @staticmethod
    def __handle_reset_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """Reset gate"""
        c.Reset(target, **(cond or {}))

    # ── New 1-qubit gates ─────────────────────────────────────────────────

    @staticmethod
    def __handle_sx_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """√X gate"""
        c.SX(target, **(cond or {}))

    @staticmethod
    def __handle_sxdg_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """√X† gate"""
        c.SXdg(target, **(cond or {}))

    @staticmethod
    def __handle_v_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """V gate (≡ √X in TKET convention)"""
        c.V(target, **(cond or {}))

    @staticmethod
    def __handle_vdg_gate(c: Circuit, target: Qubit, _: list, cond: Optional[dict] = None):
        """V† gate"""
        c.Vdg(target, **(cond or {}))

    @staticmethod
    def __handle_u1_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """IBM U1(λ) gate — diagonal single-qubit; 1 angle in half-turns."""
        if len(args) < 1:
            raise ValueError("U1 requires exactly 1 angle argument: U1(λ)")
        c.U1(args[0], target, **(cond or {}))

    @staticmethod
    def __handle_u2_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """IBM U2(φ, λ) gate — 2 angles in half-turns."""
        if len(args) < 2:
            raise ValueError("U2 requires exactly 2 angle arguments: U2(φ, λ)")
        c.U2(args[0], args[1], target, **(cond or {}))

    @staticmethod
    def __handle_u3_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """IBM U3(θ, φ, λ) gate — full SU(2); 3 angles in half-turns."""
        if len(args) < 3:
            raise ValueError("U3 requires exactly 3 angle arguments: U3(θ, φ, λ)")
        c.U3(args[0], args[1], args[2], target, **(cond or {}))

    @staticmethod
    def __handle_tk1_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """TKET TK1(α, β, γ) Euler decomposition; 3 angles in half-turns."""
        if len(args) < 3:
            raise ValueError("TK1 requires exactly 3 angle arguments: TK1(α, β, γ)")
        c.TK1(args[0], args[1], args[2], target, **(cond or {}))

    @staticmethod
    def __handle_phasedx_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """PhasedX(exponent, phase) — X rotation around a phase-shifted axis; 2 angles in half-turns."""
        if len(args) < 2:
            raise ValueError("PX / PHASEDX requires exactly 2 arguments: PX(exponent, phase)")
        c.PhasedX(args[0], args[1], target, **(cond or {}))

    # ── New 2-qubit gates ─────────────────────────────────────────────────

    @staticmethod
    def __handle_crx_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """Controlled-Rx gate: CRX(angle, ctrl) — 1 angle + control qubit."""
        if len(args) < 2:
            raise ValueError("CRX requires 2 arguments: CRX(angle, ctrl)")
        ctrl = args[1] if isinstance(args[1], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[1])
        Backend.__ensure_qubit(c, ctrl)
        c.CRx(args[0], ctrl, target, **(cond or {}))

    @staticmethod
    def __handle_cry_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """Controlled-Ry gate: CRY(angle, ctrl) — 1 angle + control qubit."""
        if len(args) < 2:
            raise ValueError("CRY requires 2 arguments: CRY(angle, ctrl)")
        ctrl = args[1] if isinstance(args[1], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[1])
        Backend.__ensure_qubit(c, ctrl)
        c.CRy(args[0], ctrl, target, **(cond or {}))

    @staticmethod
    def __handle_crz_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """Controlled-Rz gate: CRZ(angle, ctrl) — 1 angle + control qubit."""
        if len(args) < 2:
            raise ValueError("CRZ requires 2 arguments: CRZ(angle, ctrl)")
        ctrl = args[1] if isinstance(args[1], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[1])
        Backend.__ensure_qubit(c, ctrl)
        c.CRz(args[0], ctrl, target, **(cond or {}))

    @staticmethod
    def __handle_ecr_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """Echoed Cross-Resonance gate: ECR(ctrl)."""
        if len(args) < 1:
            raise ValueError("ECR requires 1 argument: ECR(ctrl)")
        ctrl = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        Backend.__ensure_qubit(c, ctrl)
        c.ECR(ctrl, target, **(cond or {}))

    @staticmethod
    def __handle_iswap_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """iSWAP gate: ISWAP(angle, other) — angle in half-turns."""
        if len(args) < 2:
            raise ValueError("ISWAP requires 2 arguments: ISWAP(angle, other)")
        other = args[1] if isinstance(args[1], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[1])
        Backend.__ensure_qubit(c, other)
        c.ISWAP(args[0], target, other, **(cond or {}))

    @staticmethod
    def __handle_iswapmax_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """Maximal iSWAP gate (≡ ISWAP(1)): ISWAPMAX(other)."""
        if len(args) < 1:
            raise ValueError("ISWAPMAX requires 1 argument: ISWAPMAX(other)")
        other = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        Backend.__ensure_qubit(c, other)
        c.ISWAPMax(target, other, **(cond or {}))

    @staticmethod
    def __handle_zzmax_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """ZZMax gate (≡ ZZPhase(½)): ZZMAX(other)."""
        if len(args) < 1:
            raise ValueError("ZZMAX requires 1 argument: ZZMAX(other)")
        other = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        Backend.__ensure_qubit(c, other)
        c.ZZMax(target, other, **(cond or {}))

    @staticmethod
    def __handle_zzphase_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """ZZPhase(angle, other) — e^{-i·angle·π/2 ZZ}; angle in half-turns."""
        if len(args) < 2:
            raise ValueError("ZZPH requires 2 arguments: ZZPH(angle, other)")
        other = args[1] if isinstance(args[1], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[1])
        Backend.__ensure_qubit(c, other)
        c.ZZPhase(args[0], target, other, **(cond or {}))

    @staticmethod
    def __handle_xxphase_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """XXPhase(angle, other) — e^{-i·angle·π/2 XX}; angle in half-turns."""
        if len(args) < 2:
            raise ValueError("XXPH requires 2 arguments: XXPH(angle, other)")
        other = args[1] if isinstance(args[1], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[1])
        Backend.__ensure_qubit(c, other)
        c.XXPhase(args[0], target, other, **(cond or {}))

    @staticmethod
    def __handle_yyphase_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """YYPhase(angle, other) — e^{-i·angle·π/2 YY}; angle in half-turns."""
        if len(args) < 2:
            raise ValueError("YYPH requires 2 arguments: YYPH(angle, other)")
        other = args[1] if isinstance(args[1], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[1])
        Backend.__ensure_qubit(c, other)
        c.YYPhase(args[0], target, other, **(cond or {}))

    @staticmethod
    def __handle_fsim_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """Fermionic Simulation gate: FSIM(θ, φ, other) — 2 angles + partner qubit."""
        if len(args) < 3:
            raise ValueError("FSIM requires 3 arguments: FSIM(θ, φ, other)")
        other = args[2] if isinstance(args[2], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[2])
        Backend.__ensure_qubit(c, other)
        c.FSim(args[0], args[1], target, other, **(cond or {}))

    @staticmethod
    def __handle_tk2_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """TKET TK2(a, b, c, other) — canonical 2-qubit interaction; 3 angles + partner qubit."""
        if len(args) < 4:
            raise ValueError("TK2 requires 4 arguments: TK2(a, b, c, other)")
        other = args[3] if isinstance(args[3], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[3])
        Backend.__ensure_qubit(c, other)
        c.TK2(args[0], args[1], args[2], target, other, **(cond or {}))

    @staticmethod
    def __handle_phiswap_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """PhasedISWAP gate: PHISWAP(p, t, other) — 2 angles + partner qubit."""
        if len(args) < 3:
            raise ValueError("PHISWAP requires 3 arguments: PHISWAP(p, t, other)")
        other = args[2] if isinstance(args[2], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[2])
        Backend.__ensure_qubit(c, other)
        c.PhasedISWAP(args[0], args[1], target, other, **(cond or {}))

    # ── New 3-qubit gates ─────────────────────────────────────────────────

    @staticmethod
    def __handle_cswap_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """CSWAP / Fredkin gate: CSWAP(ctrl, other) — swaps target↔other when ctrl=|1⟩."""
        if len(args) < 2:
            raise ValueError("CSWAP / FREDKIN requires 2 arguments: CSWAP(ctrl, other)")
        ctrl  = args[0] if isinstance(args[0], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[0])
        other = args[1] if isinstance(args[1], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[1])
        Backend.__ensure_qubit(c, ctrl)
        Backend.__ensure_qubit(c, other)
        c.CSWAP(ctrl, target, other, **(cond or {}))

    @staticmethod
    def __handle_xxphase3_gate(c: Circuit, target: Qubit, args: list, cond: Optional[dict] = None):
        """3-qubit XXPhase3(angle, q1, q2) — simultaneous XX interactions on all pairs."""
        if len(args) < 3:
            raise ValueError("XXP3 requires 3 arguments: XXP3(angle, q1, q2)")
        q1 = args[1] if isinstance(args[1], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[1])
        q2 = args[2] if isinstance(args[2], Qubit) else Qubit(Backend.DEFAULT_QUBIT_REGISTER, args[2])
        Backend.__ensure_qubit(c, q1)
        Backend.__ensure_qubit(c, q2)
        c.XXPhase3(args[0], target, q1, q2, **(cond or {}))

    # ── New group handlers ────────────────────────────────────────────────

    @staticmethod
    def __handle_phase_group(c: Circuit, _targets: list, args: list, cond: Optional[dict] = None):
        """PHASE(angle) — adds a global phase of angle × π to the whole circuit.

        The target qubit is accepted for syntactic consistency but is ignored:
        global phase is a scalar property of the circuit, not tied to any qubit.
        Raises if used inside a classical conditional branch (not meaningful there).
        """
        if not args:
            raise ValueError("PHASE requires one angle argument in half-turns: PHASE(angle)")
        if cond:
            raise ValueError(
                "PHASE (global phase) cannot be used inside a conditional branch — "
                "global phase has no physical observable effect when conditioned."
            )
        c.add_phase(args[0])

    @staticmethod
    def __handle_circbox_group(c: Circuit, targets: list, args: list, cond: Optional[dict] = None):
        """CIRCBOX(instruction) — compiles a named instruction pipeline into a CircBox sub-circuit.

        Usage:  [q0, q1] -> CIRCBOX(bell_prep)

        The named instruction is compiled into a fresh n-qubit sub-circuit
        (where n = number of qubit targets) with abstract qubits q[0]..q[n-1].
        Integer qubit references inside the pipeline (e.g. CX(1)) map directly
        to the corresponding abstract qubit in the box.  The targets supplied
        here define how those abstract qubits map back to the parent circuit.

        Limitations:
          - Named qubit references from the parent scope inside the pipeline
            are not remapped; they must not exceed the sub-circuit qubit count.
          - Conditional CIRCBOX is not supported.
        """
        from pytket.circuit import CircBox  # pylint: disable=import-outside-toplevel
        if not args:
            raise ValueError(
                "CIRCBOX requires one argument: the name of a declared instruction pipeline. "
                "Example:  [q0, q1] -> CIRCBOX(bell_prep)"
            )
        pipeline = args[0]
        if not isinstance(pipeline, GatePipeline):
            raise ValueError(
                f"CIRCBOX argument must resolve to a named instruction pipeline, "
                f"got {type(pipeline).__name__}. "
                "Declare it first as 'name : gate | pipeline'."
            )
        if cond:
            raise ValueError("CIRCBOX cannot be used inside a conditional branch.")

        qubit_targets = [t for t in targets if isinstance(t, Qubit)]
        n_qubits = len(qubit_targets)
        if n_qubits < 1:
            raise ValueError("CIRCBOX requires at least one qubit target.")

        # Build a fresh sub-circuit with abstract qubits q[0]..q[n_qubits-1].
        sub = Circuit(n_qubits)
        sub_index: dict = {i: Qubit(Backend.DEFAULT_QUBIT_REGISTER, i) for i in range(n_qubits)}

        # Compile the pipeline into the sub-circuit targeting sub qubit 0.
        # Integer args such as CX(1) reference sub qubit 1, which maps to
        # targets[1] in the parent circuit via add_circbox ordering.
        first_sub_qubit = Qubit(Backend.DEFAULT_QUBIT_REGISTER, 0)
        Backend.__execute_pipeline_for_targets([first_sub_qubit], pipeline, sub, sub_index)

        box = CircBox(sub)
        list(map(lambda q: Backend.__ensure_qubit(c, q), qubit_targets))
        c.add_circbox(box, qubit_targets)

    # ── Group qubit handlers ───────────────────────────────────────────────
    # Signature: fn(c, targets: list[Qubit], args, cond)
    # Stored directly in the dispatch table (no _per_target wrapping needed).

    @staticmethod
    def __handle_barrier_group(c: Circuit, targets: list, _args: list, cond: Optional[dict] = None):
        """BARRIER — one joint barrier across all qubit targets.

        A single c.add_barrier([q0, q1, ...]) is a cross-qubit synchronisation
        point; N separate single-qubit calls would not carry the same guarantee.
        """
        if cond:
            raise ValueError("BARRIER cannot be used inside a conditional (if/else) branch.")
        qubit_list = [t for t in targets if isinstance(t, Qubit)]
        if qubit_list:
            c.add_barrier(qubit_list)

    @staticmethod
    def __handle_measure_group(c: Circuit, targets: list, args: list, cond: Optional[dict] = None):
        """MEASURE applied to a group of qubits.

        Uses c.measure_all() when every circuit qubit is targeted with no
        explicit destination bit and no condition (the `* -> M` case).
        Falls back to individual Measure gates otherwise.
        """
        qubit_targets = [t for t in targets if isinstance(t, Qubit)]
        if not qubit_targets:
            return
        if not args and not cond and set(qubit_targets) == set(c.qubits):
            c.measure_all()
            return

        def _measure_qubit(qubit: Qubit) -> None:
            bit = args[0] if (args and isinstance(args[0], Bit)) else Bit(Backend.DEFAULT_BIT_REGISTER, qubit.index[0])
            Backend.__ensure_bit(c, bit)
            c.Measure(qubit, bit, **(cond or {}))

        list(map(_measure_qubit, qubit_targets))

    @staticmethod
    def __handle_not_bit(c: Circuit, target: Bit, args: list, _cond: Optional[dict] = None):
        """Classical NOT: target = NOT source  (source defaults to target for in-place)"""
        if len(args) > 1:
            raise ValueError("NOT takes 0 or 1 argument: NOT  or  NOT(src_bit)")
        src = args[0] if args else target
        if not isinstance(src, Bit):
            raise ValueError(f"NOT source must be a classical Bit, got {type(src).__name__}")
        Backend.__ensure_bit(c, src)
        Backend.__ensure_bit(c, target)
        c.add_c_not(src, target)

    @staticmethod
    def __handle_set_bit(c: Circuit, target: Bit, args: list, _cond: Optional[dict] = None):
        """Classical SET: target = 0 or 1"""
        if len(args) != 1 or not isinstance(args[0], int):
            raise ValueError("SET requires exactly one integer literal: SET(0) or SET(1)")
        if args[0] not in (0, 1):
            raise ValueError(f"SET argument must be 0 or 1, got {args[0]}")
        Backend.__ensure_bit(c, target)
        c.add_c_setbits([bool(args[0])], [target])

    @staticmethod
    def __handle_and_bit(c: Circuit, target: Bit, args: list, _cond: Optional[dict] = None):
        """Classical AND: target = args[0] AND args[1]"""
        if len(args) != 2 or not all(isinstance(a, Bit) for a in args):
            raise ValueError("AND requires exactly 2 bit arguments: AND(b0, b1)")
        b0, b1 = args
        list(map(lambda b: Backend.__ensure_bit(c, b), [b0, b1, target]))
        c.add_c_and(b0, b1, target)

    @staticmethod
    def __handle_or_bit(c: Circuit, target: Bit, args: list, _cond: Optional[dict] = None):
        """Classical OR: target = args[0] OR args[1]"""
        if len(args) != 2 or not all(isinstance(a, Bit) for a in args):
            raise ValueError("OR requires exactly 2 bit arguments: OR(b0, b1)")
        b0, b1 = args
        list(map(lambda b: Backend.__ensure_bit(c, b), [b0, b1, target]))
        c.add_c_or(b0, b1, target)

    @staticmethod
    def __handle_xor_bit(c: Circuit, target: Bit, args: list, _cond: Optional[dict] = None):
        """Classical XOR: target = args[0] XOR args[1]"""
        if len(args) != 2 or not all(isinstance(a, Bit) for a in args):
            raise ValueError("XOR requires exactly 2 bit arguments: XOR(b0, b1)")
        b0, b1 = args
        list(map(lambda b: Backend.__ensure_bit(c, b), [b0, b1, target]))
        c.add_c_xor(b0, b1, target)

    @staticmethod
    def __handle_copy_bit(c: Circuit, target: Bit, args: list, _cond: Optional[dict] = None):
        """Classical COPY: target = args[0]"""
        if len(args) != 1 or not isinstance(args[0], Bit):
            raise ValueError("COPY requires exactly 1 bit argument: COPY(src_bit)")
        src = args[0]
        Backend.__ensure_bit(c, src)
        Backend.__ensure_bit(c, target)
        c.add_c_copybits([src], [target])

    __qubit_dispatch: dict = {
        # ── Single-qubit ──────────────────────────────────────────────
        "N":        _per_target(__handle_x_gate),
        "X":        _per_target(__handle_x_gate),
        "Y":        _per_target(__handle_y_gate),
        "Z":        _per_target(__handle_z_gate),
        "H":        _per_target(__handle_h_gate),
        "S":        _per_target(__handle_s_gate),
        "ST":       _per_target(__handle_sdg_gate),
        "TT":       _per_target(__handle_tdg_gate),
        "T":        _per_target(__handle_t_gate),
        "RX":       _per_target(__handle_rx_gate),
        "RY":       _per_target(__handle_ry_gate),
        "RZ":       _per_target(__handle_rz_gate),
        # √X family
        "SX":       _per_target(__handle_sx_gate),
        "SXDG":     _per_target(__handle_sxdg_gate),
        "V":        _per_target(__handle_v_gate),
        "VDG":      _per_target(__handle_vdg_gate),
        # IBM universal gates
        "U1":       _per_target(__handle_u1_gate),
        "U2":       _per_target(__handle_u2_gate),
        "U3":       _per_target(__handle_u3_gate),
        # TKET native
        "TK1":      _per_target(__handle_tk1_gate),
        # Phased gates
        "PX":       _per_target(__handle_phasedx_gate),
        "PHASEDX":  _per_target(__handle_phasedx_gate),
        # ── Two-qubit ─────────────────────────────────────────────────
        "CX":       _per_target(__handle_cx_gate),
        "CNOT":     _per_target(__handle_cx_gate),
        "FCX":      _per_target(__handle_fliped_cx_gate),
        "FCNOT":    _per_target(__handle_fliped_cx_gate),
        "CY":       _per_target(__handle_cy_gate),
        "FCY":      _per_target(__handle_fliped_cy_gate),
        "CZ":       _per_target(__handle_cz_gate),
        "FCZ":      _per_target(__handle_fliped_cz_gate),
        "CH":       _per_target(__handle_ch_gate),
        "FCH":      _per_target(__handle_fliped_ch_gate),
        "CU1":      _per_target(__handle_cu1_gate),
        "SWAP":     _per_target(__handle_swap_gate),
        # Controlled-rotation family
        "CRX":      _per_target(__handle_crx_gate),
        "CRY":      _per_target(__handle_cry_gate),
        "CRZ":      _per_target(__handle_crz_gate),
        # Cross-resonance
        "ECR":      _per_target(__handle_ecr_gate),
        # iSWAP family
        "ISWAP":    _per_target(__handle_iswap_gate),
        "ISWAPMAX": _per_target(__handle_iswapmax_gate),
        # ZZ / XX / YY interaction family
        "ZZMAX":    _per_target(__handle_zzmax_gate),
        "ZZPH":     _per_target(__handle_zzphase_gate),
        "XXPH":     _per_target(__handle_xxphase_gate),
        "YYPH":     _per_target(__handle_yyphase_gate),
        # Parametric 2-qubit
        "FSIM":     _per_target(__handle_fsim_gate),
        "TK2":      _per_target(__handle_tk2_gate),
        "PHISWAP":  _per_target(__handle_phiswap_gate),
        # ── Three-qubit ───────────────────────────────────────────────
        "CCX":      _per_target(__handle_ccx_gate),
        "TOFFOLI":  _per_target(__handle_ccx_gate),
        "CSWAP":    _per_target(__handle_cswap_gate),
        "FREDKIN":  _per_target(__handle_cswap_gate),
        "XXP3":     _per_target(__handle_xxphase3_gate),
        # ── Lifecycle ─────────────────────────────────────────────────
        "R":        _per_target(__handle_reset_gate),
        "RESET":    _per_target(__handle_reset_gate),
        # ── Group (already list-based, no _per_target wrapping) ───────
        "M":        __handle_measure_group,
        "MEASURE":  __handle_measure_group,
        "BARRIER":  __handle_barrier_group,
        "PHASE":    __handle_phase_group,
        "CIRCBOX":  __handle_circbox_group,
    }

    __bit_dispatch: dict = {
        "NOT":  _per_target(__handle_not_bit),
        "SET":  _per_target(__handle_set_bit),
        "AND":  _per_target(__handle_and_bit),
        "OR":   _per_target(__handle_or_bit),
        "XOR":  _per_target(__handle_xor_bit),
        "COPY": _per_target(__handle_copy_bit),
    }

    # ── Circuit utilities ──────────────────────────────────────────────────

    @staticmethod
    def __ensure_qubit(c: Circuit, qb: Union[int, Qubit]):
        """Ensure the qubit is in the circuit."""
        q = Qubit(Backend.DEFAULT_QUBIT_REGISTER, qb) if isinstance(qb, int) else qb
        if q not in c.qubits:
            c.add_qubit(q)
            Backend.__ensure_bit(c, Bit(Backend.DEFAULT_BIT_REGISTER, q.index[0]))

    @staticmethod
    def __ensure_bit(c: Circuit, b: Union[int, Bit]):
        """Ensure the bit is in the circuit."""
        bit = Bit(Backend.DEFAULT_BIT_REGISTER, b) if isinstance(b, int) else b
        if bit not in c.bits:
            c.add_bit(bit)

    # ── Pipeline execution engine ──────────────────────────────────────────

    @staticmethod
    def __execute_pipeline_for_targets(
        targets: list,
        pipeline: GatePipeline,
        c: Circuit,
        index: dict,
        cond: Optional[dict] = None,
    ):
        """Execute a gate pipeline against a resolved list of targets.

        For each gate the engine:
          1. Looks up the gate name in the qubit dispatch (if there are qubit targets).
          2. Looks up the gate name in the bit dispatch   (if there are bit targets).
          3. Pre-checks both lookups — raises before touching the circuit if either
             target type has no handler for the requested gate.
          4. Calls each handler: fn(c, targets, args, cond).

        Every entry in both dispatch tables has that same interface, so this
        function never inspects how the handler works — it just selects and calls.
        """
        def _process_part(part) -> None:
            if isinstance(part, GatePipeByName):
                sub = GatePipeline(
                    parts=index[part.name].parts[::-1] if part.rev else index[part.name].parts
                )
                Backend.__execute_pipeline_for_targets(targets, sub, c, index, cond)
                return

            qubit_targets = [t for t in targets if isinstance(t, Qubit)]
            bit_targets   = [t for t in targets if isinstance(t, Bit)]

            # Resolve args once: str names → index values (Qubit/Bit/number)
            number_args = [index[x] if isinstance(x, str) else x for x in part.args]

            # ── pre-flight lookup (raises before any circuit mutation) ─
            qubit_fn = Backend.__qubit_dispatch.get(part.name) if qubit_targets else None
            bit_fn   = Backend.__bit_dispatch.get(part.name)   if bit_targets   else None

            if qubit_targets and qubit_fn is None:
                raise ValueError(f"Unknown qubit gate {part.name!r}")
            if bit_targets and bit_fn is None:
                raise ValueError(
                    f"Unknown classical bit operation {part.name!r}. "
                    "Valid: NOT, SET(0/1), AND(b0,b1), OR(b0,b1), XOR(b0,b1), COPY(src)"
                )

            # ── execute ───────────────────────────────────────────────
            if qubit_fn:
                list(map(lambda q: Backend.__ensure_qubit(c, q), qubit_targets))
                qubit_fn(c, qubit_targets, number_args, cond)

            if bit_fn:
                bit_fn(c, bit_targets, number_args, cond)

        list(map(_process_part, pipeline.parts))

    @staticmethod
    def __handle_pipeline(
        target: Qubit,
        pipeline: GatePipeline,
        c: Circuit,
        index: dict,
        cond: Optional[dict] = None,
    ):
        """Single-target wrapper used by the conditional-action path."""
        Backend.__execute_pipeline_for_targets([target], pipeline, c, index, cond)

    # ── Action handlers ────────────────────────────────────────────────────

    @staticmethod
    def __resolve_targets(raw_target, c: Circuit, index: dict) -> list:
        """Resolve an action target to a flat list of Qubit / Bit objects."""
        raws = (
            raw_target if isinstance(raw_target, list)
            else list(c.qubits) if (isinstance(raw_target, str) and raw_target == "*")
            else [raw_target]
        )

        def _resolve_raw(raw) -> Union[Qubit, Bit]:
            match raw:
                case Qubit(): return raw
                case Bit():   return raw
                case str():   return index[raw]
                case int():   return Qubit(Backend.DEFAULT_QUBIT_REGISTER, raw)
                case _: raise TypeError(f"Unsupported target type: {type(raw).__name__}")

        return list(map(_resolve_raw, raws))

    @staticmethod
    def __handle_action(action: Action, c: Circuit, index: dict):
        """Handle an unconditional action — resolve targets, resolve pipeline, execute."""
        targets = Backend.__resolve_targets(action.target, c, index)
        pipeline = index[action.instruction] if isinstance(action.instruction, str) else action.instruction
        if not isinstance(pipeline, GatePipeline):
            raise TypeError(f"pipeline is not a GatePipeline (got {type(pipeline).__name__})")
        list(map(
            lambda _: Backend.__execute_pipeline_for_targets(targets, pipeline, c, index),
            range(action.count or 1),
        ))

    @staticmethod
    def __handle_conditional_action(action: ConditionalAction, c: Circuit, index: dict):
        """Handle a classically conditioned action (if / if-else)."""
        condition_bit = index.get(action.condition_bit)
        if condition_bit is None:
            raise ValueError(
                f"Unknown classical bit '{action.condition_bit}' used as condition. "
                "Declare it first with '<name> : b <index>'."
            )
        if not isinstance(condition_bit, Bit):
            raise ValueError(
                f"'{action.condition_bit}' is not a classical Bit "
                f"(got {type(condition_bit).__name__})."
            )
        Backend.__ensure_bit(c, condition_bit)
        targets = Backend.__resolve_targets(action.target, c, index)

        def _handle_target(target: Qubit) -> None:
            if not isinstance(target, Qubit):
                raise TypeError(f"Conditional action target is not a Qubit (got {type(target).__name__})")
            Backend.__ensure_qubit(c, target)
            Backend.__handle_pipeline(target, action.if_pipeline, c, index,
                                       cond={"condition_bits": [condition_bit], "condition_value": 1})
            if action.else_pipeline is not None:
                Backend.__handle_pipeline(target, action.else_pipeline, c, index,
                                           cond={"condition_bits": [condition_bit], "condition_value": 0})

        list(map(_handle_target, targets))

    # ── Public API ─────────────────────────────────────────────────────────

    @staticmethod
    def compile_to_circuit(ast_nodes):
        """generate a tket circuit from ast nodes"""
        def _process_node(acc: tuple, node) -> tuple:
            c, index = acc
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
            return c, index

        c, _ = reduce(_process_node, ast_nodes, (Circuit(), {}))
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

    @staticmethod
    def compile_to_latex(circuit: Circuit) -> str:
        """Create a LaTeX/TikZ circuit diagram (quantikz package) from a tket circuit.

        Uses pytket's built-in to_latex_file() via a temporary file and returns
        the full .tex document as a string. No extra package required beyond pytket core.
        """
        tmp_fd, tmp_path = tempfile.mkstemp(suffix=".tex")
        os.close(tmp_fd)
        try:
            circuit.to_latex_file(tmp_path)
            with open(tmp_path, encoding="utf-8") as f:
                return f.read()
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    @staticmethod
    def compile_to_qir(circuit: Circuit) -> str:
        """Create a QIR (Quantum Intermediate Representation) LLVM IR text from a tket circuit.

        QIR is the Microsoft-led standard for representing quantum programs as LLVM IR.
        Requires the pytket-qir optional package.
        """
        try:
            from pytket.qir import pytket_to_qir, QIRFormat  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "QIR output requires pytket-qir. "
                "Install it with: pip install 'spinachlang[backends]'"
            ) from exc
        result = pytket_to_qir(circuit, name="spinach_circuit", qir_format=QIRFormat.STRING)
        if result is None:
            raise ValueError(
                "pytket_to_qir returned None — the circuit may contain operations "
                "not yet supported by the QIR profile. Try adding measurements."
            )
        return result

    @staticmethod
    def compile_to_braket(circuit: Circuit) -> str:
        """Create an Amazon Braket OpenQASM 3.0 representation of a tket circuit.

        Returns the OpenQASM 3.0 source string as used by AWS Braket devices.
        Requires the pytket-braket optional package.
        """
        try:
            from pytket.extensions.braket import tk_to_braket  # pylint: disable=import-outside-toplevel
            from braket.circuits.serialization import IRType    # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "Braket output requires pytket-braket. "
                "Install it with: pip install 'spinachlang[backends]'"
            ) from exc
        braket_circuit = tk_to_braket(circuit)[0]
        return braket_circuit.to_ir(IRType.OPENQASM).source

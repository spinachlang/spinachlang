"""backend of spinach"""

import json
from typing import Union
from pytket import Circuit, Qubit, Bit
from pytket.qasm import circuit_to_qasm_str
from pytket.extensions.cirq import tk_to_cirq
from pytket.extensions.pyquil import tk_to_pyquil

from app.spinach_types import (
    GateCall,
    GatePipeByName,
    GatePipeline,
    QubitDeclaration,
    BitDeclaration,
    InstructionDeclaration,
    ListDeclaration,
    Action,
)


class SpinachBack:
    """backend of spinach"""

    DEFAULT_QUBIT_REGISTER = "q"
    DEFAULT_BIT_REGISTER = "c"

    @staticmethod
    def __handle_x_gate(c: Circuit, target: Qubit, _: list):
        """X gate"""
        c.X(target)

    @staticmethod
    def __handle_y_gate(c: Circuit, target: Qubit, _: list):
        """Y gate"""
        c.Y(target)

    @staticmethod
    def __handle_z_gate(c: Circuit, target: Qubit, _: list):
        """Z gate"""
        c.Z(target)

    @staticmethod
    def __handle_h_gate(c: Circuit, target: Qubit, _: list):
        """H gate"""
        c.H(target)

    @staticmethod
    def __handle_s_gate(c: Circuit, target: Qubit, _: list):
        """S gate"""
        c.S(target)

    @staticmethod
    def __handle_t_gate(c: Circuit, target: Qubit, _: list):
        c.T(target)

    @staticmethod
    def __handle_sdg_gate(c: Circuit, target: Qubit, _: list):
        """S dager gate"""
        c.Sdg(target)

    @staticmethod
    def __handle_tdg_gate(c: Circuit, target: Qubit, _: list):
        """T dager gate"""
        c.Tdg(target)

    @staticmethod
    def __handle_rx_gate(c: Circuit, target: Qubit, args: list):
        """RX gate"""
        c.Rx(args[0], target)

    @staticmethod
    def __handle_ry_gate(c: Circuit, target: Qubit, args: list):
        """RY gate"""
        c.Ry(args[0], target)

    @staticmethod
    def __handle_rz_gate(c: Circuit, target: Qubit, args: list):
        """RZ gate"""
        c.Rz(args[0], target)

    @staticmethod
    def __handle_cx_gate(c: Circuit, target: Qubit, args: list):
        """CX gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(SpinachBack.DEFAULT_QUBIT_REGISTER, args[0])
        )
        SpinachBack.__ensure_qubit(c, controller)
        c.CX(controller, target)

    @staticmethod
    def __handle_fliped_cx_gate(c: Circuit, target: Qubit, args: list):
        """FCX gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(SpinachBack.DEFAULT_QUBIT_REGISTER, args[0])
        )
        SpinachBack.__ensure_qubit(c, controller)
        c.CX(target, controller)

    @staticmethod
    def __handle_cy_gate(c: Circuit, target: Qubit, args: list):
        """CY gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(SpinachBack.DEFAULT_BIT_REGISTER, args[0])
        )
        SpinachBack.__ensure_qubit(c, controller)
        c.CY(controller, target)

    @staticmethod
    def __handle_fliped_cy_gate(c: Circuit, target: Qubit, args: list):
        """FCY gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(SpinachBack.DEFAULT_QUBIT_REGISTER, args[0])
        )
        SpinachBack.__ensure_qubit(c, controller)
        c.CY(target, controller)

    @staticmethod
    def __handle_cz_gate(c: Circuit, target: Qubit, args: list):
        """CZ gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(SpinachBack.DEFAULT_QUBIT_REGISTER, args[0])
        )
        SpinachBack.__ensure_qubit(c, controller)
        c.CZ(controller, target)

    @staticmethod
    def __handle_fliped_cz_gate(c: Circuit, target: Qubit, args: list):
        """FCZ gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(SpinachBack.DEFAULT_QUBIT_REGISTER, args[0])
        )
        SpinachBack.__ensure_qubit(c, controller)
        c.CZ(target, controller)

    @staticmethod
    def __handle_ch_gate(c: Circuit, target: Qubit, args: list):
        """CH gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(SpinachBack.DEFAULT_QUBIT_REGISTER, args[0])
        )
        SpinachBack.__ensure_qubit(c, controller)
        c.CH(controller, target)

    @staticmethod
    def __handle_fliped_ch_gate(c: Circuit, target: Qubit, args: list):
        """FCH gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(SpinachBack.DEFAULT_QUBIT_REGISTER, args[0])
        )
        SpinachBack.__ensure_qubit(c, controller)
        c.CH(target, controller)

    @staticmethod
    def __handle_cu1_gate(c: Circuit, target: Qubit, args: list):
        """CU1 gate"""
        controller = (
            args[1]
            if isinstance(args[1], Qubit)
            else Qubit(SpinachBack.DEFAULT_QUBIT_REGISTER, args[1])
        )
        SpinachBack.__ensure_qubit(c, controller)
        c.CU1(args[0], controller, target)

    @staticmethod
    def __handle_swap_gate(c: Circuit, target: Qubit, args: list):
        """swap gate"""
        controller = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(SpinachBack.DEFAULT_QUBIT_REGISTER, args[0])
        )
        SpinachBack.__ensure_qubit(c, controller)
        c.SWAP(target, controller)

    @staticmethod
    def __handle_ccx_gate(c: Circuit, target: Qubit, args: list):
        """CCX gate"""
        controller1 = (
            args[0]
            if isinstance(args[0], Qubit)
            else Qubit(SpinachBack.DEFAULT_QUBIT_REGISTER, args[0])
        )
        controller2 = (
            args[1]
            if isinstance(args[1], Qubit)
            else Qubit(SpinachBack.DEFAULT_QUBIT_REGISTER, args[1])
        )
        SpinachBack.__ensure_qubit(c, controller1)
        SpinachBack.__ensure_qubit(c, controller2)
        c.CCX(controller1, controller2, target)

    @staticmethod
    def __handle_measure_gate(c: Circuit, target: Qubit, args: list):
        """measure gate"""
        if len(args) < 1:
            bit = Bit(SpinachBack.DEFAULT_BIT_REGISTER, target.index[0])
        else:
            bit = (
                args[0]
                if isinstance(args[0], Bit)
                else Bit(SpinachBack.DEFAULT_BIT_REGISTER, args[0])
            )
        SpinachBack.__ensure_bit(c, bit)
        c.Measure(target, bit)

    @staticmethod
    def __handle_reset_gate(c: Circuit, target: Qubit, _: list):
        """reset gate"""
        c.Reset(target)

    @staticmethod
    def __apply_gate(target: Qubit, gate_call: GateCall, c: Circuit, index: dict):
        """apply a gate to a qubit"""
        gate_dispatch = {
            "N": SpinachBack.__handle_x_gate,
            "X": SpinachBack.__handle_x_gate,
            "Y": SpinachBack.__handle_y_gate,
            "Z": SpinachBack.__handle_z_gate,
            "H": SpinachBack.__handle_h_gate,
            "S": SpinachBack.__handle_s_gate,
            "ST": SpinachBack.__handle_sdg_gate,
            "TT": SpinachBack.__handle_tdg_gate,
            "T": SpinachBack.__handle_t_gate,
            "RX": SpinachBack.__handle_rx_gate,
            "RY": SpinachBack.__handle_ry_gate,
            "RZ": SpinachBack.__handle_rz_gate,
            "CNOT": SpinachBack.__handle_cx_gate,
            "FCNOT": SpinachBack.__handle_fliped_cx_gate,
            "CX": SpinachBack.__handle_cx_gate,
            "FCX": SpinachBack.__handle_fliped_cx_gate,
            "CY": SpinachBack.__handle_cy_gate,
            "FCY": SpinachBack.__handle_fliped_cy_gate,
            "CZ": SpinachBack.__handle_cz_gate,
            "FCZ": SpinachBack.__handle_fliped_cz_gate,
            "CH": SpinachBack.__handle_ch_gate,
            "FCH": SpinachBack.__handle_fliped_ch_gate,
            "CU1": SpinachBack.__handle_cu1_gate,
            "SWAP": SpinachBack.__handle_swap_gate,
            "TOFFOLI": SpinachBack.__handle_ccx_gate,
            "CCX": SpinachBack.__handle_ccx_gate,
            "M": SpinachBack.__handle_measure_gate,
            "MEASURE": SpinachBack.__handle_measure_gate,
            "RESET": SpinachBack.__handle_reset_gate,
            "R": SpinachBack.__handle_reset_gate,
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
        fn(c, target, number_args)

    @staticmethod
    def __ensure_qubit(c: Circuit, qb: Union[int, Qubit]):
        """Ensure the qubits is in the circuit."""
        q = Qubit(SpinachBack.DEFAULT_QUBIT_REGISTER, qb) if isinstance(qb, int) else qb
        if q not in c.qubits:
            c.add_qubit(q)
            SpinachBack.__ensure_bit(
                c, Bit(SpinachBack.DEFAULT_BIT_REGISTER, q.index[0])
            )

    @staticmethod
    def __ensure_bit(c: Circuit, b: Union[int, Bit]):
        """Ensure the bit is in the circuit (no registers yet)."""
        bit = Bit("d", b) if isinstance(b, int) else b
        if bit not in c.bits:
            c.add_bit(bit)

    @staticmethod
    def __handle_pipeline(
        target: Qubit, pipeline: GatePipeline, c: Circuit, index: dict
    ):
        """apply a gate pipeline to a qubit"""
        for part in pipeline.parts:
            if isinstance(part, GatePipeByName):
                SpinachBack.__handle_pipeline(
                    target=target,
                    pipeline=GatePipeline(parts=index[part.name].parts[::-1])
                    if part.rev
                    else index[part.name],
                    c=c,
                    index=index,
                )
            else:
                SpinachBack.__apply_gate(target, part, c, index)

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
                    targeted_qubit = Qubit(SpinachBack.DEFAULT_QUBIT_REGISTER, target)
                case _:
                    raise TypeError(f"Unsupported target type: {type(target).__name__}")
            SpinachBack.__ensure_qubit(c, targeted_qubit)
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
                SpinachBack.__handle_pipeline(targeted_qubit, pipeline, c, index)

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
                    SpinachBack.__handle_action(node, c, index)
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
        cirq_circ = tk_to_cirq(circuit)
        return f"import cirq\n\ncircuit = {repr(cirq_circ)}\nprint(circuit)"

    @staticmethod
    def compile_to_quil(circuit: Circuit) -> str:
        """create a quil code representation of a tket circuit"""
        pyquil_prog = tk_to_pyquil(circuit)
        return pyquil_prog.out()

from app.spinach_types import (
    GateCall,
    GatePipeline,
    QubitDeclaration,
    InstructionDeclaration,
    ListDeclaration,
    Action,
)
import json
from pytket import Circuit
from pytket.qasm import circuit_to_qasm_str
from pytket.extensions.qiskit import tk_to_qiskit
from pytket.extensions.cirq import tk_to_cirq
from pytket.extensions.pyquil import tk_to_pyquil


class SpinachBack:
    @staticmethod
    def __get_max_qubit_number(ast_nodes):
        return max(
            (decl.number for decl in ast_nodes if isinstance(decl, QubitDeclaration)),
            default=0,
        )

    @staticmethod
    def __handle_x_gate(c: Circuit, target: int, _: list):
        c.X(target)

    @staticmethod
    def __handle_y_gate(c: Circuit, target: int, _: list):
        c.Y(target)

    @staticmethod
    def __handle_z_gate(c: Circuit, target: int, _: list):
        c.Z(target)

    @staticmethod
    def __handle_h_gate(c: Circuit, target: int, _: list):
        c.H(target)

    @staticmethod
    def __handle_s_gate(c: Circuit, target: int, _: list):
        c.S(target)

    @staticmethod
    def __handle_t_gate(c: Circuit, target: int, _: list):
        c.T(target)

    @staticmethod
    def __handle_sdg_gate(c: Circuit, target: int, _: list):
        c.Sdg(target)

    @staticmethod
    def __handle_tdg_gate(c: Circuit, target: int, _: list):
        c.Tdg(target)

    @staticmethod
    def __handle_rx_gate(c: Circuit, target: int, _: list):
        c.Rx(target)

    @staticmethod
    def __handle_ry_gate(c: Circuit, target: int, _: list):
        c.Ry(target)

    @staticmethod
    def __handle_rz_gate(c: Circuit, target: int, _: list):
        c.Rz(target)

    @staticmethod
    def __handle_cx_gate(c: Circuit, target: int, args: list):
        c.CX(args[0], target)

    @staticmethod
    def __handle_cy_gate(c: Circuit, target: int, args: list):
        c.CY(args[0], target)

    @staticmethod
    def __handle_cz_gate(c: Circuit, target: int, args: list):
        c.CZ(args[0], target)

    @staticmethod
    def __handle_ch_gate(c: Circuit, target: int, args: list):
        c.CH(args[0], target)

    @staticmethod
    def __handle_cu1_gate(c: Circuit, target: int, args: list):
        c.CU1(args[0], args[1], target)

    @staticmethod
    def __handle_swap_gate(c: Circuit, target: int, args: list):
        c.SWAP(target, args[0])

    @staticmethod
    def __handle_ccx_gate(c: Circuit, target: int, args: list):
        c.CCX(args[0], args[1], target)

    @staticmethod
    def __handle_measure_gate(c: Circuit, target: int, args: list):
        c.Measure(target, args[0])

    @staticmethod
    def __apply_gate(target: int, gate_call: GateCall, c: Circuit, index: dict):
        # Sdg and Tdg are not supported by pytket we will need in the futur to do something like: circ.add_gate(OpType.Sdg, [], [q])
        # Measuer all and barrier will be their own instructions since it affects all the qibits
        # There is a way to add gates with add_gate
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
            "CX": SpinachBack.__handle_cx_gate,
            "CY": SpinachBack.__handle_cy_gate,
            "CZ": SpinachBack.__handle_cz_gate,
            "CH": SpinachBack.__handle_ch_gate,
            "CU1": SpinachBack.__handle_cu1_gate,
            "SWAP": SpinachBack.__handle_swap_gate,
            "TOFFOLI": SpinachBack.__handle_ccx_gate,
            "CCX": SpinachBack.__handle_ccx_gate,
            "M": SpinachBack.__handle_measure_gate,
            "MEASURE": SpinachBack.__handle_measure_gate,
        }
        fn = gate_dispatch.get(gate_call.name)
        if fn is None:
            raise ValueError(f"Unknown gate {gate_call.name!r}")
        number_args = list(
            map(lambda x: index[x] if isinstance(x, str) else x, gate_call.args)
        )
        fn(c, target, number_args)

    @staticmethod
    def __handle_pipeline(target: int, pipeline: GatePipeline, c: Circuit, index: dict):
        for gate in pipeline.parts:
            gate_call = index[gate] if isinstance(gate, str) else gate
            if not isinstance(gate_call, GateCall):
                raise TypeError(
                    f"gate_call is not a GateCall (got {type(gate).__name__})"
                )
            SpinachBack.__apply_gate(target, gate_call, c, index)

    @staticmethod
    def __handle_action(action: Action, c: Circuit, index: dict):
        if isinstance(action.target, list):
            targets = action.target
        else:
            targets = [action.target]
        for target in targets:
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

                number_target = index[target] if isinstance(target, str) else target
                if isinstance(number_target, str):
                    raise TypeError(
                        f"target is not a number (got {type(target).__name__})"
                    )
                SpinachBack.__handle_pipeline(number_target, pipeline, c, index)

    @staticmethod
    def compile_to_circuit(ast_nodes):
        c = Circuit(SpinachBack.__get_max_qubit_number(ast_nodes) + 1, 10)
        index = dict()
        for node in ast_nodes:
            match node:
                case QubitDeclaration(name=name, number=number):
                    index[name] = number
                case ListDeclaration(name=name, items=items):
                    index[name] = items
                case InstructionDeclaration(name=name, pipeline=pipeline):
                    index[name] = pipeline
                case Action():
                    SpinachBack.__handle_action(node, c, index)
        return c

    @staticmethod
    def compile_to_openqasm(circuit: Circuit) -> str:
        return circuit_to_qasm_str(circuit)

    @staticmethod
    def compile_to_json(circuit: Circuit) -> str:
        return json.dumps(circuit.to_dict(), indent=4, sort_keys=True)

    @staticmethod
    def compile_to_cirq_python(circuit: Circuit) -> str:
        cirq_circ = tk_to_cirq(circuit)
        return f"import cirq\n\ncircuit = {repr(cirq_circ)}\nprint(circuit)"

    @staticmethod
    def compile_to_quil(circuit: Circuit) -> str:
        pyquil_prog = tk_to_pyquil(circuit)
        return pyquil_prog.out()

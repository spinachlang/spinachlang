from app.spinach_types import (
    GateCall,
    GatePipeline,
    QubitDeclaration,
    InstructionDeclaration,
    ListDeclaration,
    Action,
)
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
    def __apply_gate(target: int, gate_call: GateCall, c: Circuit):
        # Sdg and Tdg are not supported by pytket we will need in the futur to do something like: circ.add_gate(OpType.Sdg, [], [q])
        # Measuer all and barrier will be their own instructions since it affects all the qibits
        # There is a way to add gates with add_gate
        gate_dispatch = {
            "X": c.X,
            "Y": c.Y,
            "Z": c.Z,
            "H": c.H,
            "S": c.S,
            "T": c.T,
            "RX": c.Rx,
            "RY": c.Ry,
            "RZ": c.Rz,
            "CNOT": c.CX,
            "CX": c.CX,
            "CY": c.CY,
            "CZ": c.CZ,
            "CU1": c.CU1,
            "SWAP": c.SWAP,
            "TOFFOLI": c.CCX,
            "CCX": c.CCX,
            "M": c.MEASURE,
            "MEASURE": c.MEASURE,
        }
        fn = gate_dispatch.get(gate_call.name)
        if fn is None:
            raise ValueError(f"Unknown gate {gate_call.name!r}")

        try:
            if gate_call.name in ["M", "MEASURE"]:
                fn(target, *(gate_call.args if gate_call.args is not None else ()))

            else:
                fn(*((gate_call.args if gate_call.args is not None else ()), target))

        except TypeError as e:
            raise TypeError(
                f"Error calling gate {gate_call.name!r} with args {gate_call.args}: {e}"
            ) from e

    @staticmethod
    def __handle_pipeline(target: int, pipeline: GatePipeline, c: Circuit, index: dict):
        for gate in pipeline.parts:
            gate_call = index[gate] if isinstance(gate, str) else gate
            if not isinstance(gate_call, GateCall):
                raise TypeError(
                    f"gate_call is not a GateCall (got {type(gate).__name__})"
                )
            SpinachBack.__apply_gate(target, gate_call, c)

    @staticmethod
    def __handle_action(action: Action, c: Circuit, index: dict):
        if isinstance(action.target, list):
            targets = action.target
        else:
            targets = [action.target]
        for target in targets:
            for _ in range(action.count or 0):
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
                if not isinstance(target, int):
                    raise TypeError(
                        f"target is not a number (got {type(target).__name__})"
                    )
                SpinachBack.__handle_pipeline(number_target, pipeline, c, index)

    @staticmethod
    def compile_to_circuit(ast_nodes):
        c = Circuit(SpinachBack.__get_max_qubit_number(ast_nodes))
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
    def compile_to_openqasm(circuit: Circuit):
        return circuit_to_qasm_str(circuit)

    @staticmethod
    def compile_to_qiskit(circuit: Circuit):
        return tk_to_qiskit(circuit)

    @staticmethod
    def compile_to_cirq(circuit: Circuit):
        return tk_to_cirq(circuit)

    @staticmethod
    def compile_to_pyquil(circuit: Circuit):
        return tk_to_pyquil(circuit)

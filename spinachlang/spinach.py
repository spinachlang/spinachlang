"""The spinach language"""

from .parser import Parser
from .backend import Backend
from .ast_builder import AstBuilder


class Spinach:
    """The spinach language"""

    @staticmethod
    def create_circuit(code: str):
        """generate a tket circuit from spinach code"""
        built = AstBuilder().transform(Parser.get_tree(code))
        return Backend.compile_to_circuit(built)

    # ── String output (CLI / file) ─────────────────────────────────────────

    @staticmethod
    def compile(code: str, language: str) -> str:
        """translate spinach code to other languages"""
        dispatch = {
            "qasm":   Backend.compile_to_openqasm,
            "json":   Backend.compile_to_json,
            "cirq":   Backend.compile_to_cirq_python,
            "quil":   Backend.compile_to_quil,
            "latex":  Backend.compile_to_latex,
            "qir":    Backend.compile_to_qir,
            "braket": Backend.compile_to_braket,
        }
        if language not in dispatch:
            raise ValueError(
                f"Unknown target language {language!r}. "
                f"Valid options: {', '.join(sorted(dispatch))}"
            )
        return dispatch[language](Spinach.create_circuit(code=code))

    # ── Native object output (library / simulation) ────────────────────────

    @staticmethod
    def to_tket(code: str):
        """Return a pytket Circuit from Spinach source.

        The pytket Circuit is the core IR from which all other objects are
        derived. Run it on any pytket backend (AerBackend, IBMQBackend, etc.)
        or inspect it directly. No extra packages required beyond pytket core.

        Example::

            from spinachlang import Spinach
            from pytket.extensions.qiskit import AerBackend

            circuit = Spinach.to_tket(code)
            backend = AerBackend()
            backend.compile_circuit(circuit)
            handle = backend.process_circuit(circuit, n_shots=1000)
            counts = backend.get_result(handle).get_counts()
        """
        return Spinach.create_circuit(code)

    @staticmethod
    def to_cirq(code: str):
        """Return a cirq.Circuit from Spinach source.

        The returned object is a native cirq.Circuit, ready for simulation
        with cirq.Simulator() or cirq.DensityMatrixSimulator().

        Requires pytket-cirq: pip install spinachlang

        Example::

            import cirq
            from spinachlang import Spinach

            circuit = Spinach.to_cirq(code)
            result = cirq.Simulator().simulate(circuit)
            print(result.final_state_vector)
        """
        try:
            from pytket.extensions.cirq import tk_to_cirq  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "cirq objects require pytket-cirq. "
                "Install it with: pip install spinachlang"
            ) from exc
        return tk_to_cirq(Spinach.create_circuit(code))

    @staticmethod
    def to_braket(code: str):
        """Return a braket.circuits.circuit.Circuit from Spinach source.

        The returned object is a native Amazon Braket Circuit, ready to
        submit to any AWS Braket device or LocalSimulator.

        Requires pytket-braket: pip install spinachlang

        Example::

            from braket.devices import LocalSimulator
            from spinachlang import Spinach

            circuit = Spinach.to_braket(code)
            result = LocalSimulator().run(circuit, shots=1000).result()
            print(result.measurement_counts)
        """
        try:
            from pytket.extensions.braket import tk_to_braket  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "Braket objects require pytket-braket. "
                "Install it with: pip install spinachlang"
            ) from exc
        return tk_to_braket(Spinach.create_circuit(code))[0]

    @staticmethod
    def to_pyquil(code: str):
        """Return a pyquil.Program from Spinach source.

        The returned object is a native PyQuil Program, ready to run on a
        Rigetti QVM or QPU via the PyQuil QC interface.

        Requires pytket-pyquil: pip install spinachlang

        Example::

            from pyquil import get_qc
            from spinachlang import Spinach

            program = Spinach.to_pyquil(code)
            qc = get_qc("2q-qvm")
            result = qc.run(program).readout_data
        """
        try:
            from pytket.extensions.pyquil import tk_to_pyquil  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "PyQuil objects require pytket-pyquil. "
                "Install it with: pip install spinachlang"
            ) from exc
        return tk_to_pyquil(Spinach.create_circuit(code))

    @staticmethod
    def to_qiskit(code: str):
        """Return a qiskit.QuantumCircuit from Spinach source.

        The returned object is a native Qiskit QuantumCircuit, ready for
        simulation with Qiskit Aer or execution on IBM Quantum hardware.

        Requires pytket-qiskit: pip install spinachlang

        Example::

            from qiskit_aer import AerSimulator
            from spinachlang import Spinach

            circuit = Spinach.to_qiskit(code)
            circuit.measure_all()
            result = AerSimulator().run(circuit, shots=1000).result()
            print(result.get_counts())
        """
        try:
            from pytket.extensions.qiskit import tk_to_qiskit  # pylint: disable=import-outside-toplevel
        except ImportError as exc:
            raise ImportError(
                "Qiskit objects require pytket-qiskit. "
                "Install it with: pip install spinachlang"
            ) from exc
        return tk_to_qiskit(Spinach.create_circuit(code))

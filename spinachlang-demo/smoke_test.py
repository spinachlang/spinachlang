"""Smoke test: exercise every notebook code cell without Jupyter."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

import matplotlib
matplotlib.use("Agg")   # headless – no display needed
import matplotlib.pyplot as plt

from spinachlang import to_tket_circuit, to_qiskit_circuit
from qiskit_aer import AerSimulator
from qiskit.visualization import (
    plot_histogram, plot_bloch_multivector, plot_state_qsphere, plot_state_city,
)
from qiskit.quantum_info import Statevector
import qiskit, qiskit_aer

print(f"Qiskit {qiskit.__version__}  Aer {qiskit_aer.__version__}")

simulator = AerSimulator()


def statevector_from(code: str) -> Statevector:
    return Statevector.from_instruction(to_qiskit_circuit(code))


# ── 1. Superposition ──────────────────────────────────────────────────────────
SPH_SUPERPOS      = "0 -> H"
SPH_SUPERPOS_MEAS = "0 -> H | M"

tket = to_tket_circuit(SPH_SUPERPOS_MEAS)
assert tket.n_qubits == 1
print(f"[1] Superposition TKET OK  (qubits={tket.n_qubits} depth={tket.depth()})")

qc = to_qiskit_circuit(SPH_SUPERPOS_MEAS)
counts = simulator.run(qc, shots=2048).result().get_counts()
assert set(counts.keys()) <= {"0", "1"}, f"unexpected keys: {counts}"
print(f"    shots: {counts}")

sv = statevector_from(SPH_SUPERPOS)
assert abs(abs(sv.data[0]) ** 2 - 0.5) < 1e-6, sv.data
print("    statevector OK")

plot_bloch_multivector(sv, title="Superposition |+⟩")
plt.savefig("/tmp/bloch.png"); plt.close()
print("    Bloch sphere saved to /tmp/bloch.png")

# ── 2. Bell state ─────────────────────────────────────────────────────────────
SPH_BELL      = "q 0 -> H | FCX(q 1)"
SPH_BELL_MEAS = "q 0 -> H | FCX(q 1)\n* -> M"

tket = to_tket_circuit(SPH_BELL_MEAS)
assert tket.n_qubits == 2
print(f"[2] Bell TKET OK  (qubits={tket.n_qubits} depth={tket.depth()})")

qc = to_qiskit_circuit(SPH_BELL_MEAS)
counts = simulator.run(qc, shots=2048).result().get_counts()
unexpected = {k for k in counts if k not in ("00", "11")}
assert not unexpected, f"Bell: unexpected states {unexpected}"
print(f"    shots: {counts}")
print("    entanglement confirmed (only |00⟩ and |11⟩)")

sv = statevector_from(SPH_BELL)
plot_state_qsphere(sv, title="Bell |Φ+⟩")
plt.savefig("/tmp/qsphere_bell.png"); plt.close()
print("    Q-sphere saved to /tmp/qsphere_bell.png")

# ── 3. GHZ ────────────────────────────────────────────────────────────────────
SPH_GHZ      = "q 0 -> H | FCX(q 1) | FCX(q 2)"
SPH_GHZ_MEAS = SPH_GHZ + "\n* -> M"

tket = to_tket_circuit(SPH_GHZ_MEAS)
assert tket.n_qubits == 3
print(f"[3] GHZ TKET OK  (qubits={tket.n_qubits} depth={tket.depth()})")

qc = to_qiskit_circuit(SPH_GHZ_MEAS)
counts = simulator.run(qc, shots=2048).result().get_counts()
unexpected = {k for k in counts if k not in ("000", "111")}
assert not unexpected, f"GHZ: unexpected states {unexpected}"
print(f"    shots: {counts}")
print("    3-qubit GHZ confirmed")

sv = statevector_from(SPH_GHZ)
plot_state_city(sv, title="GHZ amplitudes", figsize=(8, 5), alpha=0.6,
                color=["#4CAF50", "#2196F3"])
plt.savefig("/tmp/state_city_ghz.png"); plt.close()
print("    State-city saved to /tmp/state_city_ghz.png")

# ── 4. Deutsch ────────────────────────────────────────────────────────────────
SPH_DEUTSCH = "\n".join([
    "q 1 -> X",
    "[q 0, q 1] -> H",
    "q 1 -> CX(q 0)",
    "q 0 -> H | M",
])

tket = to_tket_circuit(SPH_DEUTSCH)
print(f"[4] Deutsch TKET OK  (qubits={tket.n_qubits} depth={tket.depth()})")

qc = to_qiskit_circuit(SPH_DEUTSCH)
counts = simulator.run(qc, shots=1024).result().get_counts()
print(f"    shots: {counts}")

q0_bits = {state[-1]: n for state, n in counts.items()}
dominant = max(q0_bits, key=q0_bits.get)
assert dominant == "1", f"Deutsch wrong answer: dominant bit = {dominant}"
print("    verdict: BALANCED (correct)")

qc.draw("mpl")
plt.savefig("/tmp/deutsch_circuit.png"); plt.close()
print("    circuit diagram saved to /tmp/deutsch_circuit.png")

print("\nAll smoke tests passed.")


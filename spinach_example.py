import cirq

circuit = cirq.Circuit([
    cirq.Moment(
        cirq.X(cirq.LineQubit(1)),
    ),
    cirq.Moment(
        cirq.H(cirq.LineQubit(1)),
    ),
    cirq.Moment(
        cirq.CNOT(cirq.LineQubit(0), cirq.LineQubit(1)),
    ),
    cirq.Moment(
        cirq.X(cirq.LineQubit(1)),
    ),
    cirq.Moment(
        cirq.H(cirq.LineQubit(1)),
    ),
    cirq.Moment(
        cirq.CNOT(cirq.LineQubit(0), cirq.LineQubit(1)),
    ),
    cirq.Moment(
        cirq.measure(cirq.LineQubit(1), key=cirq.MeasurementKey(name='c[0]')),
        cirq.measure(cirq.LineQubit(0), key=cirq.MeasurementKey(name='c[1]')),
    ),
])
print(circuit)
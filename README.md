# Spinach lang
![logo for Spinach](spinach.png "Spinach")
Spinach is a quantum programming language.
Its goal is to provide a dedicated language that can simulate and compile code for execution on quantum computers. Spinach also aims to offer tools that allow users to do more with less code.

At the moment, there are three kinds of statements. qbit declaration, pipeline declaration and actions.
## qubit declaration
To create a qubit, name a qubit and assign a number like this:

```

tom : 1
```

## pipeline declaration
To create a pipeline, name it the same way but by giving it a pipeline instead of a number

```

entangle : H | CNOT(tom)

```

This way we can store gate sequances.

## pipeline

The pipelines are what makes this language so fun. In other quantum languages, every time we invoque a gate, we need a new line. Here we can tell in one line to use a sequance of gate on a qubit.

```

N | H | CNOT(tom) | M(0)

```

## gate

The gates are the core of quantum logic. Gere are all the available gates today:

```

N or X
Y
Z
H
S
ST
TT
T
RX(theta)
RY(theta)
RZ(theta)
CNOT(control) or CX(control)
CY(control)
CZ(control)
CH(control)
CU1(phi)
SWAP(target)
TOFFOLI(control1, control2) or CCX(control1, control2)
M(bit) or MEASURE(bit)

```

## how to use
create a venv and start it:

```bash
python -m venv venv
source venv/bin/activate

```
install the dependencies

```bash

pip install -r requirements.txt

```
Create a spinach script and run it like this

```bash

python . -l qasm your_script.sph

```

Here's an example of script to try:

```

tom : 1
charle : 0
entangle : N | H | CNOT(charle) 
tom -> 2 entangle
tom -> MEASURE(0)
charle -> MEASURE(1)

```

## features

At the moment, compiling into qasm is the only output we can get. In the future, I want to enable more languages to compile to and the possibility to simulate and work on jupyter. This language uses tket so anything tket can do, spinach can also do. This language will be usable by itself but also as a python librarie.

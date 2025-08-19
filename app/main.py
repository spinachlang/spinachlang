#!/usr/bin/env python3

import sys
import argparse
import pathlib
from app.spinach import Spinach


def read_code(path: str) -> str:
    if path == "-":
        return sys.stdin.read()
    p = pathlib.Path(path)
    if not p.is_file():
        raise FileNotFoundError(f"Source file not found: {path}")
    if p.suffix.lower() != ".sph":
        raise ValueError(f"Expected a .sph file, got '{p.suffix}'")
    return p.read_text(encoding="utf-8")


def infer_output_path(
    input_path: str, language: str, provided: str | None
) -> pathlib.Path:
    if provided and provided != "-":
        return pathlib.Path(provided)
    in_path = pathlib.Path(input_path)
    stem = in_path.stem
    ext_map = {
        "qasm": ".qasm",
        "json": ".json",
        "cirq": ".py",
        "quil": ".quil",
    }
    return pathlib.Path(f"{stem}{ext_map[language]}")


def main():
    parser = argparse.ArgumentParser(
        prog="spinach-compile",
        description="Compile .sph Spinach source into target quantum backend.",
    )
    parser.add_argument(
        "source",
        help="Input .sph file, or '-' to read from stdin (then output must be stdout).",
    )
    parser.add_argument(
        "-l",
        "--language",
        required=True,
        choices=["qasm", "cirq", "quil", "json"],
        help="Target compilation language.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="Output path (default: inferred from source and language). Use '-' for stdout.",
    )
    args = parser.parse_args()

    try:
        code = read_code(args.source)
        compiled = Spinach.compile(code=code, language=args.language)
        out_path = infer_output_path(args.source, args.language, args.output)

        if args.output == "-" or (args.output is None and str(out_path) == "-"):
            sys.stdout.write(compiled)
        else:
            # If output is explicitly "-" or user wants stdout
            if args.output == "-":
                sys.stdout.write(compiled)
            else:
                out_path.write_text(compiled, encoding="utf-8")
    except Exception as e:
        sys.stderr.write(f"Error: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()

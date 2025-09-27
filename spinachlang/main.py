"""The CLI of spinach"""

import sys
import argparse
import pathlib
from .exit_code import ExitCode
from .spinach import Spinach


def read_code(path: str) -> str:
    """Open the spinach file"""
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
    """Name the output file"""
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


def main() -> None:
    """CLI entry point"""
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
    except FileNotFoundError as e:
        sys.stderr.write(f"[File Error] {e}\n")
        sys.exit(ExitCode.FILE_NOT_FOUND)
    except ValueError as e:
        sys.stderr.write(f"[Input Error] {e}\n")
        sys.exit(ExitCode.INVALID_INPUT)
    except OSError as e:
        sys.stderr.write(f"[System Error] Failed to read file: {e}\n")
        sys.exit(ExitCode.READ_ERROR)

    compiled = Spinach.compile(code=code, language=args.language)

    try:
        out_path = infer_output_path(args.source, args.language, args.output)

        if args.output == "-" or (args.output is None and str(out_path) == "-"):
            sys.stdout.write(compiled)
        else:
            out_path.write_text(compiled, encoding="utf-8")
    except OSError as e:
        sys.stderr.write(f"[Write Error] Could not write output: {e}\n")
        sys.exit(ExitCode.WRITE_ERROR)


if __name__ == "__main__":
    main()

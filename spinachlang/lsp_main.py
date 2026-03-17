"""Console-script entry point for the SpinachLang LSP server.

Usage (stdio transport, called by editors / VS Code extensions):
    spinachlang-lsp

Usage (TCP, useful for debugging):
    spinachlang-lsp --tcp --port 2087
"""

import argparse
import logging
import sys

from .lsp import SERVER_NAME, SERVER_VERSION, server


def _build_arg_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the LSP entry point."""
    p = argparse.ArgumentParser(
        prog="spinachlang-lsp",
        description=f"{SERVER_NAME} {SERVER_VERSION} — Language Server for SpinachLang (.sph files).",
    )
    p.add_argument(
        "--tcp",
        action="store_true",
        default=False,
        help="Start server over TCP instead of stdio.",
    )
    p.add_argument(
        "--host",
        default="127.0.0.1",
        help="TCP host to bind when --tcp is used (default: 127.0.0.1).",
    )
    p.add_argument(
        "--port",
        type=int,
        default=2087,
        help="TCP port to bind when --tcp is used (default: 2087).",
    )
    p.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging verbosity (default: WARNING).",
    )
    return p


def main() -> None:
    """Parse CLI arguments and start the SpinachLang LSP server."""
    args = _build_arg_parser().parse_args()

    logging.basicConfig(
        stream=sys.stderr,
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    )

    if args.tcp:
        server.start_tcp(args.host, args.port)
    else:
        server.start_io()


if __name__ == "__main__":
    main()


"""Top-level package for SpinachLang.

Provides Spinach class and helper functions for circuit compilation and TKET integration.
"""

from .spinach import Spinach

compile_code = Spinach.compile
create_tket_circuit = Spinach.create_circuit

__all__ = ["compile_code", "create_tket_circuit", "Spinach"]

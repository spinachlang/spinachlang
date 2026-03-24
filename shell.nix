# Development shell for SpinachLang on NixOS.
#
# PyTKET (and other C++ extensions) require libstdc++.so.6 which is not in the
# standard library search path on NixOS.  This shell sets LD_LIBRARY_PATH so
# that all compiled extensions load correctly when using a uv-managed venv.
#
# Usage (fresh machine):
#   nix-shell                        # enter the dev shell (auto-creates .venv)
#   source .venv/bin/activate        # activate the virtualenv
#   uv pip install '.[lsp,dev]'      # install all dependencies
#   spinachlang --help               # verify the installation
#
# Optional backends (Quil/pyquil requires Python <=3.12):
#   uv pip install '.[pyquil]'
#
# NixOS 24.05+: if nix-shell fails with "flakes disabled", run once:
#   mkdir -p ~/.config/nix
#   echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  name = "spinachlang-dev";

  packages = with pkgs; [
    # ── Python runtime ────────────────────────────────────────────────────────
    # Project requires Python >=3.10; 3.13 is the currently tested version.
    python313

    # ── Package manager ───────────────────────────────────────────────────────
    # uv is used for all virtualenv and package management workflows.
    uv

    # ── Version control ───────────────────────────────────────────────────────
    git

    # ── C/C++ runtime ─────────────────────────────────────────────────────────
    # libstdc++.so.6 — required by pytket's compiled C++ extension modules.
    stdenv.cc.cc.lib
    # zlib — pulled in by many compiled Python wheels.
    zlib
    # libffi — required by Python's ctypes/cffi layer and several C extensions.
    libffi

    # ── Rust toolchain ────────────────────────────────────────────────────────
    # Required to build maturin-based wheels (e.g. qcs-sdk-python, pulled in by
    # pytket-pyquil) without relying on rustup.
    cargo
    rustc

    # ── OpenSSL ───────────────────────────────────────────────────────────────
    # openssl.out — runtime shared libraries (libssl.so, libcrypto.so).
    # openssl.dev — headers + pkg-config metadata for wheels that compile
    #               OpenSSL bindings from source (e.g. qcs-sdk-python).
    openssl.out
    openssl.dev

    # ── Build helpers ─────────────────────────────────────────────────────────
    pkg-config

    # ── SSL/TLS certificates ──────────────────────────────────────────────────
    # Required so that uv / pip can validate HTTPS certificates when
    # downloading packages from PyPI.
    cacert
  ];

  shellHook = ''
    # ── Dynamic linker paths ──────────────────────────────────────────────────
    # Expose every native shared library that Python C/C++ extensions may need
    # at import time.
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:${pkgs.libffi}/lib:${pkgs.openssl.out}/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

    # ── pkg-config search path ────────────────────────────────────────────────
    # Let maturin / setuptools locate OpenSSL when building wheels from source.
    export PKG_CONFIG_PATH="${pkgs.openssl.dev}/lib/pkgconfig''${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"

    # ── Rust / maturin ────────────────────────────────────────────────────────
    # Point maturin at the nix-provided cargo so it does not invoke rustup
    # (which has no default toolchain set in this environment).
    export CARGO="${pkgs.cargo}/bin/cargo"

    # ── SSL certificates ──────────────────────────────────────────────────────
    # Required for uv / pip to validate PyPI HTTPS certificates.
    export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
    export NIX_SSL_CERT_FILE="$SSL_CERT_FILE"

    # ── Virtualenv bootstrap ──────────────────────────────────────────────────
    # Automatically create .venv on first entry so the user can immediately
    # activate it without an extra manual step.
    if [ ! -d .venv ]; then
      echo "  → No .venv found — creating one with uv (python3.13)…"
      uv venv --python python3.13 --quiet
    fi

    echo ""
    echo "╔══════════════════════════════════════════════════════╗"
    echo "║        SpinachLang dev shell — NixOS ready           ║"
    echo "╠══════════════════════════════════════════════════════╣"
    echo "║  Quick-start (first time):                           ║"
    echo "║    source .venv/bin/activate                         ║"
    echo "║    uv pip install '.[lsp,dev]'                       ║"
    echo "║    spinachlang --help                                ║"
    echo "║                                                      ║"
    echo "║  Run tests : pytest                                  ║"
    echo "║  Run LSP   : spinachlang-lsp                         ║"
    echo "║  Build dist: python -m build && twine check dist/*   ║"
    echo "╚══════════════════════════════════════════════════════╝"
    echo ""
  '';
}


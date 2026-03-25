# Nix shell for the SpinachLang × IBM Quantum Simulator Jupyter demo.
#
# This shell provides every native library that PyTKET, Qiskit-Aer, and their
# C/C++ wheels need on NixOS, plus Python, uv, and Jupyter itself.
#
# ── Quick-start ───────────────────────────────────────────────────────────────
#
#   nix-shell                          # enter the shell (auto-creates .venv)
#   source .venv/bin/activate          # activate the virtualenv
#   pip install -r requirements.txt    # install Python deps
#   jupyter lab spinachlang_ibm_demo.ipynb   # open the notebook
#
# ── Notes ─────────────────────────────────────────────────────────────────────
#  • pytket and qiskit-aer ship compiled C++ extensions that require libstdc++
#    at runtime.  LD_LIBRARY_PATH is set automatically by the shellHook below.
#  • If you want to install spinachlang from local source instead of PyPI, run:
#      pip install -e ../   (from inside the demo directory)
#  • NixOS 24.05+: if nix-shell is disabled, enable flakes once:
#      mkdir -p ~/.config/nix
#      echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf

{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  name = "spinachlang-demo";

  packages = with pkgs; [
    # ── Python runtime ────────────────────────────────────────────────────────
    python313

    # ── Package manager ───────────────────────────────────────────────────────
    uv

    # ── Version control ───────────────────────────────────────────────────────
    git

    # ── C/C++ runtime ─────────────────────────────────────────────────────────
    # libstdc++.so.6  — required by pytket and qiskit-aer compiled extensions.
    stdenv.cc.cc.lib
    # zlib — pulled in by many compiled Python wheels.
    zlib
    # libffi — required by Python ctypes/cffi layer and several C extensions.
    libffi

    # ── Rust toolchain ────────────────────────────────────────────────────────
    # Some transitive deps (e.g. qcs-sdk-python) ship sdists requiring Rust.
    cargo
    rustc

    # ── OpenSSL ───────────────────────────────────────────────────────────────
    openssl.out   # runtime shared libraries (libssl.so, libcrypto.so)
    openssl.dev   # headers + pkg-config for wheels that compile OpenSSL bindings

    # ── Build helpers ─────────────────────────────────────────────────────────
    pkg-config

    # ── SSL/TLS certificates ──────────────────────────────────────────────────
    cacert
  ];

  shellHook = ''
    # ── Dynamic linker paths ──────────────────────────────────────────────────
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib:${pkgs.libffi}/lib:${pkgs.openssl.out}/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

    # ── pkg-config ────────────────────────────────────────────────────────────
    export PKG_CONFIG_PATH="${pkgs.openssl.dev}/lib/pkgconfig''${PKG_CONFIG_PATH:+:$PKG_CONFIG_PATH}"

    # ── Rust / maturin ────────────────────────────────────────────────────────
    export CARGO="${pkgs.cargo}/bin/cargo"

    # ── SSL certificates ──────────────────────────────────────────────────────
    export SSL_CERT_FILE="${pkgs.cacert}/etc/ssl/certs/ca-bundle.crt"
    export NIX_SSL_CERT_FILE="$SSL_CERT_FILE"

    # ── Virtualenv bootstrap ──────────────────────────────────────────────────
    if [ ! -d .venv ]; then
      echo "  → No .venv found — creating one with uv (python3.13)…"
      uv venv --python python3.13 --quiet
    fi

    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║   SpinachLang × IBM Quantum Demo — NixOS shell ready        ║"
    echo "╠══════════════════════════════════════════════════════════════╣"
    echo "║  First time setup:                                           ║"
    echo "║    source .venv/bin/activate                                 ║"
    echo "║    pip install -r requirements.txt                           ║"
    echo "║                                                              ║"
    echo "║  (optional) install spinachlang from local source:           ║"
    echo "║    pip install -e ../                                        ║"
    echo "║                                                              ║"
    echo "║  Launch the demo:                                            ║"
    echo "║    jupyter lab spinachlang_ibm_demo.ipynb                    ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
  '';
}


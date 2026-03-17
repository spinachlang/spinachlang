# Development shell for SpinachLang on NixOS.
#
# PyTKET (and other C++ extensions) require libstdc++.so.6 which is not in the
# standard library search path on NixOS.  This shell exposes the GCC C++ runtime
# library through LD_LIBRARY_PATH so that the compiled extensions load correctly
# when using a uv-managed virtual environment.
#
# Usage:
#   nix-shell          # drop into the dev shell
#   nix-shell --run 'uv pip install .'
#   nix-shell --run '.venv/bin/spinachlang --help'

{ pkgs ? import <nixpkgs> { } }:

pkgs.mkShell {
  name = "spinachlang-dev";

  packages = with pkgs; [
    # C++ runtime – required by pytket's compiled extension modules
    stdenv.cc.cc.lib
    # zlib is also commonly needed by compiled Python wheels
    zlib
  ];

  shellHook = ''
    # Make libstdc++.so.6 (and libz.so) discoverable by the dynamic linker.
    export LD_LIBRARY_PATH="${pkgs.stdenv.cc.cc.lib}/lib:${pkgs.zlib}/lib''${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

    echo "SpinachLang dev shell – LD_LIBRARY_PATH set for pytket C++ extensions."
    echo "Run: uv pip install . && .venv/bin/spinachlang --help"
  '';
}


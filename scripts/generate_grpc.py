#!/usr/bin/env python3
"""Generate gRPC Python code from proto files (output under app/schemas/proto)."""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROTO_DIR = ROOT / "src" / "schemas" / "proto"
OUT_DIR = PROTO_DIR

OUT_DIR.mkdir(parents=True, exist_ok=True)

# Compile all *.proto files in the proto dir (echo.proto, action.proto, ...)
proto_files = sorted(PROTO_DIR.glob("*.proto"))
if not proto_files:
    print("No .proto files found in", PROTO_DIR, file=sys.stderr)
    sys.exit(1)

cmd = [
    sys.executable,
    "-m",
    "grpc_tools.protoc",
    f"-I{PROTO_DIR}",
    f"--python_out={OUT_DIR}",
    f"--grpc_python_out={OUT_DIR}",
    *[str(p) for p in proto_files],
]
subprocess.run(cmd, check=True)

# Fix imports in all *_pb2_grpc.py so they work inside the package
for grpc_file in OUT_DIR.glob("*_pb2_grpc.py"):
    text = grpc_file.read_text()
    text = re.sub(r"import (\w+_pb2) as ", r"from . import \1 as ", text)
    grpc_file.write_text(text)

print("Generated gRPC code in", OUT_DIR, "for:", ", ".join(p.name for p in proto_files))

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import subprocess

try:
    from google.protobuf import descriptor_pb2
    from google.protobuf import descriptor_pool
except ModuleNotFoundError as exc:  # pragma: no cover - exercised in dependency-limited envs
    descriptor_pb2 = None  # type: ignore[assignment]
    descriptor_pool = None  # type: ignore[assignment]
    _PROTOBUF_IMPORT_ERROR = exc
else:
    _PROTOBUF_IMPORT_ERROR = None


@dataclass(frozen=True)
class DescriptorBundle:
    descriptor_set_path: Path
    pool: object


def _require_protobuf_runtime() -> None:
    if _PROTOBUF_IMPORT_ERROR is not None:
        raise RuntimeError(
            "python protobuf runtime is required (install package: protobuf)"
        ) from _PROTOBUF_IMPORT_ERROR


def build_descriptor_bundle(repo_root: Path, out_dir: Path) -> DescriptorBundle:
    _require_protobuf_runtime()

    protoc = shutil.which("protoc")
    if not protoc:
        raise RuntimeError("protoc is required but was not found in PATH")

    proto_root = repo_root / "oaa"
    proto_files = sorted(proto_root.rglob("*.proto"))
    if not proto_files:
        raise RuntimeError(f"no proto files found under {proto_root}")

    out_dir.mkdir(parents=True, exist_ok=True)
    descriptor_set_path = out_dir / "oaa-descriptor-set.pb"

    cmd = [
        protoc,
        f"--proto_path={repo_root}",
        f"--descriptor_set_out={descriptor_set_path}",
        "--include_imports",
    ]
    cmd.extend(str(path.relative_to(repo_root)) for path in proto_files)

    run = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if run.returncode != 0:
        stderr = run.stderr.strip() or "unknown protoc error"
        raise RuntimeError(f"failed to build descriptor set: {stderr}")

    file_set = descriptor_pb2.FileDescriptorSet()  # type: ignore[union-attr]
    file_set.ParseFromString(descriptor_set_path.read_bytes())

    pool = descriptor_pool.DescriptorPool()  # type: ignore[union-attr]
    for file_proto in file_set.file:
        pool.Add(file_proto)

    return DescriptorBundle(descriptor_set_path=descriptor_set_path, pool=pool)

from __future__ import annotations

from pathlib import Path
import re

from analysis.tools.proto_stream_validator.message_map import resolve_message_type

from .models import DispatchObservation


_BRANCH_RE = re.compile(
    r"(?:case\s+(0x[0-9a-fA-F]+|\d+)\s*:|"
    r"if\s*\(\s*[A-Za-z_]\w*\s*==\s*(0x[0-9a-fA-F]+|\d+)\s*\)\s*\{)"
)
_SERVICE_BRANCH_RE = re.compile(
    r"(?:case\s+(0x[0-9a-fA-F]+|\d+)\s*:|"
    r"if\s*\(\s*[A-Za-z_]\w*\s*(?:==|!=)\s*(0x[0-9a-fA-F]+|\d+)\s*\)\s*\{?)"
)
_DEFAULT_INSTANCE_RE = re.compile(
    r"\b([a-z][a-z0-9]*)\s+[A-Za-z_]\w*\s*=\s*\1\.a\s*;"
)
_BUILDER_INSTANCE_RE = re.compile(
    r"\b[A-Za-z_]\w*\s+([A-Za-z_]\w*)\s*=\s*([a-z][a-z0-9]*)\.a\.o\(\)"
)
_SERVICE_TOKEN_RE = re.compile(r"\brpq\.([A-Z][A-Z0-9_]*)\b")
_SERVICE_BY_TOKEN = {
    "CONTROL": "control",
    "INPUT_SOURCE": "input_source",
    "SENSOR_SOURCE": "sensor_source",
    "VIDEO_SINK": "media_sink",
    "AUDIO_SINK_GUIDANCE": "media_sink",
    "AUDIO_SINK_MEDIA": "media_sink",
}
_SERVICE_BY_ID = {
    1: "control",
    2: "media_sink",
    3: "media_sink",
    4: "media_sink",
    5: "media_sink",
    7: "sensor_source",
    8: "input_source",
    9: "bluetooth",
    10: "navigation",
    11: "media_info",
    13: "phone_status",
    15: "radio",
    17: "wifi_projection",
    19: "car_control",
    20: "car_local_media",
}
_SUPER_SERVICE_RE = re.compile(r"\bsuper\(\s*(\d+)\s*,")
_NAMED_MESSAGE_RE = re.compile(
    r'"(?:Wrong\s+)?([A-Z][A-Za-z0-9]+)\s+message(?:\\n|\.|"|\s)'
)
_ID_COMPARE_RE = re.compile(
    r"\b[A-Za-z_]\w*\s*(?:==|!=)\s*(0x[0-9a-fA-F]+|\d+)"
)
_SEND_LITERAL_RE = re.compile(
    r"\.\w+\(\s*(0x[0-9a-fA-F]+|\d+)\s*,"
)
_PASCAL_TOKEN_RE = re.compile(r"\b[A-Z][A-Za-z0-9]{7,}\b")
_CANONICAL_LOG_ALIASES = {
    "AuthenticationResult": "BluetoothAuthenticationResult",
}


def _extract_file_observations(
    path: Path,
    sources: Path,
    apk_class_names: set[str],
    *,
    service_type: str,
    lookahead_lines: int,
    branch_pattern: re.Pattern[str] = _BRANCH_RE,
) -> list[DispatchObservation]:
    lines = path.read_text(errors="ignore").splitlines()
    observations: list[DispatchObservation] = []
    for index, line in enumerate(lines):
        branch = branch_pattern.search(line)
        if not branch:
            continue
        message_id = int(branch.group(1) or branch.group(2), 0)
        try:
            canonical_name = resolve_message_type(
                "",
                0,
                message_id,
                service_type=service_type,
            )
        except KeyError:
            continue

        candidate_start = index + 1
        if "!=" in branch.group(0) and "{" in line:
            depth = line.count("{") - line.count("}")
            if depth > 0:
                for guard_index in range(index + 1, len(lines)):
                    depth += lines[guard_index].count("{") - lines[guard_index].count("}")
                    if depth <= 0:
                        candidate_start = guard_index + 1
                        break
        stop = min(candidate_start + lookahead_lines, len(lines))
        for candidate_index in range(candidate_start, stop):
            if branch_pattern.search(lines[candidate_index]):
                break
            default_instance = _DEFAULT_INSTANCE_RE.search(lines[candidate_index])
            if not default_instance:
                continue
            apk_class = default_instance.group(1)
            if apk_class in apk_class_names:
                observations.append(
                    DispatchObservation(
                        canonical_name=canonical_name,
                        message_id=message_id,
                        apk_class=apk_class,
                        source=str(path.relative_to(sources)),
                        line=candidate_index + 1,
                        service_type=service_type,
                    )
                )
            break
    return observations


def extract_control_dispatch(
    jadx_root: Path,
    apk_class_names: set[str],
    *,
    lookahead_lines: int = 18,
) -> list[DispatchObservation]:
    """Extract conservative control message-ID to proto-class observations.

    This deliberately emits observations rather than mappings. The matcher must
    still confirm that an observed APK class has the canonical schema shape.
    """
    sources = jadx_root / "sources"
    observations: list[DispatchObservation] = []
    for path in sources.rglob("*.java"):
        observations.extend(
            _extract_file_observations(
                path,
                sources,
                apk_class_names,
                service_type="control",
                lookahead_lines=lookahead_lines,
            )
        )
    return observations


def extract_service_dispatch(
    jadx_root: Path,
    apk_class_names: set[str],
    *,
    lookahead_lines: int = 18,
) -> list[DispatchObservation]:
    """Extract observations from files with explicit ``rpq`` service tokens."""
    sources = jadx_root / "sources"
    observations: list[DispatchObservation] = []
    for path in sources.rglob("*.java"):
        text = path.read_text(errors="ignore")
        services = {
            _SERVICE_BY_TOKEN[token]
            for token in _SERVICE_TOKEN_RE.findall(text)
            if token in _SERVICE_BY_TOKEN
        }
        services.update(
            _SERVICE_BY_ID[int(service_id)]
            for service_id in _SUPER_SERVICE_RE.findall(text)
            if int(service_id) in _SERVICE_BY_ID
        )
        if len(services) != 1:
            continue
        service_type = next(iter(services))
        if service_type == "control":
            continue
        observations.extend(
            _extract_file_observations(
                path,
                sources,
                apk_class_names,
                service_type=service_type,
                lookahead_lines=lookahead_lines,
                branch_pattern=_SERVICE_BRANCH_RE,
            )
        )
    return observations


def extract_named_dispatch(
    jadx_root: Path,
    apk_class_names: set[str],
    *,
    lookbehind_lines: int = 48,
) -> list[DispatchObservation]:
    """Extract proto identities spelled out by nearby validation log strings."""
    sources = jadx_root / "sources"
    observations: list[DispatchObservation] = []
    for path in sources.rglob("*.java"):
        lines = path.read_text(errors="ignore").splitlines()
        for index, line in enumerate(lines):
            named = _NAMED_MESSAGE_RE.search(line)
            if not named:
                continue
            start = max(0, index - lookbehind_lines)
            apk_class = None
            message_id = 0
            for candidate_index in range(index - 1, start - 1, -1):
                if apk_class is None:
                    default_instance = _DEFAULT_INSTANCE_RE.search(lines[candidate_index])
                    if default_instance and default_instance.group(1) in apk_class_names:
                        apk_class = default_instance.group(1)
                if message_id == 0:
                    comparison = _ID_COMPARE_RE.search(lines[candidate_index])
                    if comparison:
                        message_id = int(comparison.group(1), 0)
                    else:
                        branch = _BRANCH_RE.search(lines[candidate_index])
                        if branch:
                            message_id = int(branch.group(1) or branch.group(2), 0)
                if apk_class is not None and message_id != 0:
                    break
            if apk_class is None:
                continue
            observations.append(
                DispatchObservation(
                    canonical_name=f"oaa.proto.messages.{named.group(1)}",
                    message_id=message_id,
                    apk_class=apk_class,
                    source=str(path.relative_to(sources)),
                    line=index + 1,
                    service_type="named_log",
                )
            )
    return observations


def extract_canonical_name_logs(
    jadx_root: Path,
    apk_class_names: set[str],
    canonical_names: set[str],
    *,
    context_lines: int = 64,
) -> list[DispatchObservation]:
    """Associate canonical names in logs with a nearby proto instance/builder."""
    simple_names = {name.rsplit(".", 1)[-1] for name in canonical_names}
    sources = jadx_root / "sources"
    observations = []
    for path in sources.rglob("*.java"):
        lines = path.read_text(errors="ignore").splitlines()
        for index, line in enumerate(lines):
            if '"' not in line or _NAMED_MESSAGE_RE.search(line):
                continue
            tokens = set(_PASCAL_TOKEN_RE.findall(line))
            tokens.update(
                canonical
                for short, canonical in _CANONICAL_LOG_ALIASES.items()
                if short in line
            )
            matches = sorted(tokens & simple_names, key=len, reverse=True)
            if not matches:
                continue
            canonical_simple_name = matches[0]
            canonical_name = f"oaa.proto.messages.{canonical_simple_name}"
            if canonical_name not in canonical_names:
                continue

            start = max(0, index - context_lines)
            stop = min(len(lines), index + context_lines + 1)
            class_candidates = []
            for candidate_index in range(start, stop):
                default_instance = _DEFAULT_INSTANCE_RE.search(lines[candidate_index])
                if default_instance and default_instance.group(1) in apk_class_names:
                    class_candidates.append(
                        (
                            abs(candidate_index - index),
                            candidate_index,
                            default_instance.group(1),
                            None,
                        )
                    )
                builder = _BUILDER_INSTANCE_RE.search(lines[candidate_index])
                if builder and builder.group(2) in apk_class_names:
                    class_candidates.append(
                        (
                            abs(candidate_index - index),
                            candidate_index,
                            builder.group(2),
                            builder.group(1),
                        )
                    )
            if not class_candidates:
                continue
            _, class_index, apk_class, builder_variable = min(class_candidates)

            message_id = 0
            id_candidates = []
            for candidate_index in range(start, stop):
                branch = _BRANCH_RE.search(lines[candidate_index])
                if branch and builder_variable is None:
                    id_candidates.append(
                        (
                            abs(candidate_index - class_index),
                            int(branch.group(1) or branch.group(2), 0),
                        )
                    )
                send = _SEND_LITERAL_RE.search(lines[candidate_index])
                if send and (
                    builder_variable is None
                    or re.search(
                        rf"\b{re.escape(builder_variable)}\.q\(\)",
                        lines[candidate_index],
                    )
                ):
                    id_candidates.append(
                        (abs(candidate_index - class_index), int(send.group(1), 0))
                    )
            if id_candidates:
                message_id = min(id_candidates)[1]
            observations.append(
                DispatchObservation(
                    canonical_name=canonical_name,
                    message_id=message_id,
                    apk_class=apk_class,
                    source=str(path.relative_to(sources)),
                    line=index + 1,
                    service_type="canonical_log",
                )
            )
    return observations


def extract_dispatch_observations(
    jadx_root: Path,
    apk_class_names: set[str],
    canonical_names: set[str] | None = None,
) -> list[DispatchObservation]:
    """Combine control and explicit service-context observations."""
    combined = extract_control_dispatch(jadx_root, apk_class_names)
    combined.extend(extract_service_dispatch(jadx_root, apk_class_names))
    combined.extend(extract_named_dispatch(jadx_root, apk_class_names))
    if canonical_names:
        combined.extend(
            extract_canonical_name_logs(
                jadx_root,
                apk_class_names,
                canonical_names,
            )
        )
    deduplicated = {
        (
            item.canonical_name,
            item.message_id,
            item.apk_class,
            item.source,
            item.line,
            item.service_type,
        ): item
        for item in combined
    }
    return sorted(
        deduplicated.values(),
        key=lambda item: (
            item.canonical_name,
            item.apk_class,
            item.source,
            item.line,
            item.service_type,
        ),
    )

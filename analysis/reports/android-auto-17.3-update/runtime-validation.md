# Runtime Validation Matrix

Execution date: 2026-07-24. The required preflight took the no-device branch:
`adb devices -l` reported no ADB `device` row. Per the Task 9 branch rule, no
scenario capture, `adb logcat -c`, copy, conversion, or validator command was
attempted. The separate Python capture environment check also found that the
`frida` module is unavailable.

| Probe | Required capability | Setup and command | Expected protocol event | Result | Evidence path | Status |
|---|---|---|---|---|---|---|
| RT-ENV | An ADB `device` row, target package version, and the capture Python dependencies/tool | Required Task 9 preflight commands, recorded below | A target `17.3.662804-release` package can be interrogated and the capture tool can start | runtime-unverified | Preflight transcript below; `RT-ENV` is deferred because no ADB device was available. | runtime-unverified: no ADB device available during execution; validated capture Python environment unavailable (`frida`) |
| RT-VIDEO-FOCUS | Target-version phone attached to the DHU, video-focus controls, and capture dependencies | Not attempted by the no-device branch; required capture would be `phone_full_capture.py --duration 90 --scenario aa-17.3-video-focus-ui` | Framed `0x8007`, `0x8008`, `0x8009`, and `0x800A` focus traffic, with normalized direction checked against Task 3 | runtime-unverified | No capture artifact exists; see the preflight transcript below. | runtime-unverified: no ADB device available during execution |
| RT-VIDEO-UI | Target-version phone attached to the DHU, a day/night or blended-UI transition, and capture dependencies | Not attempted by the no-device branch; shares the `aa-17.3-video-focus-ui` capture | Framed overlay/UI-token configuration traffic with direction checked against Task 3 | runtime-unverified | No capture artifact exists; see the preflight transcript below. | runtime-unverified: no ADB device available during execution |
| RT-RADIO | Target-version phone attached to the DHU, radio service activation, and capture dependencies | Not attempted by the no-device branch; required capture would be `phone_full_capture.py --duration 120 --scenario aa-17.3-radio` | Discovery, initial list/info, one tune request/response, and mute when the runtime activates the service | runtime-unverified | No capture artifact exists; see the preflight transcript below. | runtime-unverified: no ADB device available during execution |
| RT-CARCONTROL | Target-version phone attached to the DHU, car-control service activation, and capture dependencies | Not attempted by the no-device branch; required capture would be `phone_full_capture.py --duration 120 --scenario aa-17.3-car-control` | Discovery, listener registration, state report, one set/result, and one action when the runtime activates the service | runtime-unverified | No capture artifact exists; see the preflight transcript below. | runtime-unverified: no ADB device available during execution |
| RT-MULTIDISPLAY | Target-version phone attached to a DHU topology that can advertise MAIN, CLUSTER, and AUXILIARY, plus capture dependencies | Not attempted by the no-device branch; required capture would be `phone_full_capture.py --duration 120 --scenario aa-17.3-multi-display` | Discovery, channels, AV setup/open, display/input IDs, media streams, and focus for the advertised topology | runtime-unverified | No capture artifact exists; see the preflight transcript below. | runtime-unverified: no ADB device available during execution |

## Required environment preflight

### 1. `adb devices -l`

Exit code: `0`

stdout:

```text
List of devices attached

```

stderr: empty

Decision input: there is no row whose state is `device`.

### 2. `adb shell dumpsys package com.google.android.projection.gearhead | rg 'versionName|longVersionCode'`

Exit code: `1`

stdout: empty

stderr:

```text
adb: no devices/emulators found
```

No installed Android Auto version was observable, so no traffic can be used to
confirm claims about `17.3.662804-release`.

### 3. `python3 -c 'import frida, cryptography; print("capture dependencies present")'`

Exit code: `1`

stdout: empty

stderr:

```text
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import frida, cryptography; print("capture dependencies present")
    ^^^^^^^^^^^^^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'frida'
```

The validated-capture Python environment is unavailable because module
`frida` is missing. `cryptography` was not independently evaluated because
Python stops at the failed `frida` import.

### 4. `python3 /mnt/e/claude/personal/android-auto-dhu/phone_full_capture.py --help`

Exit code: `1`

stdout: empty

stderr:

```text
Traceback (most recent call last):
  File "/mnt/e/claude/personal/android-auto-dhu/phone_full_capture.py", line 15, in <module>
    import frida
ModuleNotFoundError: No module named 'frida'
```

The external capture tool was read/executed only. It was not modified.

## Capture preservation and re-run prerequisites

No ignored runtime directory or artifact was created: creating it and clearing
logcat are Steps 2-5 actions, which the no-device branch forbids. Therefore
there are no frame citations, channel IDs, message IDs, directions, payload
decodes, converted JSONL files, or validator baselines to report.

The worktree's `analysis/aa_apk_17.3.662804_apkm` entry is a symbolic link to
the primary checkout. Consequently the mandated worktree command
`git check-ignore -q analysis/aa_apk_17.3.662804_apkm/runtime-validation`
exits `128` with `fatal: pathspec ... is beyond a symbolic link`; it does not
create or stage an artifact. The equivalent read-only check in the linked
primary checkout exits `0` and identifies `.gitignore:6:analysis/aa_*/` as the
matching ignore rule. Both the worktree path and linked target were absent.

To retry, attach an ADB device running exactly `17.3.662804-release`, install
`frida` into the Python interpreter used by `phone_full_capture.py`, re-run
all four preflight commands, and then perform the prescribed scenario captures
and validation without treating an unavailable service as protocol absence.

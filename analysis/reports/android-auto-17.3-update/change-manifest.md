# Change Manifest

This is the frozen publication contract for Tasks 11-13 plus the bounded Task
14 baseline-refresh extension. A later task may modify only a file in its exact
allowed-file set below, and only for the semantic change attached to the cited
change ID. `planned` means accepted for
static publication, not runtime-confirmed. `no canonical change` and
`deferred` rows are retained so closed evidence cannot disappear silently.
When a row spans tasks, a task may touch only the row paths also present in
that task's authoritative exact staging block. This row/allowlist intersection
is the per-file task allocation; a multi-task status never grants either task
the other task's files.

## Canonical change rows

| Change | Accepted evidence | Canonical files | Exact semantic change | Compatibility boundary | Verification command | Status |
|---|---|---|---|---|---|---|
| CHG-VID-8007 | DIR-VID-8007 | `oaa/video/VideoFocusRequestMessage.proto`; `oaa/video/VideoFocusRequestMessage.audit.yaml`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Keep ID/name/schema; publish Phone -> HU. | Direction-only correction; wire schema and ID stay stable. | `rg -n 'Wire msg 0x8007, Phone->HU' oaa/video/VideoFocusRequestMessage.proto && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/video/VideoFocusRequestMessage.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/video/VideoFocusRequestMessage.proto");m=next(x for x in f.message_type if x.name=="VideoFocusRequest");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["focus_mode",2,1,14,".oaa.proto.enums.VideoFocusMode.Enum"],["focus_reason",3,1,14,".oaa.proto.enums.VideoFocusReason.Enum"]]' && rg -n '0x8007.*Phone -> HU' docs/channels/video.md && ! rg -n '0x8007.*HU -> Phone' docs/channels/video.md analysis/reports/proto-verification/video.md` | closed (Tasks 11 and 13) |
| CHG-VID-8008 | DIR-VID-8008 | `oaa/video/VideoFocusIndicationMessage.proto`; `oaa/video/VideoFocusIndicationMessage.audit.yaml`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Keep ID/name/schema; publish HU -> Phone. | Direction-only correction; wire schema and ID stay stable. | `rg -n 'Wire msg 0x8008, HU->Phone' oaa/video/VideoFocusIndicationMessage.proto && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/video/VideoFocusIndicationMessage.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/video/VideoFocusIndicationMessage.proto");m=next(x for x in f.message_type if x.name=="VideoFocusIndication");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["focus_mode",1,1,14,".oaa.proto.enums.VideoFocusMode.Enum"],["unrequested",2,1,8,""]]' && rg -n '0x8008.*HU -> Phone' docs/channels/video.md && ! rg -n '0x8008.*Phone -> HU' docs/channels/video.md analysis/reports/proto-verification/video.md` | applied (Task 11); audit/report synchronized (Task 13) |
| CHG-VID-8009 | DIR-VID-8009 | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/av/AVChannelMessageIdsEnum.audit.yaml`; `oaa/av/UiConfigMessages.proto`; `oaa/av/UiConfigMessages.audit.yaml`; `oaa/video/UpdateUiConfigRequestMessage.proto`; `oaa/video/UpdateUiConfigRequestMessage.audit.yaml`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Name 0x8009 `UPDATE_UI_CONFIG_REQUEST` and publish its field-1 UI-config payload HU -> Phone. | Replaces the historical focus-notification label; no tag/type change. | `rg -n 'UPDATE_UI_CONFIG_REQUEST = 0x8009' oaa/av/AVChannelMessageIdsEnum.proto && rg -n '0x8009.*HU -> Phone' docs/channels/video.md analysis/reports/proto-verification/video.md && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/video/UpdateUiConfigRequestMessage.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/video/UpdateUiConfigRequestMessage.proto");m=next(x for x in f.message_type if x.name=="UpdateUiConfigRequest");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["config",1,1,11,".oaa.proto.data.AdditionalVideoConfig"]]' && ! rg -n 'VIDEO_FOCUS_NOTIFICATION = 0x8009' oaa/av/AVChannelMessageIdsEnum.proto && ! rg -n '0x8009.*Phone -> HU' docs/channels/video.md analysis/reports/proto-verification/video.md` | applied (Task 11); audit/report synchronized (Task 13) |
| CHG-VID-800A | DIR-VID-800A | `oaa/av/UiConfigMessages.proto`; `oaa/video/UpdateUiConfigRequestMessage.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Keep name/payload; publish Phone -> HU. | Direction-only correction; 0x8009 and 0x800A remain the same payload in opposite directions. | `rg -n '0x800A.*UpdateUiConfigRequest.*Phone -> HU' docs/channels/video.md analysis/reports/proto-verification/video.md && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/video/UpdateUiConfigRequestMessage.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/video/UpdateUiConfigRequestMessage.proto");m=next(x for x in f.message_type if x.name=="UpdateUiConfigRequest");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["config",1,1,11,".oaa.proto.data.AdditionalVideoConfig"]]' && ! rg -n '0x800A.*HU -> Phone' docs/channels/video.md analysis/reports/proto-verification/video.md` | applied (Task 11) |
| CHG-VID-800B | DIR-VID-800B | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/av/UiConfigMessages.proto`; `docs/channels/video.md`; `docs/channels/media.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x800B as no-payload-parsed `AUDIO_UNDERFLOW`, HU -> Phone; remove reply/heartbeat claims. | Do not infer an empty protobuf schema merely because the phone callback does not parse a payload. | `rg -n 'AUDIO_UNDERFLOW = 0x800B' oaa/av/AVChannelMessageIdsEnum.proto && rg -n '0x800B.*AudioUnderflow.*HU -> Phone.*no payload parsed' docs/channels/video.md && ! rg -n 'UPDATE_UI_CONFIG_REPLY = 0x800B' oaa/av/AVChannelMessageIdsEnum.proto && ! rg -n '0x800B.*heartbeat' docs/channels/video.md analysis/reports/proto-verification/video.md` | applied (Task 11); audit/report synchronized (Task 13) |
| CHG-VID-800C | DIR-VID-800C | `oaa/av/AVChannelMessageIdsEnum.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x800C as `ACTION_TAKEN`, Phone -> HU, with enum field 1 documented. | No public action enum is added in this release; only the proven wrapper boundary is documented. | `rg -n 'ACTION_TAKEN = 0x800C' oaa/av/AVChannelMessageIdsEnum.proto && rg -n '0x800C.*ActionTaken.*Phone -> HU' docs/channels/video.md analysis/reports/proto-verification/video.md && rg -n '0x800C.*enum field 1' docs/channels/video.md docs/cross-version/video.md && rg -n 'public action enum.*unpublished' docs/channels/video.md docs/cross-version/video.md && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schemas.pb";targets=["oaa/av/AVChannelMessageIdsEnum.proto","oaa/av/UiConfigMessages.proto","oaa/av/AVChannelMediaOptionsMessage.proto","oaa/carcontrol/CarControlMessages.proto","oaa/video/CriticalUiNotification.proto","oaa/video/IntegratedOverlayStartNotification.proto","oaa/video/IntegratedOverlayStopNotification.proto","oaa/video/UpdateUiConfigRequestMessage.proto","oaa/video/VideoFocusIndicationMessage.proto","oaa/video/VideoFocusRequestMessage.proto"];subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),*targets],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());assert {x.name for x in s.file}==set(targets);walk=lambda m:[e.name for e in m.enum_type]+sum((walk(x) for x in m.nested_type),[]);names=[e.name for f in s.file for e in f.enum_type]+sum((walk(m) for f in s.file for m in f.message_type),[]);assert not any("action" in x.casefold() for x in names)' && ! rg -n 'AUDIO_UNDERFLOW = 0x800C' oaa/av/AVChannelMessageIdsEnum.proto` | applied (Task 11) |
| CHG-VID-800D | DIR-VID-800D | `oaa/av/AVChannelMessageIdsEnum.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x800D as `OVERLAY_PARAMETERS`, Phone -> HU, with repeated overlay-options field 1 documented. | Nested overlay-option semantics beyond the proven three-field shape remain unpublished. | `rg -n 'OVERLAY_PARAMETERS = 0x800D' oaa/av/AVChannelMessageIdsEnum.proto && rg -n '0x800D.*OverlayParameters.*Phone -> HU' docs/channels/video.md && rg -n '0x800D.*repeated overlay-options field 1' docs/channels/video.md docs/cross-version/video.md && rg -n 'nested overlay-option semantics.*unpublished' docs/channels/video.md docs/cross-version/video.md && ! rg -n 'ACTION_TAKEN = 0x800D' oaa/av/AVChannelMessageIdsEnum.proto` | applied (Task 11) |
| CHG-VID-800E | DIR-VID-800E | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/video/IntegratedOverlayStartNotification.proto`; `oaa/video/IntegratedOverlayStartNotification.audit.yaml`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x800E as `OVERLAY_START`, HU -> Phone, with int32 display-session ID field 1. | Corrects name/direction only; field tag and type remain stable. | `rg -n 'OVERLAY_START = 0x800E' oaa/av/AVChannelMessageIdsEnum.proto && rg -n 'Wire msg 0x800E, HU->Phone' oaa/video/IntegratedOverlayStartNotification.proto && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/video/IntegratedOverlayStartNotification.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/video/IntegratedOverlayStartNotification.proto");m=next(x for x in f.message_type if x.name=="IntegratedOverlayStartNotification");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["display_session_id",1,1,5,""]]' && rg -n '0x800E.*HU -> Phone' docs/channels/video.md && ! rg -n 'OVERLAY_PARAMETERS = 0x800E' oaa/av/AVChannelMessageIdsEnum.proto` | applied (Task 11); audit/report synchronized (Task 13) |
| CHG-VID-800F | DIR-VID-800F | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/video/IntegratedOverlayStopNotification.proto`; `oaa/video/IntegratedOverlayStopNotification.audit.yaml`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x800F as empty `OVERLAY_STOP`, HU -> Phone. | Corrects name/direction; preserves the empty message. | `rg -n 'OVERLAY_STOP = 0x800F' oaa/av/AVChannelMessageIdsEnum.proto && rg -n 'Wire msg 0x800F, HU->Phone' oaa/video/IntegratedOverlayStopNotification.proto && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/video/IntegratedOverlayStopNotification.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/video/IntegratedOverlayStopNotification.proto");m=next(x for x in f.message_type if x.name=="IntegratedOverlayStopNotification");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[]' && rg -n '0x800F.*OverlayStop.*HU -> Phone.*empty' docs/channels/video.md analysis/reports/proto-verification/video.md && ! rg -n 'OVERLAY_START = 0x800F' oaa/av/AVChannelMessageIdsEnum.proto` | applied (Task 11); audit/report synchronized (Task 13) |
| CHG-VID-8010 | DIR-VID-8010 | `oaa/av/AVChannelMessageIdsEnum.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Remove the unsupported `OVERLAY_STOP` assignment from 0x8010 and leave the slot unnamed/reserved. | Deferred: no name, payload, direction, or later-name shift is permitted. | `python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/av/AVChannelMessageIdsEnum.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/av/AVChannelMessageIdsEnum.proto");m=next(x for x in f.message_type if x.name=="AVChannelMessage");e=next(x for x in m.enum_type if x.name=="Enum");assert all(x.number!=32784 for x in e.value)' && rg -n '0x8010.*reserved' docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md && rg -n '0x8010.*unknown' docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md && rg -n '0x8010.*deferred' docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md && ! rg -n '0x8010.*OverlayStop' docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md` | applied reservation; evidence remains deferred (Task 11) |
| CHG-VID-8011 | DIR-VID-8011 | `oaa/av/AVChannelMessageIdsEnum.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Name 0x8011 `UI_CONFIG_REQUEST` and align docs/report to Phone -> HU. | Existing canonical payload is retained unchanged. | `rg -n 'UI_CONFIG_REQUEST = 0x8011' oaa/av/AVChannelMessageIdsEnum.proto && rg -n '0x8011.*UiConfigRequest.*Phone -> HU' docs/channels/video.md analysis/reports/proto-verification/video.md && rg -n 'optional UiConfigData config = 1' oaa/video/UiConfigRequestMessage.proto && git diff --quiet -- oaa/video/UiConfigRequestMessage.proto && ! rg -n 'OVERLAY_SESSION_UPDATE = 0x8011' oaa/av/AVChannelMessageIdsEnum.proto` | applied (Task 11) |
| CHG-VID-8012 | DIR-VID-8012 | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/av/UiConfigMessages.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Name 0x8012 `UPDATE_HU_UI_CONFIG_RESPONSE` and align docs/report to HU -> Phone. | Existing theming-token-status payload is retained unchanged. | `rg -n 'UPDATE_HU_UI_CONFIG_RESPONSE = 0x8012' oaa/av/AVChannelMessageIdsEnum.proto && rg -n '0x8012.*UpdateHuUiConfigResponse.*HU -> Phone' docs/channels/video.md analysis/reports/proto-verification/video.md && rg -n 'optional ThemingTokensStatus status = 1' oaa/video/UpdateHuUiConfigResponse.proto && git diff --quiet -- oaa/video/UpdateHuUiConfigResponse.proto && ! rg -n 'UPDATE_HU_UI_CONFIG_REQUEST = 0x8012' oaa/av/AVChannelMessageIdsEnum.proto` | applied (Task 11) |
| CHG-VID-8013 | DIR-VID-8013 | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/av/UiConfigMessages.proto`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x8013 as `MEDIA_STATS`, HU -> Phone, and remove the UI-config response assignment. | Existing media-stats schema is unchanged. | `rg -n 'MEDIA_STATS = 0x8013' oaa/av/AVChannelMessageIdsEnum.proto && rg -n '0x8013.*MediaStats.*HU -> Phone' docs/channels/video.md analysis/reports/proto-verification/video.md && git diff --quiet -- oaa/av/AVChannelMediaStatsMessage.proto && ! rg -n 'UPDATE_HU_UI_CONFIG_RESPONSE = 0x8013' oaa/av/AVChannelMessageIdsEnum.proto oaa/av/UiConfigMessages.proto` | applied (Task 11) |
| CHG-VID-8014 | DIR-VID-8014 | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/av/AVChannelMediaOptionsMessage.proto`; `oaa/av/AVChannelMediaOptionsMessage.audit.yaml`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x8014 as `MEDIA_OPTIONS`, Phone -> HU, and add its exact optional proto2 13-field wire shape. | 17.3 proves only tags, labels, and types: nine PingConfiguration messages, three bools, and one uint32; neutral field names do not claim application semantics, which remain unresolved. | `rg -n 'MEDIA_OPTIONS = 0x8014' oaa/av/AVChannelMessageIdsEnum.proto && rg -n '0x8014.*MediaOptions.*Phone -> HU' docs/channels/video.md analysis/reports/proto-verification/video.md && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/av/AVChannelMediaOptionsMessage.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/av/AVChannelMediaOptionsMessage.proto");m=next(x for x in f.message_type if x.name=="AVChannelMediaOptions");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["ping_configuration_1",1,1,11,".oaa.proto.data.PingConfiguration"],["bool_value_2",2,1,8,""],["ping_configuration_3",3,1,11,".oaa.proto.data.PingConfiguration"],["ping_configuration_4",4,1,11,".oaa.proto.data.PingConfiguration"],["ping_configuration_5",5,1,11,".oaa.proto.data.PingConfiguration"],["ping_configuration_6",6,1,11,".oaa.proto.data.PingConfiguration"],["uint32_value_7",7,1,13,""],["ping_configuration_8",8,1,11,".oaa.proto.data.PingConfiguration"],["bool_value_9",9,1,8,""],["ping_configuration_10",10,1,11,".oaa.proto.data.PingConfiguration"],["bool_value_11",11,1,8,""],["ping_configuration_12",12,1,11,".oaa.proto.data.PingConfiguration"],["ping_configuration_13",13,1,11,".oaa.proto.data.PingConfiguration"]];assert f.syntax!="proto3";assert f.package=="oaa.proto.messages";assert [x.name for x in f.message_type]==["AVChannelMediaOptions"];assert not f.enum_type;assert not m.enum_type;assert not m.nested_type' && rg -ni 'field semantics.*unresolved' oaa/av/AVChannelMediaOptionsMessage.proto docs/channels/video.md docs/cross-version/video.md analysis/reports/proto-verification/video.md && ! rg -n 'MEDIA_STATS = 0x8014' oaa/av/AVChannelMessageIdsEnum.proto` | applied schema correction (Task 11 Fix Round 1); audit synchronized (Task 13) |
| CHG-VID-8015 | DIR-VID-8015 | `oaa/av/AVChannelMessageIdsEnum.proto`; `oaa/video/CriticalUiNotification.proto`; `oaa/video/CriticalUiNotification.audit.yaml`; `docs/channels/video.md`; `docs/cross-version/video.md`; `analysis/reports/proto-verification/video.md` | Publish 0x8015 as `CRITICAL_UI_NOTIFICATION`, Phone -> HU; add the proven field-1 critical-UI-focus enum payload. | New optional proto2 payload coverage; no acknowledgement or response is implied. | `rg -n 'CRITICAL_UI_NOTIFICATION = 0x8015' oaa/av/AVChannelMessageIdsEnum.proto && rg -n '0x8015.*CriticalUiNotification.*Phone -> HU' docs/channels/video.md analysis/reports/proto-verification/video.md && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/video/CriticalUiNotification.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/video/CriticalUiNotification.proto");m=next(x for x in f.message_type if x.name=="CriticalUiNotification");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["focus",1,1,14,".oaa.proto.messages.CriticalUiFocus"]];e=next(x for x in f.enum_type if x.name=="CriticalUiFocus");assert [[x.name,x.number] for x in e.value]==[["CRITICAL_UI_FOCUS_UNKNOWN",0],["CRITICAL_UI_FOCUS_PROJECTED",1],["CRITICAL_UI_FOCUS_NATIVE",2]];assert f.syntax!="proto3";assert f.package=="oaa.proto.messages";assert [x.name for x in f.message_type]==["CriticalUiNotification"];assert [x.name for x in f.enum_type]==["CriticalUiFocus"]'` | applied (Task 11); audit/report synchronized (Task 13) |
| CHG-CC-8001 | DIR-CC-8001 | `oaa/carcontrol/CarControlMessages.proto`; `oaa/carcontrol/CarControlMessages.audit.yaml`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish Phone -> HU and phone-owned request correlation. | Direction/ownership correction only. | `rg -n '0x8001.*SetCarPropertyValueRequest.*Phone.*HU' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/carcontrol/CarControlMessages.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/carcontrol/CarControlMessages.proto");m=next(x for x in f.message_type if x.name=="SetCarPropertyValueRequest");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["car_property",1,1,11,".oaa.proto.messages.CarProperty"],["property_value",2,1,11,".oaa.proto.messages.CarPropertyValue"],["request_id",3,1,9,""]]' && rg -n '0x8001.*Phone→HU' analysis/reports/proto-verification/carcontrol.md && ! rg -n '0x8001.*HU.*Phone' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md && ! rg -n '0x8001.*HU→Phone' analysis/reports/proto-verification/carcontrol.md` | applied (Task 11); audit/report synchronized (Task 13) |
| CHG-CC-8002 | DIR-CC-8002 | `oaa/carcontrol/CarControlMessages.proto`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish HU -> Phone response and phone-side UUID matching. | Direction/ownership correction only. | `rg -n '0x8002.*SetCarPropertyValueResponse.*HU.*Phone' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/carcontrol/CarControlMessages.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/carcontrol/CarControlMessages.proto");m=next(x for x in f.message_type if x.name=="SetCarPropertyValueResponse");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["car_property",1,1,11,".oaa.proto.messages.CarProperty"],["status",2,1,14,".oaa.proto.enums.Status.Enum"],["request_id",3,1,9,""],["error_code",4,1,5,""]]' && rg -n '0x8002.*HU→Phone' analysis/reports/proto-verification/carcontrol.md && ! rg -n '0x8002.*Phone.*HU' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md && ! rg -n '0x8002.*Phone→HU' analysis/reports/proto-verification/carcontrol.md` | applied (Task 11) |
| CHG-CC-8003 | DIR-CC-8003 | `oaa/carcontrol/CarControlMessages.proto`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish Phone -> HU and note inbound copies are unexpected. | Direction correction only; no acknowledgement is inferred. | `rg -n '0x8003.*RegisterCarPropertyListenersRequest.*Phone.*HU' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/carcontrol/CarControlMessages.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/carcontrol/CarControlMessages.proto");m=next(x for x in f.message_type if x.name=="RegisterCarPropertyListenersRequest");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["car_properties",1,3,11,".oaa.proto.messages.CarProperty"]]' && rg -n '0x8003.*Phone→HU' analysis/reports/proto-verification/carcontrol.md && rg -n '0x8003.*unexpected' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md && ! rg -n '0x8003.*HU→Phone' analysis/reports/proto-verification/carcontrol.md` | applied (Task 11) |
| CHG-CC-8004 | DIR-CC-8004 | `oaa/carcontrol/CarControlMessages.proto`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish HU -> Phone and phone-side registration-state update. | Direction/ownership correction only. | `rg -n '0x8004.*RegisterCarPropertyListenersResponse.*HU.*Phone' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/carcontrol/CarControlMessages.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/carcontrol/CarControlMessages.proto");m=next(x for x in f.message_type if x.name=="RegisterCarPropertyListenersResponse");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["results",1,3,11,".oaa.proto.messages.SetCarPropertyListenerResult"]]' && rg -n '0x8004.*HU→Phone' analysis/reports/proto-verification/carcontrol.md && ! rg -n '0x8004.*Phone.*HU' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md && ! rg -n '0x8004.*Phone→HU' analysis/reports/proto-verification/carcontrol.md` | applied (Task 11) |
| CHG-CC-8005 | DIR-CC-8005 | `oaa/carcontrol/CarControlMessages.proto`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish HU -> Phone state change delivery. | Direction/ownership correction only. | `rg -n '0x8005.*CarPropertyChangeEvent.*HU.*Phone' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/carcontrol/CarControlMessages.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/carcontrol/CarControlMessages.proto");m=next(x for x in f.message_type if x.name=="CarPropertyChangeEvent");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["car_property",1,1,11,".oaa.proto.messages.CarProperty"],["property_value",2,1,11,".oaa.proto.messages.CarPropertyValue"],["status",3,1,5,""]]' && rg -n '0x8005.*HU→Phone' analysis/reports/proto-verification/carcontrol.md && ! rg -n '0x8005.*Phone.*HU' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md && ! rg -n '0x8005.*Phone→HU' analysis/reports/proto-verification/carcontrol.md` | applied (Task 11) |
| CHG-CC-8006 | DIR-CC-8006 | `oaa/carcontrol/CarControlMessages.proto`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish Phone -> HU and note inbound copies are unexpected. | Direction correction only; no response is inferred. | `rg -n '0x8006.*CarActionNotification.*Phone.*HU' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/carcontrol/CarControlMessages.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/carcontrol/CarControlMessages.proto");m=next(x for x in f.message_type if x.name=="CarActionNotification");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["action",1,1,11,".oaa.proto.messages.CarAction"]]' && rg -n '0x8006.*Phone→HU' analysis/reports/proto-verification/carcontrol.md && rg -n '0x8006.*unexpected' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md && ! rg -n '0x8006.*HU→Phone' analysis/reports/proto-verification/carcontrol.md` | applied (Task 11) |
| CHG-CC-8007 | DIR-CC-8007 | `oaa/carcontrol/CarControlMessages.proto`; `docs/channels/carcontrol.md`; `docs/cross-version/carcontrol.md`; `analysis/reports/proto-verification/carcontrol.md` | Keep ID/name/schema; publish HU -> Phone replacement-style group update. | Direction/ownership correction only. | `rg -n '0x8007.*CarControlGroupUpdate.*HU.*Phone' oaa/carcontrol/CarControlMessages.proto docs/channels/carcontrol.md && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/carcontrol/CarControlMessages.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/carcontrol/CarControlMessages.proto");m=next(x for x in f.message_type if x.name=="CarControlGroupUpdate");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["car_control_group",1,1,11,".oaa.proto.messages.CarControlGroup"]]' && rg -n '0x8007.*HU→Phone' analysis/reports/proto-verification/carcontrol.md && rg -n '0x8007.*replace' docs/channels/carcontrol.md && ! rg -n '0x8007.*Phone→HU' analysis/reports/proto-verification/carcontrol.md` | applied (Task 11) |
| CHG-SEN-8001 | DIR-SEN-8001 | `analysis/reports/proto-verification/sensor.md` | Preserve canonical SensorRequest Phone -> HU; correct only the inverted verification row. | No proto or channel-doc change. | `rg -n 'SensorRequest.*0x8001.*Phone→HU' analysis/reports/proto-verification/sensor.md && ! rg -n 'SensorRequest.*0x8001.*HU→Phone' analysis/reports/proto-verification/sensor.md` | applied report correction (Task 11) |
| CHG-SEN-8002 | DIR-SEN-8002 | `analysis/reports/proto-verification/sensor.md` | Preserve canonical SensorStartResponse HU -> Phone; correct only the inverted verification row. | No proto or channel-doc change. | `rg -n 'SensorStartResponse.*0x8002.*HU→Phone' analysis/reports/proto-verification/sensor.md && ! rg -n 'SensorStartResponse.*0x8002.*Phone→HU' analysis/reports/proto-verification/sensor.md` | applied report correction (Task 11) |
| CHG-SEN-8003 | DIR-SEN-8003 | `analysis/reports/proto-verification/sensor.md` | Preserve canonical SensorEventIndication HU -> Phone; correct only the inverted verification row. | No proto or channel-doc change. | `rg -n 'SensorEventIndication.*0x8003.*HU→Phone' analysis/reports/proto-verification/sensor.md && ! rg -n 'SensorEventIndication.*0x8003.*Phone→HU' analysis/reports/proto-verification/sensor.md` | applied report correction (Task 11) |
| CHG-SEN-8004 | DIR-SEN-8004 | `analysis/reports/proto-verification/sensor.md` | Preserve canonical SensorError HU -> Phone; correct only the inverted verification row. | No proto or channel-doc change. | `rg -n 'SensorError.*0x8004.*HU→Phone' analysis/reports/proto-verification/sensor.md && ! rg -n 'SensorError.*0x8004.*Phone→HU' analysis/reports/proto-verification/sensor.md` | applied report correction (Task 11) |
| CHG-REPORT-RAD-801A | DIR-RAD-801A | `docs/channels/radio.md` | Keep the correct mapping; correct list-notification prose to HU -> Phone. | No radio proto/catalog/report mapping change. | `rg -n '0x801A = RadioProgramListNotification.*HU→Phone' oaa/radio/RadioMessages.proto && rg -n 'RadioProgramListNotification.*HU.*Phone' docs/channels/radio.md && ! rg -n 'RadioProgramListNotification.*Phone.*HU' docs/channels/radio.md && git diff --quiet -- oaa/radio/RadioMessages.proto` | applied prose correction (Task 13) |
| CHG-REPORT-RAD-801B | DIR-RAD-801B | `docs/channels/radio.md` | Keep the correct mapping; correct program-info workflow prose to HU -> Phone. | No radio proto/catalog/report mapping change. | `rg -n '0x801B = RadioProgramInfoNotification.*HU→Phone' oaa/radio/RadioMessages.proto && rg -n 'RadioProgramInfoNotification.*HU.*Phone' docs/channels/radio.md && ! rg -n 'RadioProgramInfoNotification.*Phone.*HU' docs/channels/radio.md && git diff --quiet -- oaa/radio/RadioMessages.proto` | applied prose correction (Task 13) |
| CHG-REPORT-RAD-801C | DIR-RAD-801C | `docs/channels/radio.md` | Keep the correct mapping; correct mute-request prose to Phone -> HU. | No radio proto/catalog/report mapping change. | `rg -n '0x801C = RadioMuteRequest.*Phone→HU' oaa/radio/RadioMessages.proto && rg -n 'RadioMuteRequest.*Phone.*HU' docs/channels/radio.md && ! rg -n 'RadioMuteRequest.*HU.*Phone' docs/channels/radio.md && git diff --quiet -- oaa/radio/RadioMessages.proto` | applied prose correction (Task 13) |
| CHG-REPORT-RAD-801D | DIR-RAD-801D | `docs/channels/radio.md` | Keep the correct mapping; correct mute-response prose to HU -> Phone. | No radio proto/catalog/report mapping change. | `rg -n '0x801D = RadioMuteResponse.*HU→Phone' oaa/radio/RadioMessages.proto && rg -n 'RadioMuteResponse.*HU.*Phone' docs/channels/radio.md && ! rg -n 'RadioMuteResponse.*Phone.*HU' docs/channels/radio.md && git diff --quiet -- oaa/radio/RadioMessages.proto` | applied prose correction (Task 13) |
| CHG-REPORT-RAD-801E | DIR-RAD-801E | `docs/channels/radio.md` | Keep the correct mapping; correct tune-request prose to Phone -> HU. | No radio proto/catalog/report mapping change. | `rg -n '0x801E = RadioTuneRequest.*Phone→HU' oaa/radio/RadioMessages.proto && rg -n 'RadioTuneRequest.*Phone.*HU' docs/channels/radio.md && ! rg -n 'RadioTuneRequest.*HU.*Phone' docs/channels/radio.md && git diff --quiet -- oaa/radio/RadioMessages.proto` | applied prose correction (Task 13) |
| CHG-REPORT-RAD-801F | DIR-RAD-801F | `docs/channels/radio.md` | Keep the correct mapping; correct tune-response/ownership prose to HU -> Phone. | No radio proto/catalog/report mapping change. | `rg -n '0x801F = RadioTuneResponse.*HU→Phone' oaa/radio/RadioMessages.proto && rg -n 'RadioTuneResponse.*HU.*Phone' docs/channels/radio.md && ! rg -n 'RadioTuneResponse.*Phone.*HU' docs/channels/radio.md && git diff --quiet -- oaa/radio/RadioMessages.proto` | applied prose correction (Task 13) |
| CHG-REPORT-RAD-8020 | DIR-RAD-8020 | `docs/channels/radio.md` | Keep the correct mapping; correct favorite-list workflow prose to HU -> Phone. | No radio proto/catalog/report mapping change. | `rg -n '0x8020 = RadioFavoriteListNotification.*HU→Phone' oaa/radio/RadioMessages.proto && rg -n 'RadioFavoriteListNotification.*HU.*Phone' docs/channels/radio.md && ! rg -n 'RadioFavoriteListNotification.*Phone.*HU' docs/channels/radio.md && git diff --quiet -- oaa/radio/RadioMessages.proto` | applied prose correction (Task 13) |
| CHG-REPORT-RAD-8021 | DIR-RAD-8021 | `docs/channels/radio.md` | Keep the correct mapping; correct favorite-toggle prose to Phone -> HU. | No radio proto/catalog/report mapping change. | `rg -n '0x8021 = RadioFavoriteToggleRequest.*Phone→HU' oaa/radio/RadioMessages.proto && rg -n 'RadioFavoriteToggleRequest.*Phone.*HU' docs/channels/radio.md && ! rg -n 'RadioFavoriteToggleRequest.*HU.*Phone' docs/channels/radio.md && git diff --quiet -- oaa/radio/RadioMessages.proto` | applied prose correction (Task 13) |
| CHG-REPORT-RAD-8022 | DIR-RAD-8022 | `docs/channels/radio.md` | Keep the correct mapping; correct tune-direction ownership to Phone -> HU. | No radio proto/catalog/report mapping change. | `rg -n '0x8022 = RadioTuneDirectionRequest.*Phone→HU' oaa/radio/RadioMessages.proto && rg -n 'RadioTuneDirectionRequest.*Phone.*HU' docs/channels/radio.md && ! rg -n 'RadioTuneDirectionRequest.*HU.*Phone' docs/channels/radio.md && git diff --quiet -- oaa/radio/RadioMessages.proto` | applied prose correction (Task 13) |
| CHG-REPORT-RAD-8023 | DIR-RAD-8023 | none | Explicit no canonical change: retain ID, name, one-string schema, direction, and history. | Mapping is already correct. | `rg -n '0x8023 = RadioSearchRequest.*Phone→HU' oaa/radio/RadioMessages.proto && rg -n 'RadioSearchRequest.*0x8023.*Phone.*HU' docs/channels/radio.md && python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/radio/RadioMessages.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/radio/RadioMessages.proto");m=next(x for x in f.message_type if x.name=="RadioSearchRequest");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["query",1,1,9,""]]' && git diff --quiet -- oaa/radio/RadioMessages.proto` | no canonical change |
| CHG-ID-AV-F6 | ID-AV-F6 | `oaa/av/AVChannelData.proto`; `oaa/av/AVChannelData.audit.yaml`; `docs/channels/display-routing.md`; `docs/channels/architecture.md`; `docs/interactions/03-service-discovery.md`; `docs/channel-map.md`; `analysis/reports/multi-display/prodigy-maintainer-handoff.md` | Rename AV field 6 from `channel_id` to `display_id`; document logical display identity. | Breaking generated-API rename only; tag 6 and uint32 wire type stay stable. | `python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/av/AVChannelData.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/av/AVChannelData.proto");m=next(x for x in f.message_type if x.name=="AVChannel");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field if x.number==6]==[["display_id",6,1,13,""]]' && ! rg -n 'channel_id[[:space:]]*=[[:space:]]*6' oaa/av/AVChannelData.proto && rg -n 'optional[[:space:]]+uint32[[:space:]]+display_id[[:space:]]*=[[:space:]]*6' docs/interactions/03-service-discovery.md && test "$(rg -c --include-zero '^[[:space:]]*channel_id[[:space:]]*:' docs/interactions/03-service-discovery.md)" -eq 1 && rg -n '^[[:space:]]*channel_id[[:space:]]*:[[:space:]]*3[[:space:]/;].*Transport video channel' docs/interactions/03-service-discovery.md && rg -n '^[[:space:]]*display_id[[:space:]]*:[[:space:]]*0[[:space:]/;].*Logical MAIN display identity' docs/interactions/03-service-discovery.md && rg -n 'ChannelDescriptor\.channel_id.*transport channel ID' docs/interactions/03-service-discovery.md && rg -n 'AVChannel\.display_id.*field 6.*joins' docs/interactions/03-service-discovery.md && rg -n 'InputChannelConfig\.display_id.*field 5' docs/interactions/03-service-discovery.md && rg -n 'breaking generated API rename' analysis/reports/multi-display/prodigy-maintainer-handoff.md` | applied canonical/docs/audit (Task 12); active-guide scope correction applied (Task 12 Fix Round 1); formatting-independent gate hardening applied (Task 12 Fix Round 2); comment-independent cardinality hardening applied (Task 12 Fix Round 3); final audit/report synchronized (Task 13) |
| CHG-ID-INPUT-F5 | ID-INPUT-F5 | `oaa/input/InputChannelConfigData.proto`; `oaa/input/InputChannelConfigData.audit.yaml`; `docs/channels/display-routing.md`; `docs/channels/architecture.md`; `docs/channel-map.md`; `analysis/reports/multi-display/prodigy-maintainer-handoff.md` | Preserve field-5 `display_id`; document it as the AV field-6 reference, distinct from transport channel ID and service type 8. | No tag/type/API rename. | `rg -n 'optional uint32 display_id = 5' oaa/input/InputChannelConfigData.proto && rg -n 'AVChannel.*field 6' docs/channels/display-routing.md docs/channels/architecture.md analysis/reports/multi-display/prodigy-maintainer-handoff.md && ! rg -n 'channel_id = 5' oaa/input/InputChannelConfigData.proto` | applied documentation/audit clarification (Task 12); final report synchronized (Task 13) |
| CHG-ID-CD-F16 | ID-CD-F16 | `oaa/control/ChannelDescriptorData.proto`; `oaa/control/ChannelDescriptorData.audit.yaml`; `docs/channels/media.md`; `docs/channels/architecture.md`; `docs/channel-map.md`; `analysis/reports/proto-verification/sdp.md`; `analysis/reports/proto-verification/sdp-progress.md` | Publish field 16 as the 17.3 CarLocalMedia marker/service type 20. | Historical 16.2 `generic_notification` meaning is insufficient evidence; do not publish it as an alias or semantic reuse. | `rg -n 'car_local_media_channel = 16' oaa/control/ChannelDescriptorData.proto && rg -n 'service type 20' docs/channels/media.md && rg -n 'service type 20' analysis/reports/proto-verification/sdp.md && rg -n 'service type 20' analysis/reports/proto-verification/sdp-progress.md && ! rg -n '16=generic_notification' oaa/control/ChannelDescriptorData.proto` | applied canonical/docs/audit (Task 12); SDP report synchronized (Task 13) |
| CHG-ID-CD-F17 | ID-CD-F17 | `oaa/control/ChannelDescriptorData.proto`; `oaa/control/ChannelDescriptorData.audit.yaml`; `docs/channels/media.md`; `docs/channels/architecture.md`; `docs/channel-map.md`; `analysis/reports/proto-verification/sdp.md`; `analysis/reports/proto-verification/sdp-progress.md` | Publish field 17 as the 17.3 BufferedMedia marker/service type 21. | Historical 16.2 `voice` meaning is insufficient evidence; do not publish it as an alias or semantic reuse. | `rg -n 'buffered_media_channel = 17' oaa/control/ChannelDescriptorData.proto && rg -n 'service type 21' docs/channels/media.md && rg -n 'service type 21' analysis/reports/proto-verification/sdp.md && rg -n 'service type 21' analysis/reports/proto-verification/sdp-progress.md && ! rg -n '17=voice' oaa/control/ChannelDescriptorData.proto` | applied canonical/docs/audit (Task 12); SDP report synchronized (Task 13) |
| CHG-ID-CD-F18 | ID-CD-F18 | `oaa/control/ChannelDescriptorData.proto`; `oaa/control/ChannelDescriptorData.audit.yaml`; `docs/channels/carintent.md`; `docs/channels/architecture.md`; `docs/channel-map.md`; `analysis/reports/proto-verification/sdp.md`; `analysis/reports/proto-verification/sdp-progress.md` | Publish optional field 18 as the CarIntent marker/service type 22. | Compatible optional addition in 17.3 relative to the available 16.2 descriptor ending at field 17. | `rg -n 'car_intent_channel = 18' oaa/control/ChannelDescriptorData.proto && rg -n 'compatible.*17.3.*16.2' docs/channels/carintent.md && rg -n 'compatible.*17.3.*16.2' analysis/reports/proto-verification/sdp.md && rg -n 'compatible.*17.3.*16.2' analysis/reports/proto-verification/sdp-progress.md && rg -n 'service type 22' docs/channels/carintent.md analysis/reports/proto-verification/sdp.md analysis/reports/proto-verification/sdp-progress.md` | applied canonical/docs/audit (Task 12); SDP report synchronized (Task 13) |
| CHG-CI-DESCRIPTOR | SVC-CI-DESCRIPTOR | `oaa/control/ChannelDescriptorData.proto`; `docs/channels/carintent.md`; `docs/channels/architecture.md`; `docs/channel-map.md` | Document field 18, bit 0x20000, and GAL service type 22. | Static descriptor evidence only; no framed discovery capture. | `rg -n 'field 18.*0x20000.*service type 22' docs/channels/carintent.md && rg -n 'car_intent_channel = 18' oaa/control/ChannelDescriptorData.proto` | applied (Task 12) |
| CHG-CI-ENDPOINT | SVC-CI-ENDPOINT | `docs/channels/carintent.md` | Document the incoming HU -> Phone parse, log, and callback chain. | Do not add an acknowledgement, response, or runtime-delivery claim. | `rg -n 'HU -> Phone.*parse.*log.*callback' docs/channels/carintent.md && rg -ni 'no acknowledgement.*no response.*runtime-unverified' docs/channels/carintent.md && ! rg -ni 'runtime-confirmed delivery' docs/channels/carintent.md` | applied static boundary (Task 12) |
| CHG-CI-ID | SVC-CI-ID | `docs/channels/carintent.md` | Explicit no raw-ID assignment: publish the raw message ID as unknown. | Deferred; conventional 0x8001 is forbidden. | `rg -n 'raw message ID.*unknown' docs/channels/carintent.md && ! rg -n 'CarIntent.*0x8001' docs/channels/carintent.md && ! rg -n '0x8001.*CarIntent' docs/channels/carintent.md` | deferred boundary documented (Task 12) |
| CHG-CI-SCHEMA | SVC-CI-SCHEMA | `oaa/carintent/CarIntentMessage.proto`; `oaa/carintent/CarIntentMessage.audit.yaml`; `docs/channels/carintent.md` | Add a proto2 payload containing only optional string field 2 and document its HU -> Phone use. | Field 1, intent-type enum, acknowledgement, and response are forbidden. | `python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/carintent/CarIntentMessage.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/carintent/CarIntentMessage.proto");m=next(x for x in f.message_type if x.name=="CarIntentMessage");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["metadata",2,1,9,""]];assert f.syntax!="proto3";assert f.package=="oaa.proto.messages";assert [x.name for x in f.message_type]==["CarIntentMessage"];assert not f.enum_type;assert not m.enum_type;assert not m.nested_type' && rg -n 'HU -> Phone.*only.*field 2' docs/channels/carintent.md` | applied proto/docs/audit (Task 12); final audit synchronized (Task 13) |
| CHG-CI-GATE | SVC-CI-GATE | `docs/channels/carintent.md` | Document the false named-flag default separately from the actual field-18 descriptor-presence factory gate. | Do not claim the named flag controls factory construction or that production activation was observed. | `rg -n 'AdasRouteInfoFeature__car_intent_enabled.*default.*false' docs/channels/carintent.md && rg -n 'descriptor.*0x20000.*actual.*gate' docs/channels/carintent.md && ! rg -n 'feature flag controls.*factory' docs/channels/carintent.md` | applied static boundary (Task 12) |
| CHG-CLM-STATE5 | SVC-CLM-STATE5 | `oaa/media/CarLocalMediaPlaybackStatusMessage.proto`; `oaa/media/CarLocalMediaPlaybackStatusMessage.audit.yaml`; `docs/channels/media.md` | Keep wire value 5 explicitly unnamed/unknown; publish no semantic state label. | Deferred until runtime or unobfuscated source resolves the value; BufferedMedia enum names are not transferable. | `python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/media/CarLocalMediaPlaybackStatusMessage.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/media/CarLocalMediaPlaybackStatusMessage.proto");e=next(x for x in f.enum_type if x.name=="CarLocalMediaPlaybackState");assert [[x.name,x.number] for x in e.value]==[["CAR_LOCAL_PLAYBACK_STOPPED",1],["CAR_LOCAL_PLAYBACK_PLAYING",2],["CAR_LOCAL_PLAYBACK_PAUSED",3],["CAR_LOCAL_PLAYBACK_ERROR",4],["CAR_LOCAL_PLAYBACK_UNKNOWN_5",5]]' && rg -n 'numeric value 5.*unknown.*deferred' docs/channels/media.md && ! rg -n 'needs wire capture' oaa/media/CarLocalMediaPlaybackStatusMessage.proto docs/channels/media.md` | deferred boundary documented in proto/docs/audit (Task 12); final audit synchronized (Task 13) |
| CHG-CLM-FLOW | SVC-CLM-FLOW | `docs/channels/media.md`; `docs/channel-map.md`; `analysis/reports/proto-verification/media.md`; `analysis/reports/proto-verification/PROGRESS.md` | Publish service type 20: 0x8001/0x8002 HU -> Phone and 0x8003 Phone -> HU, using the three existing payloads. | Static endpoint flow only; no acknowledgement, runtime activation, frame, or callback-delivery claim. The metadata and request protos already carry the proven directions and require no canonical change. | `for target in docs/channels/media.md analysis/reports/proto-verification/media.md analysis/reports/proto-verification/PROGRESS.md; do if ! rg -n 'service type 20' "$target"; then exit 1; fi; if ! rg -n -e '0x8001.*CarLocalMediaPlaybackStatus.*HU ?[-→]>? ?Phone' -e 'CarLocalMediaPlaybackStatus.*0x8001.*HU ?[-→]>? ?Phone' "$target"; then exit 1; fi; if ! rg -n -e '0x8002.*CarLocalMediaPlaybackMetadata.*HU ?[-→]>? ?Phone' -e 'CarLocalMediaPlaybackMetadata.*0x8002.*HU ?[-→]>? ?Phone' "$target"; then exit 1; fi; if ! rg -n -e '0x8003.*CarLocalMediaPlaybackRequest.*Phone ?[-→]>? ?HU' -e 'CarLocalMediaPlaybackRequest.*0x8003.*Phone ?[-→]>? ?HU' "$target"; then exit 1; fi; if rg -n -e '0x8001.*CarLocalMediaPlaybackStatus.*Phone ?[-→]>? ?HU' -e 'CarLocalMediaPlaybackStatus.*0x8001.*Phone ?[-→]>? ?HU' -e '0x8002.*CarLocalMediaPlaybackMetadata.*Phone ?[-→]>? ?HU' -e 'CarLocalMediaPlaybackMetadata.*0x8002.*Phone ?[-→]>? ?HU' -e '0x8003.*CarLocalMediaPlaybackRequest.*HU ?[-→]>? ?Phone' -e 'CarLocalMediaPlaybackRequest.*0x8003.*HU ?[-→]>? ?Phone' "$target"; then exit 1; fi; done && rg -n 'Sent by HU to phone' oaa/media/CarLocalMediaPlaybackMetadataMessage.proto && rg -n 'Phone -> HU' oaa/media/CarLocalMediaPlaybackRequestMessage.proto` | canonical docs applied (Task 12); media/PROGRESS reports synchronized (Task 13); metadata/request protos no change |
| CHG-BUF-DESCRIPTOR | SVC-BUF-DESCRIPTOR | `oaa/control/ChannelDescriptorData.proto`; `oaa/media/BufferedMediaSinkMessage.proto`; `docs/channels/media.md`; `docs/channels/architecture.md`; `docs/channel-map.md` | Document field 17, bit 0x10000, and GAL service type 21. | Preserve the insufficient-evidence boundary for historical field-17 semantics. | `rg -n 'buffered_media_channel = 17' oaa/control/ChannelDescriptorData.proto && rg -n '0x10000.*service type 21' oaa/media/BufferedMediaSinkMessage.proto docs/channels/media.md && ! rg -n 'field 17.*voice alias' docs/channels/media.md` | applied static boundary (Task 12) |
| CHG-BUF-ENDPOINT | SVC-BUF-ENDPOINT | `oaa/media/BufferedMediaSinkMessage.proto`; `docs/channels/media.md`; `analysis/reports/proto-verification/media.md`; `analysis/reports/proto-verification/PROGRESS.md` | Replace the universal discard-only claim with the bounded 17.3 incoming ID-4 parse/consume branch, HU -> Phone. | This does not establish a response, completed transfer, runtime activation, or downstream media operation. | `rg -n 'ID 4.*HU -> Phone.*parse.*consume' oaa/media/BufferedMediaSinkMessage.proto && for target in docs/channels/media.md analysis/reports/proto-verification/media.md analysis/reports/proto-verification/PROGRESS.md; do if ! rg -n 'ID 4.*HU -> Phone.*parse.*consume' "$target"; then exit 1; fi; if ! rg -n -e 'does not prove.*response.*completed transfer.*runtime-unverified' -e 'does not establish.*response.*completed transfer.*runtime-unverified' "$target"; then exit 1; fi; done && ! rg -n '17.3.*discards all data' oaa/media/BufferedMediaSinkMessage.proto docs/channels/media.md` | canonical/proto/docs applied (Task 12); media/PROGRESS reports synchronized (Task 13) |
| CHG-BUF-IDS | SVC-BUF-IDS | `oaa/media/BufferedMediaSinkMessage.proto`; `docs/channels/media.md`; `analysis/reports/proto-verification/media.md` | Publish only incoming raw ID 4; explicitly leave IDs 1-3 and every outbound path unknown. | Validator range acceptance is not endpoint meaning or send evidence. | `for target in oaa/media/BufferedMediaSinkMessage.proto docs/channels/media.md analysis/reports/proto-verification/media.md; do if ! rg -n 'raw ID 4.*HU -> Phone' "$target"; then exit 1; fi; if ! rg -n 'IDs 1-3.*unknown' "$target"; then exit 1; fi; done && rg -n 'outbound.*unknown' docs/channels/media.md && rg -n 'outbound.*unknown' analysis/reports/proto-verification/media.md` | ID 4 canonical/docs applied and IDs 1-3/outbound deferred (Task 12); media report synchronized (Task 13) |
| CHG-BUF-SCHEMAS | SVC-BUF-SCHEMAS | `oaa/media/BufferedMediaSinkMessage.proto`; `oaa/media/BufferedMediaSinkMessage.audit.yaml`; `docs/channels/media.md`; `analysis/reports/proto-verification/media.md` | Add only the six optional ID-4 fields and state enum values 0-4 proven by the parser. | No URL, request/response, lifecycle, transport/data-plane, or session semantics beyond the six consumed fields. | `python3 -c 'from google.protobuf import descriptor_pb2 as d;import atexit,pathlib,subprocess,tempfile;t=tempfile.TemporaryDirectory();atexit.register(t.cleanup);p=pathlib.Path(t.name)/"schema.pb";subprocess.run(["protoc","--proto_path=.","--descriptor_set_out="+str(p),"oaa/media/BufferedMediaSinkMessage.proto"],check=True);s=d.FileDescriptorSet();s.ParseFromString(p.read_bytes());f=next(x for x in s.file if x.name=="oaa/media/BufferedMediaSinkMessage.proto");m=next(x for x in f.message_type if x.name=="BufferedMediaSinkMessage");assert [[x.name,x.number,x.label,x.type,x.type_name] for x in m.field]==[["session_id",1,1,5,""],["uid",2,1,4,""],["current_position_ms",3,1,4,""],["state",4,1,14,".oaa.proto.messages.BufferedMediaState"],["buffered_position_ms",5,1,4,""],["content_duration_ms",6,1,4,""]];e=next(x for x in f.enum_type if x.name=="BufferedMediaState");assert [[x.name,x.number] for x in e.value]==[["BUFFERED_MEDIA_STATE_UNKNOWN",0],["BUFFERED_MEDIA_STATE_PLAYING",1],["BUFFERED_MEDIA_STATE_PAUSED",2],["BUFFERED_MEDIA_STATE_STOPPED",3],["BUFFERED_MEDIA_STATE_BUFFERING",4]];assert f.syntax!="proto3";assert f.package=="oaa.proto.messages";assert [x.name for x in f.message_type]==["BufferedMediaSinkMessage"];assert [x.name for x in f.enum_type]==["BufferedMediaState"]' && for target in oaa/media/BufferedMediaSinkMessage.proto docs/channels/media.md analysis/reports/proto-verification/media.md; do if ! rg -n 'IDs 1-3.*unknown' "$target"; then exit 1; fi; done && rg -n 'outbound.*unknown' docs/channels/media.md && rg -n 'outbound.*unknown' analysis/reports/proto-verification/media.md` | proto/docs applied (Task 12); BufferedMedia audit and media report synchronized (Task 13) |
| CHG-BUF-GATE | SVC-BUF-GATE | `oaa/media/BufferedMediaSinkMessage.proto`; `docs/channels/media.md`; `docs/channels/architecture.md` | Document the distinct magic-value construction, descriptor-presence, registration, endpoint attachment, and worker-start gates. | Defaults/branches are static; do not claim production enablement, live descriptor advertisement, open endpoint, or running worker. | `rg -n '834952858.*construction' oaa/media/BufferedMediaSinkMessage.proto docs/channels/media.md && rg -n '0x10000.*descriptor' docs/channels/media.md docs/channels/architecture.md && rg -n 'registration.*endpoint attachment.*worker start' docs/channels/media.md docs/channels/architecture.md && rg -n 'BUFFERED_MEDIA_WORKER.*runtime-unverified' docs/channels/media.md && ! rg -n 'enabled in production' docs/channels/media.md docs/channels/architecture.md` | applied static boundary (Task 12) |
| CHG-BASELINE-ADDITIONAL-VIDEO | historical canonical normalization | `oaa/video/AdditionalVideoConfigData.proto`; `oaa/video/AdditionalVideoConfigData.audit.yaml`; four converted-scenario normalized baselines listed below | Refresh `min_resolution`/`max_resolution`/`preferred_resolution` to the canonical `display_insets`/`field_2_insets`/`field_3_insets` rendering introduced by `8a0861a`. | Fields 1-3 remain length-delimited messages whose four child fields remain uint32 tags 1-4; this is normalized schema naming/semantics, not capture-byte mutation. | `rg -n -e 'display_insets = 1' -e 'field_2_insets = 2' -e 'field_3_insets = 3' oaa/video/AdditionalVideoConfigData.proto && ! rg -n -e 'min_resolution' -e 'max_resolution' -e 'preferred_resolution' analysis/baselines/non_media/general.normalized.json analysis/baselines/non_media/idle-baseline.normalized.json analysis/baselines/non_media/music-playback.normalized.json analysis/baselines/non_media/active-navigation.normalized.json` | applied baseline refresh (Task 14) |
| CHG-BASELINE-NAV-TYPE | historical canonical normalization | `oaa/navigation/NavigationChannelData.proto`; `oaa/navigation/NavigationChannelData.audit.yaml`; all five normalized baselines listed below | Render NavigationChannel field 2 numeric value 1 as canonical enum `TURN_BY_TURN`, from `72ed02c`. | Field 2 remains protobuf varint tag 2; int32-to-enum changes the decoded label, not captured bytes. | `rg -n 'required enums.NavigationType.Enum type = 2' oaa/navigation/NavigationChannelData.proto && python3 -c 'import pathlib;ps=list(pathlib.Path("analysis/baselines/non_media").glob("*.normalized.json"));assert sum("\"type\": \"TURN_BY_TURN\"" in p.read_text() for p in ps)==5'` | applied baseline refresh (Task 14) |
| CHG-BASELINE-SENSOR-TYPE | historical canonical normalization | `oaa/sensor/SensorChannelConfigData.proto`; `oaa/sensor/SensorChannelConfigData.audit.yaml`; all five normalized baselines listed below | Refresh stale SensorTypeEntry field key `type` to canonical `sensor_type`; `f494172` introduced that spelling and `72ed02c` added the 17.3 required-field proof. | Enum field 1 stays varint tag 1; optional-to-required validation and generated-name correction do not alter the captured encoding. | `rg -n 'required enums.SensorType.Enum sensor_type = 1' oaa/sensor/SensorChannelConfigData.proto && python3 -c 'import pathlib;ps=list(pathlib.Path("analysis/baselines/non_media").glob("*.normalized.json"));assert sum("\"sensor_type\":" in p.read_text() for p in ps)==5'` | applied baseline refresh (Task 14) |
| CHG-BASELINE-INPUT-KEYCODES | historical canonical normalization | `oaa/input/InputBindingRequestMessage.proto`; `oaa/input/InputBindingRequestMessage.audit.yaml`; four converted-scenario normalized baselines listed below | Refresh input-binding request field key `scan_codes` to canonical `keycodes`, selected by the service-aware resolver in `1340b0b`. | Both legacy and canonical views use repeated packed int32 field 1; only normalized API identity changes. | `rg -n 'repeated int32 keycodes = 1' oaa/input/InputBindingRequestMessage.proto && ! rg -n '"scan_codes":' analysis/baselines/non_media/general.normalized.json analysis/baselines/non_media/idle-baseline.normalized.json analysis/baselines/non_media/music-playback.normalized.json analysis/baselines/non_media/active-navigation.normalized.json` | applied baseline refresh (Task 14) |
| CHG-BASELINE-NAV-STEP-DISTANCE | historical canonical normalization | `oaa/navigation/NavigationTurnEventMessage.proto`; `oaa/navigation/NavigationTurnEventMessage.audit.yaml`; `general` and `active-navigation` normalized baselines | Refresh NavigationNextTurnDistanceEvent field 1 from stale `remaining_distance` to source-proven `step_distance`, introduced by `72ed02c`. | Field 1 stays a length-delimited message and the captured child remains NavigationTurnDistance at child tag 1; this reclassifies the same bytes. | `rg -n 'NavigationStepDistance step_distance = 1' oaa/navigation/NavigationTurnEventMessage.proto && ! rg -n '"remaining_distance":' analysis/baselines/non_media/general.normalized.json analysis/baselines/non_media/active-navigation.normalized.json` | applied baseline refresh (Task 14) |
| CHG-BASELINE-INPUT-BINDING | historical canonical normalization | `analysis/tools/proto_stream_validator/message_map.py`; `oaa/input/InputBindingRequestMessage.proto`; `oaa/input/InputBindingResponseMessage.proto`; their audit sidecars; four converted-scenario normalized baselines listed below | Refresh `BindingRequest`/`BindingResponse` identities to `InputBindingRequest`/`InputBindingResponse` and render response status as its canonical int32 value, following `1340b0b`. | Request remains packed int32 tag 1; response remains varint tag 1. Message/API names and enum-vs-int presentation change without changing capture bytes. | `rg -n 'input_source.*0x8002.*InputBindingRequest' analysis/tools/proto_stream_validator/message_map.py && rg -n 'input_source.*0x8003.*InputBindingResponse' analysis/tools/proto_stream_validator/message_map.py && ! rg -n -e 'oaa.proto.messages.BindingRequest' -e 'oaa.proto.messages.BindingResponse' analysis/baselines/non_media/general.normalized.json analysis/baselines/non_media/idle-baseline.normalized.json analysis/baselines/non_media/music-playback.normalized.json analysis/baselines/non_media/active-navigation.normalized.json` | applied baseline refresh (Task 14) |
| CHG-BASELINE-BT-STATUS | historical canonical normalization | `oaa/bluetooth/BluetoothPairingResponseMessage.proto`; `oaa/bluetooth/BluetoothPairingResponseMessage.audit.yaml`; `2026-02-28-s25-cleanbuild` normalized baseline | Render BluetoothPairingResponse status value 1 as shared enum `UNSOLICITED_MESSAGE`, corrected by `1340b0b`. | Field 1 remains a varint at tag 1; int32-to-enum changes normalized display only. | `rg -n 'required enums.Status.Enum status = 1' oaa/bluetooth/BluetoothPairingResponseMessage.proto && rg -n '"status": "UNSOLICITED_MESSAGE"' analysis/baselines/non_media/2026-02-28-s25-cleanbuild.normalized.json` | applied baseline refresh (Task 14) |
| CHG-REPORT-RT-ENV | RT-ENV | none | Explicit no canonical change: runtime environment validation was unavailable. | No device/version or capture-dependency claim can be promoted. | `rg -n -P '^\x7c RT-ENV \x7c.*\x7c runtime-unverified \x7c.*no ADB device was available.*\x7c runtime-unverified: no ADB device available during execution;.*frida.*\x7c$' analysis/reports/android-auto-17.3-update/runtime-validation.md` | runtime-unverified |
| CHG-REPORT-RT-VIDEO-FOCUS | RT-VIDEO-FOCUS | none | Explicit no canonical change: no framed video-focus traffic was captured. | Static direction remains static, not runtime-confirmed. | `rg -n -P '^\x7c RT-VIDEO-FOCUS \x7c.*aa-17\.3-video-focus-ui.*\x7c runtime-unverified \x7c No capture artifact exists;.*\x7c runtime-unverified: no ADB device available during execution \x7c$' analysis/reports/android-auto-17.3-update/runtime-validation.md` | runtime-unverified |
| CHG-REPORT-RT-VIDEO-UI | RT-VIDEO-UI | none | Explicit no canonical change: no framed video-UI transition was captured. | Static UI/overlay direction remains static, not runtime-confirmed. | `rg -n -P '^\x7c RT-VIDEO-UI \x7c.*day/night or blended-UI transition.*aa-17\.3-video-focus-ui.*\x7c runtime-unverified \x7c No capture artifact exists;.*\x7c runtime-unverified: no ADB device available during execution \x7c$' analysis/reports/android-auto-17.3-update/runtime-validation.md` | runtime-unverified |
| CHG-REPORT-RT-RADIO | RT-RADIO | none | Explicit no canonical change: no runtime radio activation or traffic was observed. | Static radio mappings are not runtime-confirmed. | `rg -n -P '^\x7c RT-RADIO \x7c.*radio service activation.*aa-17\.3-radio.*\x7c runtime-unverified \x7c No capture artifact exists;.*\x7c runtime-unverified: no ADB device available during execution \x7c$' analysis/reports/android-auto-17.3-update/runtime-validation.md` | runtime-unverified |
| CHG-REPORT-RT-CARCONTROL | RT-CARCONTROL | none | Explicit no canonical change: no runtime car-control activation or traffic was observed. | Static car-control directions are not runtime-confirmed. | `rg -n -P '^\x7c RT-CARCONTROL \x7c.*car-control service activation.*aa-17\.3-car-control.*\x7c runtime-unverified \x7c No capture artifact exists;.*\x7c runtime-unverified: no ADB device available during execution \x7c$' analysis/reports/android-auto-17.3-update/runtime-validation.md` | runtime-unverified |
| CHG-REPORT-RT-MULTIDISPLAY | RT-MULTIDISPLAY | none | Explicit no canonical change: no simultaneous multi-display discovery, streams, or focus were captured. | Static logical-display construction does not prove runtime concurrency. | `rg -n -P '^\x7c RT-MULTIDISPLAY \x7c.*MAIN, CLUSTER, and AUXILIARY.*aa-17\.3-multi-display.*\x7c runtime-unverified \x7c No capture artifact exists;.*\x7c runtime-unverified: no ADB device available during execution \x7c$' analysis/reports/android-auto-17.3-update/runtime-validation.md` | runtime-unverified |

## Task 14 baseline refresh

Task 14 found that all five committed non-media baselines predated accepted
canonical decoder names. The validator first regenerated candidates under
`/tmp`, the complete old-to-candidate diff was classified against this closed
nine-group allowlist, and only then were the tracked baselines regenerated with
`--bless --reason`. No capture JSONL was edited.

| Drift group | Manifest mapping | Origin | Normalized change | Wire-invariance boundary | Diff issues |
|---|---|---|---|---|---:|
| AV display identity | CHG-ID-AV-F6 | `a4fcef7` | `AVChannel.channel_id` -> `display_id` | uint32 tag 6 unchanged | 24 |
| Active sensor request identity | CHG-SEN-8001 | `1340b0b` plus the existing `SensorRequest` audit | `SensorStartRequestMessage` -> `SensorRequest` | enum tag 1 and int64 tag 2 unchanged; active schema replaces the retracted duplicate | 47 |
| Additional-video inset identity | CHG-BASELINE-ADDITIONAL-VIDEO | `8a0861a` | resolution-range names -> three inset names | parent tags 1-3 remain messages; child tags 1-4 remain uint32 | 72 |
| Navigation channel enum rendering | CHG-BASELINE-NAV-TYPE | `72ed02c` | numeric `1` -> `TURN_BY_TURN` | varint tag 2 unchanged | 5 |
| Sensor type-entry field identity | CHG-BASELINE-SENSOR-TYPE | `f494172`, with required-field proof in `72ed02c` | `type` -> `sensor_type` | enum varint tag 1 unchanged | 110 |
| Input keycode field identity | CHG-BASELINE-INPUT-KEYCODES | canonical input schema in `f494172`, resolver selection in `1340b0b` | `scan_codes` -> `keycodes` | repeated packed int32 tag 1 unchanged | 16 |
| Navigation current-position semantics | CHG-BASELINE-NAV-STEP-DISTANCE | `72ed02c` | `remaining_distance` -> `step_distance` | captured field 1 and its field-1 distance child remain length-delimited | 72 |
| Active input-binding message identity | CHG-BASELINE-INPUT-BINDING | canonical input schemas in `f494172`, resolver selection in `1340b0b` | message names become `InputBinding*`; response `OK` becomes int32 `0` | request packed-int32 tag 1 and response varint tag 1 unchanged | 36 |
| Bluetooth shared-status rendering | CHG-BASELINE-BT-STATUS | `1340b0b` | numeric `1` -> `UNSOLICITED_MESSAGE` | varint tag 1 unchanged | 1 |

The closed inventory is **383 diff issues**: 11 for
`2026-02-28-s25-cleanbuild`, 111 each for `general` and
`active-navigation`, and 75 each for `idle-baseline` and `music-playback`.
Normalized record counts remain 516, 3,107, 3,107, 2,098, and 2,521
respectively (`general` and `active-navigation` share the 3,107-row capture).

Capture inputs are unchanged:

| Capture | SHA-256 |
|---|---|
| `analysis/captures/non_media/2026-02-28-s25-cleanbuild.jsonl` | `0cc5cee30a6b4b614fc041c360eadd35bc706c5fb47fc1875fd0bde07aca8a81` |
| `analysis/captures/non_media/general.converted.jsonl` | `5654cce4b48b85c0c4c60546f3ca37948f63089fc4cc9b46decd4e9ba5ca2817` |
| `analysis/captures/non_media/idle-baseline.converted.jsonl` | `6b1d6572729f5913dac3f3f617924fb2656f4b0ce4eb29badc5dc1a7f8efb1e9` |
| `analysis/captures/non_media/music-playback.converted.jsonl` | `ad76653d2c58b2f7555834d0d86dfa3da18e2c009d2f7e3871bcaa4ca22f873d` |
| `analysis/captures/non_media/active-navigation.converted.jsonl` | `5654cce4b48b85c0c4c60546f3ca37948f63089fc4cc9b46decd4e9ba5ca2817` |

The durable allowlist gate compares pre-release commit `0812713` with the
refreshed files. It must report exactly the nine groups and counts above, no
other diff signature, unchanged row counts, and the five capture hashes:

```sh
PYTHONPATH=. python3 - <<'PY'
import json, re, subprocess
from collections import Counter
from pathlib import Path
from analysis.tools.proto_stream_validator.diffing import diff_normalized

base = "08127131f26393441364630e51c4936c036c55ba"
names = ["2026-02-28-s25-cleanbuild", "general", "idle-baseline", "music-playback", "active-navigation"]
expected_diffs = {"2026-02-28-s25-cleanbuild": 11, "general": 111, "idle-baseline": 75, "music-playback": 75, "active-navigation": 111}
expected_rows = {"2026-02-28-s25-cleanbuild": 516, "general": 3107, "idle-baseline": 2098, "music-playback": 2521, "active-navigation": 3107}
groups = Counter()

for name in names:
    rel = f"analysis/baselines/non_media/{name}.normalized.json"
    old = json.loads(subprocess.check_output(["git", "show", f"{base}:{rel}"], text=True))
    new = json.loads(Path(rel).read_text())
    assert len(old) == len(new) == expected_rows[name]
    diffs = diff_normalized(old, new)
    assert len(diffs) == expected_diffs[name]
    for diff in diffs:
        path = diff.path
        row_match = re.match(r"\[(\d+)\]", path)
        row = int(row_match.group(1)) if row_match else -1
        old_type = old[row].get("message_type", "") if row >= 0 else ""
        new_type = new[row].get("message_type", "") if row >= 0 else ""
        if ".av_channel.channel_id" in path or ".av_channel.display_id" in path:
            group = "av_display"
        elif ".additional_config." in path:
            group = "additional_video"
        elif path.endswith(".navigation_channel.type"):
            group = "nav_type"
        elif ".sensor_channel.sensors[" in path and (path.endswith(".type") or path.endswith(".sensor_type")):
            group = "sensor_type"
        elif path.endswith(".scan_codes") or path.endswith(".keycodes"):
            group = "input_keycodes"
        elif path.endswith(".remaining_distance") or path.endswith(".step_distance"):
            group = "nav_step_distance"
        elif path.endswith(".message_type") and old_type.endswith("SensorStartRequestMessage") and new_type.endswith("SensorRequest"):
            group = "sensor_request"
        elif (path.endswith(".message_type") and "Binding" in old_type + new_type) or (path.endswith(".decoded.status") and old_type.endswith("BindingResponse")):
            group = "input_binding"
        elif path.endswith(".decoded.status") and old_type.endswith("BluetoothPairingResponse"):
            group = "bt_status"
        else:
            raise AssertionError((name, diff))
        groups[group] += 1

assert groups == Counter({"sensor_type": 110, "additional_video": 72, "nav_step_distance": 72, "sensor_request": 47, "input_binding": 36, "av_display": 24, "input_keycodes": 16, "nav_type": 5, "bt_status": 1}), groups
captures = {
    "analysis/captures/non_media/2026-02-28-s25-cleanbuild.jsonl": "0cc5cee30a6b4b614fc041c360eadd35bc706c5fb47fc1875fd0bde07aca8a81",
    "analysis/captures/non_media/general.converted.jsonl": "5654cce4b48b85c0c4c60546f3ca37948f63089fc4cc9b46decd4e9ba5ca2817",
    "analysis/captures/non_media/idle-baseline.converted.jsonl": "6b1d6572729f5913dac3f3f617924fb2656f4b0ce4eb29badc5dc1a7f8efb1e9",
    "analysis/captures/non_media/music-playback.converted.jsonl": "ad76653d2c58b2f7555834d0d86dfa3da18e2c009d2f7e3871bcaa4ca22f873d",
    "analysis/captures/non_media/active-navigation.converted.jsonl": "5654cce4b48b85c0c4c60546f3ca37948f63089fc4cc9b46decd4e9ba5ca2817",
}
import hashlib
for rel, expected in captures.items():
    assert hashlib.sha256(Path(rel).read_bytes()).hexdigest() == expected
print(f"baseline_refresh groups={dict(groups)} diffs={sum(groups.values())} captures=5/5")
PY
```

## Exact allowed-file sets

These sets are closed and authoritative for both edits and staging. They
override every broader directory, glob, or conditional `git add` example in a
downstream task brief. Executors must replace those examples with the exact
command below. Each command first aborts unless the index is empty, then stages
only literal manifest paths; therefore an unauthorized dirty or previously
staged file cannot enter the task commit. Files appearing in more than one set
may be changed only for the change IDs assigned to that task.

### Task 11: message IDs and directions

```sh
git diff --cached --quiet || { printf '%s\n' 'Refusing to stage Task 11: index is not empty.' >&2; exit 1; }
git add -- \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/change-manifest.md \
  analysis/reports/proto-verification/carcontrol.md \
  analysis/reports/proto-verification/sensor.md \
  analysis/reports/proto-verification/video.md \
  docs/channels/carcontrol.md \
  docs/channels/video.md \
  docs/cross-version/carcontrol.md \
  docs/cross-version/video.md \
  docs/session-handoffs.md \
  oaa/av/AVChannelMediaOptionsMessage.proto \
  oaa/av/AVChannelMessageIdsEnum.proto \
  oaa/av/UiConfigMessages.proto \
  oaa/carcontrol/CarControlMessages.proto \
  oaa/video/CriticalUiNotification.proto \
  oaa/video/IntegratedOverlayStartNotification.proto \
  oaa/video/IntegratedOverlayStopNotification.proto \
  oaa/video/UpdateUiConfigRequestMessage.proto \
  oaa/video/VideoFocusIndicationMessage.proto \
  oaa/video/VideoFocusRequestMessage.proto
```

### Task 12: identity, compatibility, and new services

```sh
git diff --cached --quiet || { printf '%s\n' 'Refusing to stage Task 12: index is not empty.' >&2; exit 1; }
git add -- \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/change-manifest.md \
  analysis/reports/multi-display/prodigy-maintainer-handoff.md \
  docs/channel-map.md \
  docs/channels/architecture.md \
  docs/channels/carintent.md \
  docs/channels/display-routing.md \
  docs/channels/media.md \
  docs/interactions/03-service-discovery.md \
  docs/session-handoffs.md \
  oaa/av/AVChannelData.proto \
  oaa/av/AVChannelData.audit.yaml \
  oaa/carintent/CarIntentMessage.proto \
  oaa/carintent/CarIntentMessage.audit.yaml \
  oaa/control/ChannelDescriptorData.proto \
  oaa/control/ChannelDescriptorData.audit.yaml \
  oaa/input/InputChannelConfigData.proto \
  oaa/input/InputChannelConfigData.audit.yaml \
  oaa/media/BufferedMediaSinkMessage.proto \
  oaa/media/CarLocalMediaPlaybackStatusMessage.proto \
  oaa/media/CarLocalMediaPlaybackStatusMessage.audit.yaml
```

### Task 13: audits, reports, coverage, documentation, and handoff

```sh
git diff --cached --quiet || { printf '%s\n' 'Refusing to stage Task 13: index is not empty.' >&2; exit 1; }
git add -- \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/change-manifest.md \
  analysis/reports/coverage-dashboard/coverage-dashboard.json \
  analysis/reports/coverage-dashboard/coverage-dashboard.md \
  analysis/reports/multi-display/prodigy-maintainer-handoff.md \
  analysis/reports/oem-vw/oem-match-pending-gold-worklist.json \
  analysis/reports/oem-vw/oem-match-pending-gold-worklist.md \
  analysis/reports/oem-vw/promotion-walk.json \
  analysis/reports/oem-vw/promotion-walk.md \
  analysis/reports/proto-verification/PROGRESS.md \
  analysis/reports/proto-verification/carcontrol.md \
  analysis/reports/proto-verification/media.md \
  analysis/reports/proto-verification/sdp-progress.md \
  analysis/reports/proto-verification/sdp.md \
  analysis/reports/proto-verification/sensor.md \
  analysis/reports/proto-verification/video.md \
  analysis/tools/coverage_dashboard/tests/test_run.py \
  analysis/tools/cross_version/tests/test_promoted_sidecars.py \
  analysis/tools/promotion_walker/report.py \
  analysis/tools/promotion_walker/run.py \
  analysis/tools/promotion_walker/tests/fixtures/sidecar_already_platinum.audit.yaml \
  analysis/tools/promotion_walker/tests/fixtures/sidecar_gold_clean.audit.yaml \
  analysis/tools/promotion_walker/tests/test_live_walk_snapshot.py \
  analysis/tools/promotion_walker/tests/test_schema_migration.py \
  analysis/tools/promotion_walker/tests/test_verdict.py \
  analysis/tools/promotion_walker/tests/test_walk_report.py \
  analysis/tools/promotion_walker/verdict.py \
  analysis/tools/seed_import/tests/test_audit_yaml_tier_consistency.py \
  analysis/tools/seed_import/tier_policy.py \
  docs/channel-map.md \
  docs/channels/architecture.md \
  docs/channels/carcontrol.md \
  docs/channels/carintent.md \
  docs/channels/display-routing.md \
  docs/channels/media.md \
  docs/channels/radio.md \
  docs/channels/video.md \
  docs/cross-version/carcontrol.md \
  docs/cross-version/video.md \
  docs/roadmap-current.md \
  docs/session-handoffs.md \
  docs/verification/01-confidence-tiers.md \
  docs/verification/02-audit-trail-format.md \
  docs/verification/03-verification-procedures.md \
  docs/verification/04-source-provenance.md \
  docs/verification/05-oem-match-policy.md \
  oaa/audio/AudioConfigData.audit.yaml \
  oaa/audio/AudioFocusChannelData.audit.yaml \
  oaa/audio/AudioFocusRequestMessage.audit.yaml \
  oaa/audio/AudioFocusResponseMessage.audit.yaml \
  oaa/audio/AudioFocusStateMessage.audit.yaml \
  oaa/audio/AudioStreamTypeEnum.audit.yaml \
  oaa/audio/AudioStreamTypeMessage.audit.yaml \
  oaa/av/AVChannelData.audit.yaml \
  oaa/av/AVChannelMediaConfigMessage.audit.yaml \
  oaa/av/AVChannelMediaOptionsMessage.audit.yaml \
  oaa/av/AVChannelMediaOptionsMessage.proto \
  oaa/av/AVChannelMediaStatsMessage.audit.yaml \
  oaa/av/AVChannelMessageIdsEnum.audit.yaml \
  oaa/av/AVChannelMessageIdsEnum.proto \
  oaa/av/AVChannelSetupRequestMessage.audit.yaml \
  oaa/av/AVChannelSetupResponseMessage.audit.yaml \
  oaa/av/AVChannelStartIndicationMessage.audit.yaml \
  oaa/av/AVInputChannelData.audit.yaml \
  oaa/av/AVInputOpenRequestMessage.audit.yaml \
  oaa/av/AVInputOpenResponseMessage.audit.yaml \
  oaa/av/AVMediaAckIndicationMessage.audit.yaml \
  oaa/av/UiConfigMessages.audit.yaml \
  oaa/bluetooth/BluetoothPairingResponseMessage.audit.yaml \
  oaa/carcontrol/CarControlMessages.audit.yaml \
  oaa/carcontrol/CarPropertyData.audit.yaml \
  oaa/carintent/CarIntentMessage.audit.yaml \
  oaa/common/DriverPositionEnum.audit.yaml \
  oaa/control/ByeByeResponseMessage.audit.yaml \
  oaa/control/CallAvailabilityMessage.audit.yaml \
  oaa/control/ChannelDescriptorData.audit.yaml \
  oaa/control/RadioChannelData.audit.yaml \
  oaa/control/VoiceSessionRequestMessage.audit.yaml \
  oaa/generic/ChannelOpenAckMessage.audit.yaml \
  oaa/input/AbsoluteInputEventData.audit.yaml \
  oaa/input/AbsoluteInputEventsData.audit.yaml \
  oaa/input/ButtonEventData.audit.yaml \
  oaa/input/ButtonEventsData.audit.yaml \
  oaa/input/InputBindingNotificationMessage.audit.yaml \
  oaa/input/InputBindingRequestMessage.audit.yaml \
  oaa/input/InputBindingResponseMessage.audit.yaml \
  oaa/input/InputChannelConfigData.audit.yaml \
  oaa/input/InputEventIndicationMessage.audit.yaml \
  oaa/input/RelativeInputEventData.audit.yaml \
  oaa/input/RelativeInputEventsData.audit.yaml \
  oaa/input/TouchEventData.audit.yaml \
  oaa/input/TouchLocationData.audit.yaml \
  oaa/media/BufferedMediaSinkMessage.audit.yaml \
  oaa/media/CarLocalMediaPlaybackEnum.audit.yaml \
  oaa/media/CarLocalMediaPlaybackMetadataMessage.audit.yaml \
  oaa/media/CarLocalMediaPlaybackRequestMessage.audit.yaml \
  oaa/media/CarLocalMediaPlaybackStatusMessage.audit.yaml \
  oaa/media/MediaPlaybackMetadataMessage.audit.yaml \
  oaa/media/MediaPlaybackStatusEventMessage.audit.yaml \
  oaa/media/MediaPlaybackStatusMessage.audit.yaml \
  oaa/media/MediaStatusListData.audit.yaml \
  oaa/media/MediaTrackIdentifierData.audit.yaml \
  oaa/mic/MicrophoneOpenResponse.audit.yaml \
  oaa/navigation/NavigationChannelData.audit.yaml \
  oaa/navigation/NavigationDistanceMessage.audit.yaml \
  oaa/navigation/NavigationImageOptionsData.audit.yaml \
  oaa/notification/NotificationChannelData.audit.yaml \
  oaa/phone/PhoneCallStateEnum.audit.yaml \
  oaa/phone/PhoneStatusInputMessage.audit.yaml \
  oaa/phone/PhoneStatusMessage.audit.yaml \
  oaa/sensor/SensorChannelConfigData.audit.yaml \
  oaa/sensor/SensorChannelData.audit.yaml \
  oaa/sensor/SensorErrorStatusEnum.audit.yaml \
  oaa/sensor/SensorRequestMessage.audit.yaml \
  oaa/sensor/SensorStartRequestMessage.audit.yaml \
  oaa/sensor/TrailerData.audit.yaml \
  oaa/sensor/VehicleEnergyModelData.audit.yaml \
  oaa/video/AdditionalVideoConfigData.audit.yaml \
  oaa/video/CriticalUiNotification.audit.yaml \
  oaa/video/IntegratedOverlayStartNotification.audit.yaml \
  oaa/video/IntegratedOverlayStopNotification.audit.yaml \
  oaa/video/UiConfigRequestMessage.audit.yaml \
  oaa/video/UpdateUiConfigRequestMessage.audit.yaml \
  oaa/video/VideoConfigData.audit.yaml \
  oaa/video/VideoFocusIndicationMessage.audit.yaml \
  oaa/video/VideoFocusRequestMessage.audit.yaml \
  oaa/video/VideoMarginsData.audit.yaml \
  oaa/wifi/WifiChannelData.audit.yaml \
  oaa/wifi/WifiCredentialsResponseMessage.audit.yaml \
  oaa/wifi/WifiInfoRequestMessage.audit.yaml \
  oaa/wifi/WifiProjectionChannelData.audit.yaml \
  oaa/wifi/WifiSecurityResponseMessage.audit.yaml \
  oaa/wifi/WifiSetupInfoMessage.audit.yaml
```

Task 13 Fix Round 1 expands this authoritative block from 60 to **133 exact
literal paths**. The additions are the canonical policy implementation/tests,
every audit whose derived tier or invalid MATCH-08 metadata changed, the four
OEM walker artifacts and their producer/tests/fixtures, the coverage outputs/snapshot,
the two comment-only AV proto corrections, and synchronized verification,
roadmap, and handoff documentation. The block remains fail-closed and contains
no directory, glob, or broad staging entry.

### Task 14: final release gate and baseline refresh

```sh
git diff --cached --quiet || { printf '%s\n' 'Refusing to stage Task 14: index is not empty.' >&2; exit 1; }
git add -- \
  analysis/baselines/non_media/2026-02-28-s25-cleanbuild.normalized.json \
  analysis/baselines/non_media/active-navigation.normalized.json \
  analysis/baselines/non_media/general.normalized.json \
  analysis/baselines/non_media/idle-baseline.normalized.json \
  analysis/baselines/non_media/music-playback.normalized.json \
  analysis/reports/android-auto-17.3-update/README.md \
  analysis/reports/android-auto-17.3-update/change-manifest.md \
  docs/session-handoffs.md
```

This eight-path extension is limited to Task 14 release evidence and the five
mechanically regenerated non-media baselines. Roadmap sequencing did not
change, so `docs/roadmap-current.md` is intentionally excluded.

## Changed-proto audit coverage

Every proto that the publication tasks may actually change has an explicitly
authorized sidecar. `create` means the sidecar is an authorized later-task
creation, not a file created by this freeze.

| Changed proto | Audit sidecar | Authorized task | State |
|---|---|---|---|
| `oaa/av/AVChannelMediaOptionsMessage.proto` | `oaa/av/AVChannelMediaOptionsMessage.audit.yaml` | Task 13 | create |
| `oaa/av/AVChannelMessageIdsEnum.proto` | `oaa/av/AVChannelMessageIdsEnum.audit.yaml` | Task 13 | create |
| `oaa/av/UiConfigMessages.proto` | `oaa/av/UiConfigMessages.audit.yaml` | Task 13 | existing |
| `oaa/carcontrol/CarControlMessages.proto` | `oaa/carcontrol/CarControlMessages.audit.yaml` | Task 13 | existing |
| `oaa/video/CriticalUiNotification.proto` | `oaa/video/CriticalUiNotification.audit.yaml` | Task 13 | create |
| `oaa/video/IntegratedOverlayStartNotification.proto` | `oaa/video/IntegratedOverlayStartNotification.audit.yaml` | Task 13 | create |
| `oaa/video/IntegratedOverlayStopNotification.proto` | `oaa/video/IntegratedOverlayStopNotification.audit.yaml` | Task 13 | create |
| `oaa/video/UpdateUiConfigRequestMessage.proto` | `oaa/video/UpdateUiConfigRequestMessage.audit.yaml` | Task 13 | create |
| `oaa/video/VideoFocusIndicationMessage.proto` | `oaa/video/VideoFocusIndicationMessage.audit.yaml` | Task 13 | existing |
| `oaa/video/VideoFocusRequestMessage.proto` | `oaa/video/VideoFocusRequestMessage.audit.yaml` | Task 13 | existing |
| `oaa/av/AVChannelData.proto` | `oaa/av/AVChannelData.audit.yaml` | Tasks 12 and 13 | existing |
| `oaa/carintent/CarIntentMessage.proto` | `oaa/carintent/CarIntentMessage.audit.yaml` | Tasks 12 and 13 | create |
| `oaa/control/ChannelDescriptorData.proto` | `oaa/control/ChannelDescriptorData.audit.yaml` | Tasks 12 and 13 | existing |
| `oaa/input/InputChannelConfigData.proto` | `oaa/input/InputChannelConfigData.audit.yaml` | Tasks 12 and 13 | existing |
| `oaa/media/BufferedMediaSinkMessage.proto` | `oaa/media/BufferedMediaSinkMessage.audit.yaml` | Task 13 | create |
| `oaa/media/CarLocalMediaPlaybackStatusMessage.proto` | `oaa/media/CarLocalMediaPlaybackStatusMessage.audit.yaml` | Tasks 12 and 13 | existing |

`CarLocalMediaPlaybackMetadataMessage.proto` already says the message is sent
by the HU to the phone, and `CarLocalMediaPlaybackRequestMessage.proto`
already says `Phone -> HU`. They are no-change inputs, are not publication
targets, and require no 17.3 sidecar update in Tasks 12-13.

## Legacy audit-schema migration set

Task 13 also owns the following exact 21 sidecars solely to migrate legacy
metadata into fields already accepted by `docs/verification/audit-schema.json`.
This authorization does not permit wire-claim changes, invented evidence, or
schema expansion. Historical class names move to `class_mapping`; `msg_id` and
`wire_id` move to `wire_msg_id`; GAL service detail is retained in `channel`;
change/note text moves to `corrections` or the existing retraction record; and
handler evidence uses the accepted `deep_trace` / `apk_deep_trace` type with a
self-contained description.

| Legacy sidecar | Migration only |
|---|---|
| `oaa/carcontrol/CarControlMessages.audit.yaml` | `changes_applied` -> `corrections` |
| `oaa/carcontrol/CarPropertyData.audit.yaml` | `changes_applied` -> `corrections` |
| `oaa/input/AbsoluteInputEventData.audit.yaml` | class/change/note metadata; handler evidence type |
| `oaa/input/AbsoluteInputEventsData.audit.yaml` | class/change/note metadata; handler evidence type |
| `oaa/input/ButtonEventData.audit.yaml` | class/change metadata; handler evidence type |
| `oaa/input/ButtonEventsData.audit.yaml` | class/change metadata; handler evidence type |
| `oaa/input/InputBindingNotificationMessage.audit.yaml` | channel/message/class/change metadata; handler evidence type |
| `oaa/input/InputBindingRequestMessage.audit.yaml` | channel/message/class/change metadata; handler evidence type |
| `oaa/input/InputBindingResponseMessage.audit.yaml` | channel/message/class/change metadata; handler evidence type |
| `oaa/input/InputEventIndicationMessage.audit.yaml` | channel/message/class/change metadata; handler evidence type |
| `oaa/input/RelativeInputEventData.audit.yaml` | class/change metadata; handler evidence type |
| `oaa/input/RelativeInputEventsData.audit.yaml` | class/change metadata; handler evidence type |
| `oaa/input/TouchEventData.audit.yaml` | class/change metadata; handler evidence type |
| `oaa/input/TouchLocationData.audit.yaml` | class/change metadata; handler evidence type |
| `oaa/media/CarLocalMediaPlaybackEnum.audit.yaml` | invalid superseded tier -> retraction/supersession record |
| `oaa/media/MediaPlaybackStatusEventMessage.audit.yaml` | notes -> `corrections` |
| `oaa/mic/MicrophoneOpenResponse.audit.yaml` | wire/note metadata |
| `oaa/navigation/NavigationDistanceMessage.audit.yaml` | internal-only note metadata |
| `oaa/sensor/SensorStartRequestMessage.audit.yaml` | changes -> retraction/corrections record |
| `oaa/sensor/VehicleEnergyModelData.audit.yaml` | changes -> `corrections` |
| `oaa/video/VideoFocusIndicationMessage.audit.yaml` | complete missing evidence description; publication sync |

The Task 13 set additionally owns
`analysis/tools/coverage_dashboard/tests/test_run.py` because the seven newly
created publication sidecars plus the Task 12 CarIntent sidecar and proto
changed every locked live-census value. The snapshot remains literal and
outcome-sensitive; dynamic/self-derived expectations are not authorized.

The committed matcher baseline is intentionally verify-only and is not in an
allowed modification set: Task 1 retained
`analysis/reports/cross-version/17-3-schema-match.json` and
`analysis/reports/cross-version/17-3-schema-match.md` after rejecting promotion
of the three unreviewed fresh-delta rows. Tasks 13-14 confirmed both files
remain unchanged. Runtime validation is likewise not a publication target; its
six rows remain the explicit runtime-unverified boundary.

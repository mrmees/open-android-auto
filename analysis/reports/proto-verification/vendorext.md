# Vendor Extension Channel Verification Report

**Channel:** Vendor Extension (#14)
**Tag:** `GH.DhuVendorExtension` (NOT a GAL tag)
**Handler Class:** `kaz.java` (16.2)
**Verified:** 2026-03-07
**Status:** COMPLETE — Not a GAL channel

## Finding

Vendor Extension is **NOT a GAL wire protocol channel**. It uses the GMS Car API vendor extension mechanism, not the GAL message handler architecture.

### Evidence (kaz.java)

1. **No `iav` inheritance** — kaz.java implements `kgv` and `pnh`, not `iav`/`hym`
2. **No GAL handler** — connects via `nft.m27162aq(m22502f, "com.google.android.apps.auto.components.dhuvendorextension")`
3. **Raw byte[] protocol** — `pnh.mo23469a(byte[])` receives opaque data, no protobuf parsing
4. **DHU-specific** — only activates for `"Google"` manufacturer + `"Desktop Head Unit"` model
5. **GMS tag** — uses `GH.DhuVendorExtension` (GMS helper tag), not `CAR.GAL.*` (GAL channel tag)

### SDP Data (VendorExtensionChannel, ChannelDescriptor field 12)

The existing `VendorExtensionChannelData.proto` defines the SDP structure:
- field 1: string name
- field 2: repeated string package_white_list
- field 3: bytes data

This is the SDP advertisement only. The actual data exchange uses GMS vendor extension API, not proto messages on a GAL channel.

### Conclusion

No GAL handler exists for Vendor Extension. No proto messages to verify. The SDP data proto (`VendorExtensionChannelData.proto`) remains at silver confidence — it describes the ChannelDescriptor field, not wire protocol messages.

## Totals

| Category | Count |
|----------|-------|
| Gold messages | 0 |
| Schema fixes | 0 |
| Retractions | 0 |
| Notes | Not a GAL channel — GMS vendor extension API |

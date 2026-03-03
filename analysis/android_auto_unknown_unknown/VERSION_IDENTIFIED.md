# Version Identification: android_auto_unknown_unknown

**Identified as:** Android Auto 15.9.655104-release (versionCode 159655104)

**Method:** AndroidManifest.xml inspection
- `android:versionName="15.9.655104-release"`
- `android:versionCode="159655104"`
- `android:compileSdkVersionCodename="Baklava"` (Android 16 SDK 36)

**Confirmation:** The source files in `apk-source/sources/` are identical to those in
`analysis/aa-15.9/jadx-output/sources/` -- both are jadx decompilations of the same APK.

**Database stats:**
- proto_classes: 1945
- proto_fields: 4974
- proto_catalog_count: 1479

**Action taken:** Created symlink `analysis/android_auto_15.9.655104-release_159655104` pointing
to this directory, giving it a proper version-tagged name consistent with the 16.1 and 16.2
directory naming convention.

**Date:** 2026-03-03

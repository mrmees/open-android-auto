# PhenotypeFlags Reference Catalog

## Overview

Google's Android Auto APK uses two distinct flag systems to control behavior:

1. **HU Capability Flags** (pus.java) -- A 55-entry enum sent to the phone during connection setup. These are negotiated feature capabilities between the head unit and phone, not server-controlled. The HU declares which capabilities it supports, and the phone adapts its behavior accordingly.

2. **Server-Side Phenotype Flags** -- Google's remote feature flag system (Phenotype/PhenotypeFlags). Over 850 individual flags organized into 43 flag sets within the `gearhead` namespace, plus 4 additional library namespaces. These are set server-side by Google and cached on the phone. The phone reads them at runtime to control feature rollouts, A/B testing, and configuration.

For an open-source HU implementation, the HU Capability Flags are directly relevant (we must declare them correctly). The Phenotype Flags are phone-internal but their default values reveal expected behavior, timing constants, and feature gates that affect what the phone sends over the wire.

**Source:** jadx 1.5.1 decompilation of Android Auto 16.2.660604-release

---

## HU Capability Flags (pus.java)

These 55 flags form a bitmask sent from the head unit to the phone during connection setup. The phone uses them to enable or disable features for the session.

| Index | Field | Name | Deprecated |
|:-----:|:-----:|------|:----------:|
| 0 | a | RESERVED_1 | |
| 1 | b | RESERVED_2 | |
| 2 | c | CAR_WINDOW_RESIZABLE | |
| 3 | d | INT_SETTINGS_AVAILABLE | |
| 4 | e | THIRD_PARTY_ACCESSIBLE_SETTINGS | |
| 5 | f | CLIENT_SIDE_FLAGS | |
| 6 | g | CONTENT_WINDOW_INSETS | |
| 7 | h | ASSISTANT_Z | Yes |
| 8 | i | START_CAR_ACTIVITY_WITH_OPTIONS | |
| 9 | j | STICKY_WINDOW_FOCUS | |
| 10 | k | NON_CONTENT_WINDOW_ANIMATIONS_SAFE | |
| 11 | l | WINDOW_REQUIRES_ONE_TEXTURE_UPDATE_TO_DRAW | |
| 12 | m | CONNECTION_STATE_HISTORY | |
| 13 | n | CLEAR_DATA | |
| 14 | o | START_DUPLEX_CONNECTION | |
| 15 | p | WINDOW_OUTSIDE_TOUCHES | |
| 16 | q | CAR_WINDOW_REQUEST_FOCUS | |
| 17 | r | SUPPORTS_SELF_MANAGED_CALLS | Yes |
| 18 | s | START_FIRST_CAR_ACTIVITY_ON_FOCUS_GAINED | |
| 19 | t | MULTI_DISPLAY | Yes |
| 20 | u | ENHANCED_NAVIGATION_METADATA | Yes |
| 21 | v | INDEPENDENT_NIGHT_MODE | |
| 22 | w | CLUSTERSIM | |
| 23 | x | MULTI_REGION | Yes |
| 24 | y | MICROPHONE_DIAGNOSTICS | Yes |
| 25 | z | AUDIO_STREAM_DIAGNOSTICS | Yes |
| 26 | A | MANIFEST_QUERYING | |
| 27 | B | PREFLIGHT | |
| 28 | C | LIFECYCLE_BEFORE_LIFETIME | Yes |
| 29 | D | POWER_SAVING_CONFIGURATION | |
| 30 | E | INITIAL_FOCUS_SETTINGS | |
| 31 | F | COOLWALK | Yes |
| 32 | G | USE_CONFIGURATION_CONTEXT | |
| 33 | H | DRIVER_POSITION_SETTING | Yes |
| 34 | I | UPDATE_PRESENTATION_INPUT_CONFIGURATION_AT_STARTUP_END | |
| 35 | J | START_AFTER_PRESENTATION_CONFIGURATION_UPDATE | |
| 36 | K | START_CLIENT_AFTER_PRESENTATION_CONFIGURATION_UPDATE | |
| 37 | L | PROJECTED_PRESENTATION_WAIT_UNTIL_CONFIGURED | |
| 38 | M | CRASH_PROJECTED_PRESENTATION_IF_NOT_CONFIGURED | |
| 39 | N | COOLWALK_ROTARY_PROXIMITY_NAVIGATION | |
| 40 | O | GUARD_AGAINST_NO_WINDOW_FOCUS_CHANGE_KILL_SWITCH | Yes |
| 41 | P | GH_DRIVEN_RESIZING | Yes |
| 42 | Q | NATIVE_APPS | |
| 43 | R | HIDE_TURN_CARDS_ON_SECONDARY_DISPLAYS | |
| 44 | S | HERO_CAR_CONTROLS | |
| 45 | T | HERO_CAR_LOCAL_MEDIA | |
| 46 | U | HERO_PUNCH_THROUGH | |
| 47 | V | REMOVE_WINDOW_FOCUS_THROUGH_ON_INPUT_FOCUS_CHANGED_KILL_SWITCH | |
| 48 | W | HERO_THEMING | |
| 49 | X | PERSIST_PROJECTION_CONFIGURATION_CONTEXT | |
| 50 | Y | APP_CONTROLLED_IMMERSIVE_MODE | |
| 51 | Z | USE_INTERNAL_CONTEXT | |
| 52 | aa | ONLY_PROCESS_CAR_CONFIGURATION_CHANGE | |
| 53 | ab | CIELO | |
| 54 | ac | PROCESS_FONT_WEIGHT_ADJUSTMENT_CONFIGURATION_CHANGE | |

### Deprecation Notes

Deprecated flags are still recognized but no longer meaningful -- the phone has hardcoded the behavior:

- **COOLWALK (31)** and **MULTI_DISPLAY (19)** -- Hardcoded to `true` on the phone side. All phones now assume Coolwalk UI and multi-display support.
- **ASSISTANT_Z (7)**, **SUPPORTS_SELF_MANAGED_CALLS (17)**, **ENHANCED_NAVIGATION_METADATA (20)**, **MULTI_REGION (23)**, **MICROPHONE_DIAGNOSTICS (24)**, **AUDIO_STREAM_DIAGNOSTICS (25)**, **LIFECYCLE_BEFORE_LIFETIME (28)**, **DRIVER_POSITION_SETTING (33)**, **GUARD_AGAINST... (40)**, **GH_DRIVEN_RESIZING (41)** -- Legacy capabilities from older protocol versions.

### Key Flag Groups

- **Hero flags (44-48):** Control embedded/integrated HU display modes (POIP = landscape cutout, SOIP = portrait cutout). Only relevant for AAOS-style integrated head units, not projection.
- **CIELO (53):** Material 3 theme overlay. When set, phone sends M3-style theming data.
- **NATIVE_APPS (42):** Enables Car App Library native apps (Cradle mode).
- **Presentation config flags (34-38):** Control startup sequencing -- when the HU reports its display configuration relative to connection establishment.

---

## Flag Namespaces

The AA APK registers flags under 5 namespaces:

| Namespace | Config Keys | Purpose |
|-----------|-------------|---------|
| `com.google.android.projection.gearhead` | CAR, GEARHEAD_ANDROID_PRIMES | All AA-specific flags (43 flag sets) |
| `com.google.android.libraries.performance.primes` | CLIENT_LOGGING_PROD | Performance telemetry |
| `com.google.android.gms.auth_account_client` | ANDROID_AUTH | Auth token handling |
| `com.google.android.libraries.consentverifier` | (default) | GDPR/consent verification |
| `com.google.android.gms.maps` | MAPS_API, GMM_REALTIME_COUNTERS | Google Maps SDK config |

Only the **gearhead** namespace contains AA-specific flags. The others are shared Google library flags for telemetry, auth, consent, and maps rendering.

---

## Gearhead Flag Sets by Category

### Layout / UI

#### SystemUi (abgu.java) -- 73 flags

The largest flag set. Controls layout breakpoints, notification behavior, thermal limits, and UI features.

**Layout Breakpoints:**

| Flag | Type | Default | Purpose |
|------|:----:|:-------:|---------|
| horizontal_rail_canonical_breakpoint_dp | long | 450 | Width threshold for horizontal rail (bottom bar) |
| short_portrait_breakpoint_dp | long | 680 | Height threshold for SHORT_PORTRAIT mode |
| semi_widescreen_breakpoint_dp | long | 880 | Width threshold for SEMI_WIDESCREEN mode |
| portrait_breakpoint_dp | long | 900 | Width threshold below which PORTRAIT is used |
| widescreen_breakpoint_dp | long | 1240 | Width threshold for full WIDESCREEN mode |
| widescreen_aspect_ratio_breakpoint | double | 1.67 | Aspect ratio threshold for widescreen classification |

**Notification / HUN (Heads-Up Notification):**

| Flag | Type | Default | Purpose |
|------|:----:|:-------:|---------|
| allow_hun_after_recycle_kill_switch | bool | true | Allow HUN after recycling |
| hun_default_heads_up_timeout_ms | long | 8000 | HUN display duration |
| hun_delay_poll_time_ms | long | 1000 | HUN poll interval |
| enable_smaller_button_for_icon_only_third_action_in_hun | bool | false | Compact HUN button |
| media_hun_in_rail_widget_timeout_ms | long | 8000 | Media HUN in rail timeout |
| rail_notification_badge_animation_enabled | bool | true | Badge animations |
| notification_badge_with_count_millis_duration | long | 12000 | Badge count display time |

**Thermal Management:**

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| thermal_battery_temperature_severe_threshold | long | 420 | 42.0C battery threshold |
| thermal_camera_threshold | long | 3 | Camera thermal level |
| thermal_display_threshold | long | 3 | Display thermal level |
| thermal_flashlight_threshold | long | 3 | Flashlight thermal level |
| thermal_hotspot_threshold | long | 3 | Hotspot thermal level |
| thermal_wireless_charging_threshold | long | 3 | Wireless charging thermal level |
| thermal_state_hun_reasons_enabled | list | HOTSPOT, WIRELESS_CHARGING, FLASHLIGHT, CAMERA, DISPLAY | Which thermal sources trigger HUN |

**UI Features:**

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| dnd_suppress_notifications_enabled | bool | false | Do Not Disturb |
| enable_gemini_in_aap_kill_switch | bool | true | Gemini AI in projection |
| inertial_scrolling_enabled | bool | false | Inertial scroll behavior |
| parked_app_badge_enabled | bool | false | App badges while parked |
| use_compose_rail | bool | false | Jetpack Compose rail migration |
| use_cal_voice_plate_for_assistant | bool | false | CAL voice plate |
| use_cal_voice_plate_for_gemini | bool | false | Gemini voice plate |
| wallpaper_backdrop_enabled | bool | false | Phone wallpaper backdrop |
| disable_gearsnacks_on_motorcycles_kill_switch | bool | true | GearSnacks = suggestion cards |
| satellite_network_status | bool | false | Satellite connectivity indicator |

**OEM Deny Lists (string lists):**

| Flag | Default Values |
|------|----------------|
| oem_exit_display_name_label_make_model_year_denylist | audi, jaguar, land_rover |
| oem_exit_label_denylist | OEM Infotainment, Cherry Auto... |
| oem_exit_label_make_model_year_denylist | gmc, cadillac, chevrolet, buick, hummer, byd |
| phone_wallpaper_in_launcher_denylist | BMW, MGU22 |

#### Coolwalk (aazl.java) -- 32 flags

Dashboard card behavior and Material 3 theme flags.

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| assistant_suggestions_enabled | bool | false | Assistant suggestion cards |
| dashboard_show_3p_notifications_with_actions_enabled | bool | false | 3P notification actions |
| enable_gm3_icon_tinting | bool | false | Material 3 icon tinting |
| gm3_focus_enabled | bool | false | Material 3 focus indicators |
| use_gm3_theme | bool | false | Material 3 theme |
| use_light_dark_theme | bool | false | Light/dark theme support |
| use_phone_primary_color | bool | false | Phone accent color |
| neutralized_theme_kill_switch | bool | true | Neutral theme fallback |
| dashboard_notifications_refresh_interval_seconds | long | 30 | Dashboard refresh rate |
| dashboard_top_card_debounce_milliseconds | long | 100 | Top card debounce |
| dashboard_top_card_rate_limit_milliseconds | long | 2000 | Top card rate limit |
| live_card_dashboard_visibility_debounce_milliseconds | long | 300 | Live card debounce |
| media_rec_card_timeout_in_millis | long | 15000 | Media recommendation timeout |
| mediacard_session_timeout_in_millis | long | 3000 | Media card session timeout |
| messaging_notification_priority_threshold_seconds | long | 60 | Messaging priority threshold |
| messaging_notification_timeout_seconds | long | 120 | Messaging notification timeout |
| nav_app_border_width | long | 0 | Nav app border width (px) |
| rounded_corner_mask_display_specific_denylist | list | Ford, Genesis, GMC, Mercedes-Benz, Volvo | No rounded corners |
| supported_navigation_apps | list | GMM variants, Waze, LocnAll | Recognized nav apps |

#### ProjectionWindowManager (abfq.java) -- 17 flags

Video rendering and frame pacing.

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| choreographer_based_frame_pacing_enabled | bool | false | Choreographer sync |
| non_square_scale_limit | double | 1.35 | Max non-square pixel scaling |
| non_square_scale_min_limit | double | 1.0125 | Min non-square pixel scaling |
| max_pending_frames_to_send | long | 3 | Frame queue depth |
| composition_semaphore_timeout | long | 5000 | Composition timeout (ms) |
| expected_frame_time_deviation | double | 0.5 | Frame timing tolerance |
| frame_update_timestamps_queue_size | long | 300 | Timestamp history size |
| vsync_time_normalization_rebase_frames | long | 10000 | VSync rebase interval |
| show_display_information | bool | false | Debug display info overlay |

#### MultiDisplay (abdx.java) -- 11 flags

Multi-display configuration and routing.

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| cluster_launcher_enabled | bool | false | Launcher on cluster display |
| cluster_rotary_window_navigation | bool | true | Rotary nav on cluster |
| clustersim_enabled | bool | false | Cluster simulator |
| gal_munger_enabled | bool | false | GAL message multiplexing |
| aux_display_default_configuration | long | 2 | Default auxiliary config |
| cluster_display_default_configuration | long | 2 | Default cluster config |
| auxiliary_display_supported_components | list | GMM variants + SDK samples | Auxiliary display apps |
| cluster_display_supported_components | list | GMM auxiliary projection variants | Cluster display apps |
| reject_clusters_for_unsupported_nav_apps | list | hyundai, kia, genesis | Reject cluster if nav unsupported |

---

### Connectivity

#### WirelessProjection (abjp.java) -- 145 flags

The second-largest flag set. Controls WiFi Direct, Bluetooth pairing, dongle detection, and wireless connection lifecycle.

**Key Connection Flags:**

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| enable_dual_sta | bool | false | Dual-STA WiFi (concurrent connections) |
| use_wpa3_when_available | bool | false | WPA3 support |
| no_bssid_validation | bool | false | Skip BSSID validation |
| start_from_notification_enabled | bool | false | Connect from notification |
| use_rfcomm_transport_for_spark | bool | false | RFCOMM for wireless (Spark) |
| associate_bt_devices_and_trigger_wireless_from_cdm | bool | false | CompanionDeviceManager |
| fallback_to_rfcomm_on_t_minus | bool | false | RFCOMM fallback |

**Timing Constants:**

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| bt_socket_write_delay_ms | long | 10 | BT write delay |
| cancellation_token_expire_in_seconds | long | 600 | 10 minute timeout |
| check_if_hu_is_reachable_timeout_millis | long | 100 | HU reachability check |
| hfp_connect_event_timeout_ms | long | 5000 | HFP connect timeout |
| wpp_first_message_timeout_ms | long | 12000 | First wireless message timeout |

**Device Detection:**

| Flag | Default | Notes |
|------|---------|-------|
| dongle_device_name_matches | "Intercooler,AndroidAuto-" | Third-party dongle name patterns |
| invalid_bt_device_types | "Untethered Headset", "Headset" | Filtered BT device types |
| suspicious_hu_bt_name_regexps | buds, airpods, watch, 1000XM patterns | Audio device false-match patterns |
| third_party_dongle_name_regexps | "AAWireless-.*" | Known dongle patterns |
| use_rfcomm_transport_for_spark_head_unit_allowlist | BMW, bmw_idc23 | BMW gets RFCOMM |
| wifi_projection_protocol_head_unit_denylist | DENSO, Pioneer, Huizhou Desay, ALPINE | WiFi protocol deny list |
| wifi_lock_selected_option_in_network_request_manager | "high_performance" | WiFi lock mode |

#### BluetoothPairing (aaxs.java) -- 6 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| car_bluetooth_service_disable | bool | false | Disable car BT service |
| disable_a2dp | bool | false | Disable A2DP profile |
| prevent_rebonding_during_wired_projection | bool | false | No BT rebond during wired |
| prevent_rebonding_during_wireless_projection | bool | false | No BT rebond during wireless |

#### ConnectivityLogging (aazc.java) -- 25 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| heartbeat_interval_ms | long | 60000 | 1-minute heartbeat |
| session_timeout_ms | long | 120000 | 2-minute session timeout |
| bluetooth_timeout_millis | long | 10000 | BT timeout |
| connectivity_refresh_timeout_ms | long | 3000 | Connectivity refresh |
| head_unit_models | string | "Android Auto\|Android Open Automotive Protocol\|Android" | Recognized HU model strings |

#### UsbBabysitter (abhq.java) -- 16 flags

USB mode switching and recovery.

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| usb_recovery_v2 | bool | true | V2 recovery enabled |
| skip_reset_when_car_connected | bool | true | No USB reset while connected |
| switch_usb_function_on_bluetooth_connect | bool | false | USB switch on BT connect |
| usb_recovery_v2_accessory_timeout_ms | long | 10000 | Accessory mode timeout |
| default_usb_function | long | -1 | Default USB function (-1 = auto) |
| stop_monitoring_delay_ms | long | 5000 | Stop monitoring delay |

---

### Media / Audio

#### Media (abcy.java) -- 27 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| cal_ui_enabled | bool | false | Car App Library media UI |
| enable_external_cal_media_apps | bool | false | External CAL media apps |
| layer_cake_root_children_cache_enabled | bool | false | Media browse tree cache |
| projected_speedbump_enabled | bool | false | Driving distraction restriction |
| show_album_art_for_suggestion | bool | false | Album art in suggestions |
| support_multiple_dashboard_media_cards | bool | false | Multiple media cards |
| support_playback_only_media | bool | false | Playback-only media apps |
| autoplay_paused_after_buffering_retry_delay_ms | long | 250 | Autoplay retry delay |

#### SynchronizedMedia (abgo.java) -- 21 flags

A/V synchronization timing parameters.

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| enable_sync | bool | false | A/V sync enabled |
| enable_sync_parked_exp | bool | true | Sync while parked |
| enable_media_stats | bool | true | Media statistics |
| audio_buffer_limit_ms | long | 300 | Audio buffer limit |
| audio_buffer_limit_ms_tts | long | 400 | TTS audio buffer limit |
| max_audio_delay_allowed_ms | long | 500 | Max audio delay |
| max_video_delay_allowed_ms | long | 500 | Max video delay |
| max_lag_tolerance_ms | long | 20 | Max lag tolerance |
| sync_interval_ms | long | 1000 | Sync check interval |

#### AudioBufferingFeature (aawr.java) -- 10 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| default_minimum_audio_buffers_for_wifi | long | 8 | WiFi audio buffer minimum |
| minimum_audio_buffers_for_wifi | long | 4 | WiFi buffer count |
| minimum_audio_buffers_for_wifi_navigation | long | 4 | WiFi nav audio buffers |
| minimum_audio_buffers_for_usb | long | 0 | USB buffer count (no extra) |
| system_sound_capture_queue_frames_navigation_16khz | long | 8 | Nav capture frames (16kHz) |
| system_sound_capture_queue_frames_navigation_48khz | long | 12 | Nav capture frames (48kHz) |
| minimum_audio_buffers_for_wifi_exclusion_list | list | Kenwood, Sony, Mazda/Panasonic, BMW/MGU, RAM/Mitsubishi, Uconnect | HUs excluded from WiFi buffer minimums |

#### AudioFocus (aaxg.java) -- 6 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| hold_channels_for_asr | bool | true | Hold audio channels during speech recognition |
| check_current_focus_change_command_kill_switch | bool | true | Focus change validation |
| loss_asr_stop_delay_ms | long | 50 | ASR stop delay on focus loss |
| should_stop_media_without_interrupting_guidance_deny_list | list | "SYNC" | Ford SYNC won't stop media during guidance |

#### AudioDiagnosticsFeature (aaxa.java) -- 9 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| audio_stats_logging_period_milliseconds | long | 30000 | Stats logging interval |
| log_audio_latency_stats_telemetry_threshold_usb | long | 700 | USB latency reporting threshold (ms) |
| log_audio_latency_stats_telemetry_threshold_wifi | long | 1400 | WiFi latency reporting threshold (ms) |
| report_audio_latency_stats_interval_ms | long | 30000 | Latency stats interval |
| publishing_period_millis | long | 1000 | Diagnostics publishing period |

---

### Video

#### VideoEncoderParams (abif.java) -- 20 flags

Video encoding parameters and adaptive bitrate configuration.

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| adaptive_bitrate_baseline_h264 | long | 1500000 | H.264 baseline bitrate (1.5 Mbps) |
| adaptive_bitrate_baseline_h265 | long | 3500000 | H.265 baseline bitrate (3.5 Mbps) |
| adaptive_bitrate_gradient_h264 | double | 2.75 | H.264 bitrate gradient |
| adaptive_bitrate_gradient_h265 | double | 0.46 | H.265 bitrate gradient |
| adaptive_bitrate_minimal_h264 | long | 2000000 | H.264 minimum bitrate (2.0 Mbps) |
| adaptive_bitrate_minimal_h265 | long | 2000000 | H.265 minimum bitrate (2.0 Mbps) |
| bitrate_adjustment_exponent | double | 0.5 | Bitrate adjustment curve |
| enable_max_h264_encoder_compatibility | bool | false | Max H.264 compatibility mode |
| force_software_codec | bool | false | Force software encoding |
| key_frame_interval_ackless | long | 2 | Keyframe interval, ackless mode (sec) |
| key_frame_interval_wireless | long | 60 | Keyframe interval, wireless (sec) |
| max_qp_wireless | long | 30 | Max quantization param, wireless |
| min_qp_wireless | long | 15 | Min quantization param, wireless |
| roi_qp_offset | long | 0 | Region of Interest QP offset |
| sixty_fps_bitrate_multiplier | double | 2.0 | 60fps bitrate multiplier (H.264) |
| sixty_fps_bitrate_multiplier_h265 | double | 2.0 | 60fps bitrate multiplier (H.265) |

#### FrameRateRestrictions (abbc.java) -- 14 flags

Thermal and power-based FPS limiting.

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| cap_fps_when_non_interactive_limit | long | 30 | FPS cap when idle |
| fps_limit_for_power_low_display_idle | long | 30 | Low power idle FPS |
| fps_limit_for_restriction_level_high | long | 15 | High restriction FPS |
| fps_limit_for_restriction_level_medium | long | 30 | Medium restriction FPS |
| min_number_of_displays_to_trigger_restrictions | long | 2 | Display count to trigger limits |
| min_thermal_status_for_frame_rate_restrictions | long | 3 | Thermal status trigger level |
| cap_fps_when_non_interactive_cars | list | ford, cupra, seat, skoda, volkswagen, google | Cars with non-interactive FPS cap |

---

### Protocol

#### FrameworkGalFeature (abbf.java) -- 27 flags

GAL (Google Automotive Link) wire protocol configuration.

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| fragment_size | long | 16128 | Max GAL fragment size (bytes) |
| framer_send_buffer_size | long | 16384 | Send buffer size |
| max_audio_buffer_ms | long | 900 | Max audio buffer (ms) |
| detect_hu_gal_ping_timeout | bool | false | Detect HU ping timeout |
| hu_gal_ping_timeout_delta_ms | long | 50 | Ping timeout delta |
| is_gal_snoop_available | bool | false | GAL packet snooping available |
| is_gal_snoop_enabled_in_starship | bool | false | GAL snooping in Starship |
| use_ping_configuration | bool | false | Use ping configuration |
| use_sequence_numbers | bool | false | Sequence number tracking |
| close_on_reader_finish | bool | false | Close on reader finish |

**Audio Buffer Stall Parameters:**

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| audio_deprioritization_threshold_ms_usb | long | 0 | USB deprioritization threshold |
| audio_deprioritization_threshold_ms_wifi | long | 0 | WiFi deprioritization threshold |
| stall_threshold_ms_usb | long | 5000 | USB stall detection threshold |
| stall_threshold_ms_wifi | long | 5000 | WiFi stall detection threshold |
| target_buffer_after_max_buffer_reached_ms | long | 700 | Target buffer after max reached |
| target_buffer_after_stall_ms_usb | long | 250 | Target buffer after USB stall |
| target_buffer_after_stall_ms_wifi | long | 250 | Target buffer after WiFi stall |

---

### Features

#### HeroFeature (abca.java) -- 19 flags

Hero = integrated/embedded display mode for AAOS head units (not projected). POIP = landscape cutout, SOIP = portrait cutout.

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| enabled | bool | true | Master Hero enable |
| cutouts_enabled | bool | true | Display cutout support |
| punch_through_enabled | bool | false | HU renders through AA overlay |
| car_controls_enabled | bool | true | Car controls in Hero mode |
| car_media_enabled | bool | true | Car media in Hero mode |
| radio_enabled | bool | true | Radio in Hero mode |
| theming_enabled | bool | true | Hero theming support |
| assistant_hero_enabled | bool | false | Assistant in Hero mode |
| demo_app_enabled | bool | false | Demo app |
| herosim_enabled | bool | false | Hero simulator |
| herosim_hmg_temp_enabled | bool | false | Hyundai Motor Group simulator |
| force_hero_layout | bool | false | Force Hero layout |
| force_hero_vertical | bool | false | Force vertical Hero |
| force_cutouts | bool | false | Force display cutouts |
| use_new_media_ui | bool | false | New media UI |

#### CradleFeature (aazp.java) -- 16 flags

Cradle = native apps running on embedded AAOS head units.

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| immersive_mode_enabled | bool | true | Immersive mode for native apps |
| all_app_launcher_enabled | bool | false | All-app launcher |
| app_controlled_immersive_mode_enabled | bool | false | App-controlled immersive |
| day_night_enabled | bool | false | Day/night theme switching |
| enable_browser_intent_interception | bool | true | Browser intent handling |
| promo_apps_enabled | bool | true | Promotional game apps |
| show_dpi_picker | bool | false | DPI picker in settings |

#### Weather (abja.java) -- 9 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| enable_auto_dismiss_card | bool | false | Auto-dismiss weather card |
| enable_on_all_screens | bool | false | Weather on all screens |
| specify_temp_unit | bool | true | Explicit temperature unit |
| api_call_polling_interval_ms | long | 360000 | Weather API poll interval (6 min) |
| api_call_retry_interval_ms | long | 30000 | API retry interval |
| auto_dismiss_threshold_ms | long | 600000 | Auto-dismiss timeout (10 min) |

#### PhoneThemeFeature (abey.java) -- 5 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| enable_dynamic_app_icon_shape_by_manufacturer_ks | bool | true | Dynamic icon shapes |
| enable_dynamic_font_family | bool | false | Dynamic font family |
| manufacturer_prefers_device_font_family | string | samsung | OEMs using device font |
| manufacturer_uses_dynamic_icon_shape | string | samsung, google | OEMs with dynamic icon shapes |

---

### UX

#### UserEducation (abht.java) -- 45 flags

Tooltip and first-run education flows. All tooltips default to disabled.

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| assistant_tooltip_first_run_enabled | bool | false | Assistant first-run tooltip |
| launcher_tooltip_first_run_enabled | bool | false | Launcher first-run tooltip |
| notification_tooltip_first_run_enabled | bool | false | Notification tooltip |
| roca_classic_upgrade_tooltip_first_run_kill_switch | bool | true | ROCA = legacy UI upgrade tooltip |
| assistant_tooltip_nth_run_count | long | 3 | Show assistant tip N times |
| launcher_tooltip_nth_run_count | long | 3 | Show launcher tip N times |
| start_of_drive_opportunity_delay | long | 5000 | Delay before showing tips (ms) |
| assistant_tooltip_start_of_navigation_threshold_seconds | long | 10800 | Nav tip threshold (3 hours) |

#### Messaging (abdk.java) -- 26 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| carextender_enabled | bool | true | CarExtender notification support |
| autoplay_messages_kill_switch | bool | false | Auto-read messages |
| display_address_as_navigate_action_label | bool | false | Address as nav action |
| smart_actions_in_messaging_ui_enabled | bool | false | Smart reply actions |
| smart_action_navigate_enabled_for_all_nav_apps | bool | false | Smart nav action for all apps |
| minimum_smart_action_confidence_score | double | 0.5 | Smart action confidence threshold |
| max_last_msg_received_age_to_display_smart_actions_hr | long | 12 | Smart action age limit (hours) |
| llm_info_page_uri | string | https://support.google.com/assistant/answer/14524048 | LLM info page |

#### Dialer (abak.java) -- 18 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| enable_duplex_for_compatible_dialers | bool | false | Simultaneous phone + car audio |
| external_dialer_enabled | bool | false | External dialer app |
| multi_sim_is_dry_run | bool | false | Multi-SIM support dry run |
| notification_powered_calls_enabled | bool | false | Notification-powered calls |
| call_audio_spot_check_delay_millis | long | 4000 | Audio spot check delay |
| delayed_startup_timeout_for_duplex_ics_ms | long | 60000 | Duplex startup timeout |

#### Assistant (aawl.java) -- 25 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| dodgeboost_initial_handshake_enabled | bool | true | DodgeBoost handshake |
| has_latest_robin_model | bool | false | Robin = on-device ML model |
| interrupt_live_on_short_search_key_press_kill_switch | bool | true | Short press interrupts live |
| upgrade_model_notification_enabled | bool | false | Model upgrade notification |
| transcription_character_limit | long | 45 | Transcription display limit |
| education_delay_milliseconds | long | 15000 | Education tip delay |
| gemini_live_dashboard_focus_delay | long | 300 | Gemini Live focus delay (ms) |

#### Preflight (abfe.java) -- 27 flags

Setup and onboarding flow.

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| allow_unsupported_aap_countries | bool | false | Allow unsupported countries |
| is_device_country_blocked | bool | false | Country blocking |
| is_phone_denylisted | bool | false | Phone deny list |
| simplified_pre_setup_enabled | bool | false | Simplified setup |
| vibrate_phone_during_frx_dialog | bool | false | Vibrate during first run |
| dont_show_again_count | long | 3 | "Don't show again" threshold |
| frx_rewind_interval_hours | long | 672 | FRX re-show interval (28 days) |

---

### Infrastructure

#### Performance (abep.java) -- 20 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| pre_warm_activities_enabled | bool | false | Pre-warm activities |
| optimize_audio_capture | bool | false | Optimized audio capture |
| enable_csl_lazy_loading | bool | false | Connection State Layer lazy load |
| log_to_telemetry | bool | true | Log performance data |
| delay_prewarm_ms | long | 2000 | Pre-warm delay |
| lifetime_delayed_start_delay_ms | long | 1000 | Delayed start |
| lifetime_delayed_start_no_video_focus_timeout_ms | long | 2000 | No-video timeout |

#### ClientAnrs (aayw.java) -- 15 flags

Application Not Responding timeouts. These define how long the phone waits before declaring a client ANR.

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| default_timeout_ms | long | 5000 | Default ANR timeout |
| display_cam_timeout_ms | long | 53000 | Display CAM timeout |
| input_event_timeout_ms | long | 10000 | Input event timeout |
| input_focus_change_timeout_ms | long | 10000 | Focus change timeout |
| lifetime_timeout_ms | long | 30000 | Lifetime timeout |
| resume_timeout_ms | long | 10000 | Resume timeout |
| setup_timeout_ms | long | 18000 | Setup timeout |
| start_timeout_ms | long | 13000 | Start timeout |
| video_config_change_timeout_ms | long | 10000 | Video config change timeout |

#### LifecycleRecovery (abcs.java) -- 6 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| watchdog_process | bool | true | Watchdog process enabled |
| projection_crash_loop_mitigation_enabled | bool | false | Crash loop mitigation |
| good_connection_seconds | long | 60 | Seconds before connection considered stable |
| max_disconnects_before_crash_loop | long | 10 | Disconnect threshold |

#### AppValidation (aawh.java) -- 7 flags

| Flag | Type | Default | Notes |
|------|:----:|:-------:|-------|
| dhu_bypass_validation | bool | true | DHU skips app validation |
| should_bypass_validation | bool | false | Bypass app validation |
| allowed_package_list | list | samsung oneconnect, samsung messaging | Allowed packages |
| blocked_packages_by_installer | list | (massive list) | Sideloaded apps blocked |

---

### Remaining Flag Sets

These sets are primarily telemetry, surveys, or minor infrastructure concerns:

| Flag Set | Class | Flags | Purpose |
|----------|-------|:-----:|---------|
| CarAppLibrary (Watevra) | abix.java | 22 | CAL host config (API levels, list sizes, speedbump) |
| CarAppLibrary | aayh.java | 57 | CAL template rendering, Compose migration flags |
| CarActivityManager | aaye.java | 10 | Activity lifecycle management |
| CarSensorParameters | aayq.java | 8 | Sensor rates, parked speed thresholds |
| TouchpadUiNavigation | abha.java | 8 | Touchpad focus navigation tuning |
| ContentBrowse | aazf.java | 6 | Driving distraction restrictions |
| Feedback | abat.java | 6 | User feedback collection |
| Bugreport | aayb.java | 7 | Bug report configuration |
| Settings | abgi.java | 7 | Settings backup/restore |
| Troubleshooter | abhd.java | 7 | Interactive troubleshooter |
| Csat | aazv.java | 5 | Customer satisfaction surveys |
| Hats | abbr.java | 5 | Happiness Tracking Surveys |
| HeadUnitFeature | abbx.java | 5 | HU update notifications |
| OsDeprecation | abej.java | 5 | OS version deprecation warnings (min SDK 28 = Android 9) |

**Watevra notable values** (CAL host configuration):

| Flag | Default | Notes |
|------|---------|-------|
| host_car_app_library_latest_api_level | 8 | Latest CAL API level |
| host_max_api_level | DEFAULT:7, gearhead:8 | Max API level |
| max_grid_list_size | DEFAULT:6, gearhead:24 | Max grid items |
| max_list_size | DEFAULT:6, gearhead:20 | Max list items |
| max_template_stack_size | DEFAULT:5 | Max template depth |
| speedbump_enabled | false | Driving distraction restriction |

**CarSensorParameters notable values:**

| Flag | Default | Notes |
|------|---------|-------|
| max_parked_speed_gps_sensor | 1.5 m/s | Speed below which car is "parked" (GPS) |
| max_parked_speed_wheel_sensor | 0.5 m/s | Speed below which car is "parked" (wheel) |
| desired_flp_request_interval_ms | 200 | Fused Location Provider interval |
| sensor_types_to_rate_throttle_at_delivery_phase | SENSOR_SPEED, SENSOR_LOCATION | Throttled sensors |

---

## Non-Gearhead Namespaces

These are shared Google library flags, not AA-specific. Included for completeness.

| Namespace | Classes | Purpose |
|-----------|---------|---------|
| Primes (`com.google.android.libraries.performance.primes`) | aboy, abpe, abpq, abol, abov, abqc, abpb, abpk | Performance telemetry configuration |
| Auth (`com.google.android.gms.auth_account_client`) | abka (10 flags) | Auth token handling |
| Consent Verifier (`com.google.android.libraries.consentverifier`) | abmt (19 flags) | GDPR/consent verification |
| Maps (`com.google.android.gms.maps`) | abnd (31), abnj (8), abng (5) | Maps SDK rendering |

---

## Layout Breakpoints

These SystemUi breakpoints determine which Coolwalk layout mode the phone selects. The phone calculates display dimensions in dp (from video resolution and reported DPI) and picks a mode:

```
Width < 450dp                           -> No horizontal rail
Width 450-879dp                         -> CANONICAL (horizontal rail, single pane)
Width 880-1239dp                        -> SEMI_WIDESCREEN (2-pane dashboard)
Width >= 1240dp AND ratio >= 1.67       -> WIDESCREEN (3-pane dashboard)
Width < 900dp                           -> PORTRAIT modes
Height < 680dp                          -> SHORT_PORTRAIT
```

**Dashboard horizontal threshold** (from `mno.m26328K`): 730dp (landscape) / 800dp (portrait).

**Layout modes** (from `mnu` enum): CANONICAL, WIDESCREEN, CLUSTER, CLUSTER_WITH_LAUNCHER, AUXILIARY, PORTRAIT, PORTRAIT_SHORT.

### Example: 1024x600 at 160 DPI

- Width = 1024dp, Height = 600dp
- Exceeds semi_widescreen (880dp) but not widescreen (1240dp)
- Aspect ratio = 1024/600 = 1.707 > 1.67 threshold
- Result: SEMI_WIDESCREEN or WIDESCREEN depending on combined width+ratio logic
- Dashboard: horizontal (1024 > 730dp threshold)

---

## Implementation Notes for OAP

### Must Implement

- **HU Capability Flags:** Declare the correct bitmask in the SDP. At minimum, set flags for features OAP actually supports (COOLWALK, MULTI_DISPLAY are deprecated but harmless to include).
- **Layout breakpoints:** These are phone-internal, but the phone's layout choice depends on the video resolution and DPI that OAP reports. To get SEMI_WIDESCREEN on 1024x600, report 160 DPI.
- **ANR timeouts:** The phone will kill the session if the HU doesn't respond within these windows. The most critical: `setup_timeout_ms` (18s), `start_timeout_ms` (13s), `input_event_timeout_ms` (10s), `video_config_change_timeout_ms` (10s).

### Should Be Aware Of

- **VideoEncoderParams:** The phone's adaptive bitrate algorithm targets 1.5 Mbps baseline for H.264. If OAP reports low bandwidth, the phone will reduce quality. Keyframe interval is 2s for ackless mode, 60s for wireless.
- **GAL fragment_size (16128):** Max GAL fragment the phone will send. OAP must handle reassembly of messages larger than this.
- **A/V sync parameters:** Audio buffer limit 300ms, max lag tolerance 20ms, sync interval 1000ms. These inform what latency budget OAP has.
- **LifecycleRecovery:** The phone considers 60 seconds a "good connection." After 10 disconnects, it triggers crash loop mitigation.
- **FrameRateRestrictions:** Phone may throttle to 15-30 FPS based on thermal status. Multi-display triggers restrictions with 2+ displays.
- **Parked speed thresholds:** GPS < 1.5 m/s or wheel < 0.5 m/s = parked. This affects speedbump (distraction) restrictions.

### Can Safely Ignore

- **UserEducation:** All tooltip flags -- phone-internal UI.
- **Feedback, Csat, Hats:** Survey and feedback collection.
- **ConnectivityLogging:** Phone-internal telemetry.
- **Preflight:** Phone-side onboarding flow.
- **AppValidation:** Controls which 3P apps run -- phone-internal. (Note: `dhu_bypass_validation` defaults true, which is why the DHU sees all apps.)
- **WirelessProjection:** Almost entirely phone-internal WiFi/BT management. Only matters if OAP handles wireless connection setup.
- **OsDeprecation:** Phone-internal version checks.
- **Bugreport, Troubleshooter, Settings:** Phone-internal features.
- **Primes, Auth, Consent, Maps namespaces:** Google library plumbing.

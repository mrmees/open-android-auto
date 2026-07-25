# CarIntent Channel

> **Evidence boundary:** Android Auto 17.3 static APK analysis proves the
> descriptor, payload shape, and phone-side consumer chain. No framed runtime
> traffic was captured.

## Service identity and compatibility

`ChannelDescriptor` field 18 uses bit `0x20000` and identifies GAL service type 22
(`CAR_INTENT`). Field 18 is a compatible optional addition in 17.3 relative to the available 16.2 descriptor, which ends at field 17.

The descriptor evidence is static: it does not prove that a head unit advertised
the marker or that an endpoint opened in a live session.

## Incoming payload

The raw message ID is unknown. In particular, no conventional numeric assignment
is inferred from other service catalogs.

The HU -> Phone payload contains only optional string field 2, `metadata`:

```protobuf
message CarIntentMessage {
    optional string metadata = 2;
}
```

There is no field 1, wire intent-type enum, top-level or nested action enum,
acknowledgement payload, or response payload in the decoded schema.

## Phone-side consumer chain

The HU -> Phone path performs parse, log, and callback dispatch: `ixg` parses
`xgc` from the incoming buffer, logs field 2 with a fixed `NAVIGATE` label, and
invokes registered consumers. `NAVIGATE` is log text, not a decoded wire enum.

There is no acknowledgement, no response, and delivery is runtime-unverified.
The static chain does not prove live callback delivery.

## Activation boundary

The named flag `AdasRouteInfoFeature__car_intent_enabled` has a declared default of `false`.
The bounded factory path does not read that flag. Instead, descriptor presence bit `0x20000` is the actual factory gate: absence suppresses the candidate and presence permits construction.

The effective server-side flag value, descriptor advertisement, endpoint opening,
and runtime delivery were not observed.

## Evidence anchors

- Descriptor: `xlv.java:23-25,44-45`; `xgd.java:4-25`
- Factory and descriptor gate: `jnb.java:398-402`; `jae.java:133-158`;
  `iix.java:16-26`
- Service type: `ixg.java:12-14`; `rpq.java:27,82-83`
- Payload and consumer: `xgc.java:4-8,19-28`; `ixg.java:17-35`
- Named flag default: `acla.java:8-21`; `acky.java:12-13`

See [CarIntentMessage.proto](../../oaa/carintent/CarIntentMessage.proto) for the
published payload and [Channel Architecture Reference](architecture.md) for the
descriptor identity domains.

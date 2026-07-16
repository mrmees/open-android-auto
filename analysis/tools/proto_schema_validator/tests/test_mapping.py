from analysis.tools.proto_schema_validator.mapping import load_mapping


def test_load_mapping_excludes_retracted_proto_files():
    mappings = load_mapping()
    files = {mapping.proto_file for mapping in mappings}

    assert "oaa/media/MediaTrackIdentifierData.proto" not in files
    assert "oaa/control/ServiceDiscoveryRequestMessage.proto" in files

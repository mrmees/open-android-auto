PYTHON ?= python3
PYTEST := PYTHONPATH=. $(PYTHON) -m pytest
PROTO_FILES := $(shell find oaa -type f -name '*.proto' -print | sort)
OAA_DIRS := $(shell find oaa -mindepth 1 -maxdepth 1 -type d -print | sort)
RELEASE_TESTS := \
	analysis/tools/apk_indexer/tests \
	analysis/tools/proto_schema_matcher/tests \
	analysis/tools/proto_schema_validator/tests \
	analysis/tools/proto_stream_validator/tests \
	analysis/tools/coverage_dashboard/tests \
	analysis/tools/arch_link_walker/tests \
	analysis/tools/cross_link_walker/tests \
	analysis/tools/seed_import/tests/test_audit_yaml_schema_validation.py \
	analysis/tools/seed_import/tests/test_audit_yaml_tier_consistency.py \
	analysis/tools/promotion_walker/tests

.PHONY: test test-release test-integration proto-check annotation-check verify

test:
	$(PYTEST) -q -ra analysis/tools

test-release:
	$(PYTEST) -q $(RELEASE_TESTS)

test-integration:
	$(PYTEST) -q -rs -m apk_index_integration analysis/tools

proto-check:
	@descriptor="$$(mktemp)"; \
	trap 'rm -f "$$descriptor"' EXIT; \
	protoc --proto_path=. --include_imports \
	  --descriptor_set_out="$$descriptor" $(PROTO_FILES); \
	test -s "$$descriptor"

annotation-check:
	PYTHONPATH=. $(PYTHON) -m analysis.tools.seed_import.annotate --check $(OAA_DIRS)

verify: proto-check test annotation-check

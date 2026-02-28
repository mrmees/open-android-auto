PYTHONPATH := .
SOURCE ?=
ANALYSIS_ROOT ?= analysis
SCOPE ?= all

.PHONY: index benchmark
index:
	@if [ -z "$(SOURCE)" ]; then \
		echo "Usage: make -C analysis/tools/apk_indexer index SOURCE=<decompiled-apk-root> [ANALYSIS_ROOT=analysis]"; \
		exit 1; \
	fi
	cd ../../.. && PYTHONPATH=$(PYTHONPATH) python3 analysis/tools/apk_indexer/run_indexer.py --source "$(SOURCE)" --analysis-root "$(ANALYSIS_ROOT)" --scope "$(SCOPE)"

benchmark:
	@if [ -z "$(SOURCE)" ]; then \
		echo "Usage: make -C analysis/tools/apk_indexer benchmark SOURCE=<decompiled-apk-root> [ANALYSIS_ROOT=analysis] [SCOPE=all] [RUNS=3]"; \
		exit 1; \
	fi
	cd ../../.. && PYTHONPATH=$(PYTHONPATH) python3 analysis/tools/apk_indexer/benchmark.py --source "$(SOURCE)" --analysis-root "$(ANALYSIS_ROOT)" --scope "$(SCOPE)" --runs "$${RUNS:-3}"

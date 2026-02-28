from analysis.tools.apk_indexer.benchmark import benchmark_runs


def test_benchmark_returns_wall_clock_metrics():
    result = benchmark_runs([0.8, 0.7, 0.9])

    assert result["runs"] == 3
    assert "mean_seconds" in result
    assert "p95_seconds" in result

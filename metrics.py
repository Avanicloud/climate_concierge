"""
Lightweight metrics collection helpers.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, Tuple


@dataclass
class Counter:
    name: str
    description: str
    value: int = 0
    labels: Tuple[str, ...] = field(default_factory=tuple)

    def inc(self, amount: int = 1) -> None:
        self.value += amount


@dataclass
class Histogram:
    name: str
    description: str
    buckets: Tuple[float, ...]
    counts: Dict[float, int] = field(default_factory=dict)

    def observe(self, value: float) -> None:
        for bucket in sorted(self.buckets):
            if value <= bucket:
                self.counts[bucket] = self.counts.get(bucket, 0) + 1
                break
        else:
            self.counts[float("inf")] = self.counts.get(float("inf"), 0) + 1


class MetricsRegistry:
    """
    Barebones metrics registry emitting Prometheus exposition format.
    """

    def __init__(self, sink_path: Path) -> None:
        self.sink_path = sink_path
        self.counters: Dict[str, Counter] = {}
        self.histograms: Dict[str, Histogram] = {}

    def counter(self, name: str, description: str) -> Counter:
        if name not in self.counters:
            self.counters[name] = Counter(name=name, description=description)
        return self.counters[name]

    def histogram(self, name: str, description: str, buckets: Iterable[float]) -> Histogram:
        if name not in self.histograms:
            self.histograms[name] = Histogram(name=name, description=description, buckets=tuple(buckets))
        return self.histograms[name]

    def emit(self) -> None:
        lines = ["# Metrics emitted at {}".format(time.strftime("%Y-%m-%d %H:%M:%S"))]
        for counter in self.counters.values():
            lines.append(f"# HELP {counter.name} {counter.description}")
            lines.append(f"# TYPE {counter.name} counter")
            lines.append(f"{counter.name} {counter.value}")
        for hist in self.histograms.values():
            lines.append(f"# HELP {hist.name} {hist.description}")
            lines.append(f"# TYPE {hist.name} histogram")
            cumulative = 0
            for bucket in sorted(hist.buckets):
                cumulative += hist.counts.get(bucket, 0)
                lines.append(f'{hist.name}_bucket{{le="{bucket}"}} {cumulative}')
            cumulative += hist.counts.get(float("inf"), 0)
            lines.append(f'{hist.name}_bucket{{le="+Inf"}} {cumulative}')
            lines.append(f"{hist.name}_count {cumulative}")
        self.sink_path.write_text("\n".join(lines), encoding="utf-8")


def timer(registry: MetricsRegistry, histogram_name: str, description: str, buckets: Iterable[float]):
    histogram = registry.histogram(histogram_name, description, buckets)

    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                elapsed = time.perf_counter() - start
                histogram.observe(elapsed)
        return wrapper

    return decorator


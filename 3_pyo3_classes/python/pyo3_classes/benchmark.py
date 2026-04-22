"""
Benchmark harness for the persistent BST Tree ADT.

Exercises an implementation through `make_unit`, `add`, and `search` only,
so it works against any implementation that satisfies the contract.

Usage:
    from tree import Leaf
    results = benchmark(lambda k, v: Leaf(k, (v,)))
    print_results(results)
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from typing import Callable, Any

from pyo3_classes.native import make_unit

MakeUnit = Callable[[int, Any], Any]


@dataclass
class Scenario:
    name: str
    n: int
    seconds: float
    ops_per_sec: float


@dataclass
class BenchmarkResults:
    label: str
    scenarios: list[Scenario] = field(default_factory=list)


def _time(fn: Callable[[], Any]) -> float:
    """Run fn once and return wall-clock seconds elapsed."""
    start = time.perf_counter()
    fn()
    return time.perf_counter() - start


def _build(make_unit: MakeUnit, keys: list[int]):
    """Build a tree by adding keys in order; value == key."""
    t = make_unit(keys[0], keys[0])
    for k in keys[1:]:
        t = t.add(k, k)
    return t


def benchmark(
        make_unit: MakeUnit,
        sizes: tuple[int, ...] = (1_000, 10_000),
        n_queries: int = 10_000,
        seed: int = 42,
        label: str = "impl",
) -> BenchmarkResults:
    """
    Exercise a Tree implementation across several scenarios.

    Scenarios:
      - build_ascending:   insert 0..N-1 (worst case for unbalanced BSTs)
      - build_descending:  insert N-1..0 (worst case, mirrored)
      - build_random:      insert a random permutation of 0..N-1
      - search_hits:       n_queries lookups for keys known to be present
      - search_misses:     n_queries lookups for keys known to be absent
      - duplicate_adds:    N adds at a single key
      - persistent_branch: N independent one-off adds from a shared base tree

    Returns a BenchmarkResults with per-scenario timings. Every measurement
    is a single wall-clock run; use larger N or repeat externally for more
    stable numbers.
    """
    rng = random.Random(seed)
    results = BenchmarkResults(label=label)

    def record(name: str, n: int, seconds: float) -> None:
        ops = n / seconds if seconds > 0 else float("inf")
        results.scenarios.append(Scenario(name, n, seconds, ops))

    for n in sizes:
        # --- build scenarios ------------------------------------------------
        asc = list(range(n))
        desc = list(range(n - 1, -1, -1))
        rand = list(range(n))
        rng.shuffle(rand)

        record(f"build_ascending (n={n})",  n, _time(lambda: _build(make_unit, asc)))
        record(f"build_descending (n={n})", n, _time(lambda: _build(make_unit, desc)))

        # Keep the randomly-built tree for the search scenarios.
        t_random = None
        def build_random():
            nonlocal t_random
            t_random = _build(make_unit, rand)
        record(f"build_random (n={n})", n, _time(build_random))

        # --- search scenarios (against the randomly-built tree) -------------
        hit_keys = [rng.randrange(n) for _ in range(n_queries)]
        miss_keys = [n + rng.randrange(n) for _ in range(n_queries)]  # all > max key

        def do_hits():
            for k in hit_keys:
                t_random.search(k)

        def do_misses():
            for k in miss_keys:
                t_random.search(k)

        record(f"search_hits (n={n}, q={n_queries})",   n_queries, _time(do_hits))
        record(f"search_misses (n={n}, q={n_queries})", n_queries, _time(do_misses))

        # --- duplicate adds at a single key ---------------------------------
        def dup_adds():
            t = make_unit(0, 0)
            for i in range(1, n):
                t = t.add(0, i)
        record(f"duplicate_adds (n={n})", n, _time(dup_adds))

        # --- persistent branching from a shared base ------------------------
        base = t_random
        branch_keys = [-(i + 1) for i in range(n)]  # all distinct, all < min key

        def branch_off():
            for k in branch_keys:
                _ = base.add(k, k)  # discard result; we only care about cost
        record(f"persistent_branch (n={n})", n, _time(branch_off))

    return results


def print_results(results: BenchmarkResults) -> None:
    """Print a human-readable table of benchmark results."""
    print(f"\n=== Benchmark: {results.label} ===")
    name_w = max(len(s.name) for s in results.scenarios)
    print(f"{'scenario'.ljust(name_w)}  {'seconds':>10}  {'ops/sec':>14}")
    print("-" * (name_w + 2 + 10 + 2 + 14))
    for s in results.scenarios:
        print(f"{s.name.ljust(name_w)}  {s.seconds:>10.4f}  {s.ops_per_sec:>14,.0f}")


def compare(results: list[BenchmarkResults]) -> None:
    """Print a side-by-side comparison table across implementations."""
    if not results:
        return
    scenario_names = [s.name for s in results[0].scenarios]
    name_w = max(len(n) for n in scenario_names)
    col_w = max(12, max(len(r.label) for r in results) + 2)

    header = "scenario".ljust(name_w) + "  " + "  ".join(r.label.rjust(col_w) for r in results)
    print("\n" + header)
    print("-" * len(header))
    for i, name in enumerate(scenario_names):
        row = name.ljust(name_w)
        for r in results:
            row += "  " + f"{r.scenarios[i].seconds:>{col_w}.4f}"
        print(row)


if __name__ == "__main__":

    from sys import setrecursionlimit
    setrecursionlimit(10005)
    from tree import Leaf
    results_py = benchmark(lambda k, v: Leaf(k, (v,)), label="python")
    results_rs = benchmark(make_unit, label="rust")
    compare([results_py, results_rs])
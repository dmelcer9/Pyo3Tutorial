"""
Test suite for the persistent BST Tree ADT.

The suite interacts with the tree ONLY through `add` and `search`,
parameterized by a `make_unit(key, value) -> Tree` factory supplied
via a pytest fixture. Every test runs once per registered implementation.

To add a new implementation, add one entry to IMPLS.
"""

import random
import pytest

from tree import Leaf
from pyo3_classes.native import make_unit as pyo3_make_unit


# --- Implementations under test ---------------------------------------------
# Each entry maps a human-readable id to a make_unit factory.
IMPLS = {
    "python": lambda k, v: Leaf(k, (v,)),
    "rust": lambda k, v: pyo3_make_unit(k, v),
}


@pytest.fixture(params=list(IMPLS.keys()))
def make_unit(request):
    return IMPLS[request.param]
# ----------------------------------------------------------------------------


class TestUnit:
    def test_search_finds_its_key(self, make_unit):
        t = make_unit(5, "a")
        assert t.search(5) == ("a",)

    def test_search_missing_smaller(self, make_unit):
        t = make_unit(5, "a")
        assert t.search(3) == ()

    def test_search_missing_larger(self, make_unit):
        t = make_unit(5, "a")
        assert t.search(7) == ()


class TestAdd:
    def test_add_smaller_key(self, make_unit):
        t = make_unit(5, "a").add(3, "b")
        assert t.search(5) == ("a",)
        assert t.search(3) == ("b",)

    def test_add_larger_key(self, make_unit):
        t = make_unit(5, "a").add(7, "b")
        assert t.search(5) == ("a",)
        assert t.search(7) == ("b",)

    def test_add_duplicate_key(self, make_unit):
        t = make_unit(5, "a").add(5, "b")
        assert t.search(5) == ("a", "b")

    def test_add_duplicate_key_preserves_order(self, make_unit):
        t = make_unit(5, "a").add(5, "b").add(5, "c")
        assert t.search(5) == ("a", "b", "c")

    def test_add_does_not_mutate_original(self, make_unit):
        original = make_unit(5, "a")
        _ = original.add(3, "b")
        _ = original.add(7, "c")
        _ = original.add(5, "d")
        assert original.search(5) == ("a",)
        assert original.search(3) == ()
        assert original.search(7) == ()

    def test_add_returns_usable_tree(self, make_unit):
        t = make_unit(5, "a").add(3, "b").add(7, "c").add(1, "d")
        assert t.search(1) == ("d",)
        assert t.search(3) == ("b",)
        assert t.search(5) == ("a",)
        assert t.search(7) == ("c",)


class TestManyElements:
    def test_ascending_insertion(self, make_unit):
        t = make_unit(0, 0)
        for i in range(1, 100):
            t = t.add(i, i)
        for i in range(100):
            assert t.search(i) == (i,)

    def test_descending_insertion(self, make_unit):
        t = make_unit(99, 99)
        for i in range(98, -1, -1):
            t = t.add(i, i)
        for i in range(100):
            assert t.search(i) == (i,)

    def test_random_insertion(self, make_unit):
        rng = random.Random(42)
        keys = list(range(200))
        rng.shuffle(keys)
        t = make_unit(keys[0], keys[0])
        for k in keys[1:]:
            t = t.add(k, k)
        for k in range(200):
            assert t.search(k) == (k,)
        for k in (-1, 200, 1000, -100):
            assert t.search(k) == ()

    def test_duplicate_keys_interleaved(self, make_unit):
        t = make_unit(5, "a")
        t = t.add(3, "x").add(5, "b").add(7, "y").add(5, "c").add(1, "z").add(5, "d")
        assert t.search(5) == ("a", "b", "c", "d")
        assert t.search(3) == ("x",)
        assert t.search(7) == ("y",)
        assert t.search(1) == ("z",)

    def test_many_duplicates_at_same_key(self, make_unit):
        t = make_unit(42, 0)
        for i in range(1, 50):
            t = t.add(42, i)
        assert t.search(42) == tuple(range(50))

    def test_search_missing_among_many(self, make_unit):
        # Insert only even keys; every odd key should be missing.
        t = make_unit(0, 0)
        for i in range(2, 100, 2):
            t = t.add(i, i)
        for i in range(1, 100, 2):
            assert t.search(i) == ()


class TestValueTypes:
    def test_any_value_types(self, make_unit):
        sentinel = object()
        t = make_unit(1, "string")
        t = t.add(2, 42)
        t = t.add(3, None)
        t = t.add(4, [1, 2, 3])
        t = t.add(5, {"k": "v"})
        t = t.add(6, sentinel)
        assert t.search(1) == ("string",)
        assert t.search(2) == (42,)
        assert t.search(3) == (None,)
        assert t.search(4) == ([1, 2, 3],)
        assert t.search(5) == ({"k": "v"},)
        assert t.search(6) == (sentinel,)

    def test_none_value_distinguishable_from_missing(self, make_unit):
        t = make_unit(5, None)
        assert t.search(5) == (None,)  # present, value happens to be None
        assert t.search(6) == ()       # genuinely absent


class TestPersistence:
    """Adds produce new trees; old trees remain reachable and unchanged."""

    def test_branches_are_independent(self, make_unit):
        base = make_unit(5, "a").add(3, "b").add(7, "c")
        left = base.add(5, "L")
        right = base.add(5, "R")
        assert base.search(5) == ("a",)
        assert left.search(5) == ("a", "L")
        assert right.search(5) == ("a", "R")

    def test_deep_branching(self, make_unit):
        t = make_unit(50, 50)
        for i in list(range(49, 0, -1)) + list(range(51, 100)):
            t = t.add(i, i)
        branched = t.add(1000, "new")
        assert t.search(1000) == ()
        assert branched.search(1000) == ("new",)
        for i in range(1, 100):
            assert t.search(i) == (i,)
            assert branched.search(i) == (i,)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
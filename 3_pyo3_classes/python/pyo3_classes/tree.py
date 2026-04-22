import abc
from dataclasses import dataclass
from typing import Any

class Tree(abc.ABC):
    @abc.abstractmethod
    def search(self, key) -> tuple[Any, ...]:
        pass
    @abc.abstractmethod
    def add(self, key: int, value: Any) -> Tree:
        pass

@dataclass
class Leaf(Tree):
    key: int
    values: tuple[Any, ...]

    def search(self, key) -> tuple[Any, ...]:
        if self.key == key:
            return self.values
        else:
            return ()

    def add(self, key: int, value: Any) -> Tree:
        if self.key == key:
            return Leaf(key, self.values + (value,))
        elif self.key > key:
            return Node(key, Leaf(key, (value,)), self)
        else:
            return Node(self.key, self, Leaf(key, (value,)))


@dataclass
class Node(Tree):
    pivot: int
    left: Tree
    right: Tree

    def search(self, key) -> tuple[Any, ...]:
        if self.pivot >= key:
            return self.left.search(key)
        else:
            return self.right.search(key)

    def add(self, key: int, value: Any) -> Tree:
        if self.pivot >= key:
            return Node(self.pivot, self.left.add(key, value), self.right)
        else:
            return Node(self.pivot, self.left, self.right.add(key, value))

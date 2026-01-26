from collections import deque
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ezbuild.environment import Program, SharedLibrary, StaticLibrary

type Target = Program | StaticLibrary | SharedLibrary


class CyclicDependencyError(Exception):
    def __init__(self, cycle: list[str]) -> None:
        self.cycle = cycle
        super().__init__(f"Cyclic dependency detected: {' -> '.join(cycle)}")


class MissingDependencyError(Exception):
    def __init__(self, target: str, dependency: str) -> None:
        self.target = target
        self.dependency = dependency
        super().__init__(
            f"Target '{target}' depends on '{dependency}' which does not exist"
        )


class DepTree:
    def __init__(self, targets: dict[str, Target]) -> None:
        self.targets = targets
        self.graph: dict[str, list[str]] = {}
        self.in_degree: dict[str, int] = {}

    def build_graph(self) -> None:
        """Build adjacency list and in-degree count from targets."""
        # Initialize graph and in-degree for all targets
        for name in self.targets:
            self.graph[name] = []
            self.in_degree[name] = 0

        # Build edges: if A depends on B, add edge B -> A (B must be built before A)
        for name, target in self.targets.items():
            for dep in target.dependencies:
                if dep not in self.targets:
                    raise MissingDependencyError(name, dep)

                # dep -> name (dep must be built before name)
                self.graph[dep].append(name)
                self.in_degree[name] += 1

    def topological_sort(self) -> list[str]:
        """
        Perform Kahn's algorithm to get build order.
        Returns list of target names in the order they should be built.
        Raises CyclicDependencyError if a cycle is detected.
        """
        self.build_graph()

        # Start with nodes that have no dependencies
        queue: deque[str] = deque()
        for name, degree in self.in_degree.items():
            if degree == 0:
                queue.append(name)

        result: list[str] = []

        while queue:
            current = queue.popleft()
            result.append(current)

            for neighbor in self.graph[current]:
                self.in_degree[neighbor] -= 1
                if self.in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # If we didn't process all nodes, there's a cycle
        if len(result) != len(self.targets):
            cycle = self._find_cycle()
            raise CyclicDependencyError(cycle)

        return result

    def _find_cycle(self) -> list[str]:
        """Find and return a cycle in the graph for error reporting."""
        # Find a node that's still in the cycle (in_degree > 0)
        remaining = {name for name, deg in self.in_degree.items() if deg > 0}

        if not remaining:
            return []

        # DFS to find the cycle
        visited: set[str] = set()
        path: list[str] = []
        path_set: set[str] = set()

        def dfs(node: str) -> list[str] | None:
            if node in path_set:
                # Found cycle, extract it
                cycle_start = path.index(node)
                return [*path[cycle_start:], node]

            if node in visited or node not in remaining:
                return None

            visited.add(node)
            path.append(node)
            path_set.add(node)

            # Check dependencies (reverse edges for finding cycle)
            target = self.targets[node]
            for dep in target.dependencies:
                if dep in remaining:
                    result = dfs(dep)
                    if result:
                        return result

            path.pop()
            path_set.remove(node)
            return None

        for start in remaining:
            cycle = dfs(start)
            if cycle:
                return cycle

        return list(remaining)

    def get_build_order(self) -> list[Target]:
        """
        Get the ordered list of targets to build.
        Returns the actual target objects in build order.
        """
        order = self.topological_sort()
        return [self.targets[name] for name in order]

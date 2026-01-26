import pytest

from ezbuild.dep_tree import CyclicDependencyError, DepTree, MissingDependencyError
from ezbuild.environment import Program, SharedLibrary, StaticLibrary
from ezbuild.language import Language


def test_cyclic_dependency_error_message() -> None:
    error = CyclicDependencyError(["a", "b", "c", "a"])
    assert error.cycle == ["a", "b", "c", "a"]
    assert "a -> b -> c -> a" in str(error)
    assert "Cyclic dependency detected" in str(error)


def test_missing_dependency_error_message() -> None:
    error = MissingDependencyError("myapp", "nonexistent")
    assert error.target == "myapp"
    assert error.dependency == "nonexistent"
    assert "myapp" in str(error)
    assert "nonexistent" in str(error)
    assert "does not exist" in str(error)


def test_deptree_init() -> None:
    targets: dict[str, Program | StaticLibrary | SharedLibrary] = {}
    tree = DepTree(targets)
    assert tree.targets is targets
    assert tree.graph == {}
    assert tree.in_degree == {}


def test_deptree_single_target_no_deps() -> None:
    prog = Program(name="app", languages=[Language.C], sources=["main.c"])
    tree = DepTree({"app": prog})
    order = tree.topological_sort()
    assert order == ["app"]


def test_deptree_two_targets_no_deps() -> None:
    prog1 = Program(name="app1", languages=[Language.C], sources=["app1.c"])
    prog2 = Program(name="app2", languages=[Language.C], sources=["app2.c"])
    tree = DepTree({"app1": prog1, "app2": prog2})
    order = tree.topological_sort()
    assert set(order) == {"app1", "app2"}
    assert len(order) == 2


def test_deptree_simple_dependency() -> None:
    lib = StaticLibrary(name="mylib", languages=[Language.C], sources=["lib.c"])
    prog = Program(
        name="app",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["mylib"],
    )
    tree = DepTree({"app": prog, "mylib": lib})
    order = tree.topological_sort()
    assert order.index("mylib") < order.index("app")


def test_deptree_chain_dependency() -> None:
    lib1 = StaticLibrary(name="lib1", languages=[Language.C], sources=["lib1.c"])
    lib2 = StaticLibrary(
        name="lib2",
        languages=[Language.C],
        sources=["lib2.c"],
        dependencies=["lib1"],
    )
    prog = Program(
        name="app",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["lib2"],
    )
    tree = DepTree({"app": prog, "lib1": lib1, "lib2": lib2})
    order = tree.topological_sort()
    assert order.index("lib1") < order.index("lib2")
    assert order.index("lib2") < order.index("app")


def test_deptree_diamond_dependency() -> None:
    base = StaticLibrary(name="base", languages=[Language.C], sources=["base.c"])
    left = StaticLibrary(
        name="left",
        languages=[Language.C],
        sources=["left.c"],
        dependencies=["base"],
    )
    right = StaticLibrary(
        name="right",
        languages=[Language.C],
        sources=["right.c"],
        dependencies=["base"],
    )
    prog = Program(
        name="app",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["left", "right"],
    )
    tree = DepTree({"app": prog, "base": base, "left": left, "right": right})
    order = tree.topological_sort()
    assert order.index("base") < order.index("left")
    assert order.index("base") < order.index("right")
    assert order.index("left") < order.index("app")
    assert order.index("right") < order.index("app")


def test_deptree_missing_dependency() -> None:
    prog = Program(
        name="app",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["nonexistent"],
    )
    tree = DepTree({"app": prog})
    with pytest.raises(MissingDependencyError) as exc_info:
        tree.topological_sort()
    assert exc_info.value.target == "app"
    assert exc_info.value.dependency == "nonexistent"


def test_deptree_cyclic_dependency_self() -> None:
    prog = Program(
        name="app",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["app"],
    )
    tree = DepTree({"app": prog})
    with pytest.raises(CyclicDependencyError) as exc_info:
        tree.topological_sort()
    assert "app" in exc_info.value.cycle


def test_deptree_cyclic_dependency_two_nodes() -> None:
    lib1 = StaticLibrary(
        name="lib1",
        languages=[Language.C],
        sources=["lib1.c"],
        dependencies=["lib2"],
    )
    lib2 = StaticLibrary(
        name="lib2",
        languages=[Language.C],
        sources=["lib2.c"],
        dependencies=["lib1"],
    )
    tree = DepTree({"lib1": lib1, "lib2": lib2})
    with pytest.raises(CyclicDependencyError) as exc_info:
        tree.topological_sort()
    assert "lib1" in exc_info.value.cycle
    assert "lib2" in exc_info.value.cycle


def test_deptree_cyclic_dependency_three_nodes() -> None:
    lib1 = StaticLibrary(
        name="lib1",
        languages=[Language.C],
        sources=["lib1.c"],
        dependencies=["lib3"],
    )
    lib2 = StaticLibrary(
        name="lib2",
        languages=[Language.C],
        sources=["lib2.c"],
        dependencies=["lib1"],
    )
    lib3 = StaticLibrary(
        name="lib3",
        languages=[Language.C],
        sources=["lib3.c"],
        dependencies=["lib2"],
    )
    tree = DepTree({"lib1": lib1, "lib2": lib2, "lib3": lib3})
    with pytest.raises(CyclicDependencyError):
        tree.topological_sort()


def test_deptree_build_graph_sets_in_degree() -> None:
    lib = StaticLibrary(name="mylib", languages=[Language.C], sources=["lib.c"])
    prog = Program(
        name="app",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["mylib"],
    )
    tree = DepTree({"app": prog, "mylib": lib})
    tree.build_graph()
    assert tree.in_degree["mylib"] == 0
    assert tree.in_degree["app"] == 1


def test_deptree_build_graph_sets_adjacency() -> None:
    lib = StaticLibrary(name="mylib", languages=[Language.C], sources=["lib.c"])
    prog = Program(
        name="app",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["mylib"],
    )
    tree = DepTree({"app": prog, "mylib": lib})
    tree.build_graph()
    assert "app" in tree.graph["mylib"]
    assert tree.graph["app"] == []


def test_deptree_get_build_order_returns_targets() -> None:
    lib = StaticLibrary(name="mylib", languages=[Language.C], sources=["lib.c"])
    prog = Program(
        name="app",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["mylib"],
    )
    tree = DepTree({"app": prog, "mylib": lib})
    order = tree.get_build_order()
    assert len(order) == 2
    assert order[0] is lib
    assert order[1] is prog


def test_deptree_get_build_order_empty() -> None:
    tree = DepTree({})
    order = tree.get_build_order()
    assert order == []


def test_deptree_multiple_dependencies() -> None:
    lib1 = StaticLibrary(name="lib1", languages=[Language.C], sources=["lib1.c"])
    lib2 = StaticLibrary(name="lib2", languages=[Language.C], sources=["lib2.c"])
    lib3 = StaticLibrary(name="lib3", languages=[Language.C], sources=["lib3.c"])
    prog = Program(
        name="app",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["lib1", "lib2", "lib3"],
    )
    tree = DepTree({"app": prog, "lib1": lib1, "lib2": lib2, "lib3": lib3})
    order = tree.topological_sort()
    assert order.index("lib1") < order.index("app")
    assert order.index("lib2") < order.index("app")
    assert order.index("lib3") < order.index("app")


def test_deptree_with_shared_library() -> None:
    lib = SharedLibrary(name="mylib", languages=[Language.C], sources=["lib.c"])
    prog = Program(
        name="app",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["mylib"],
    )
    tree = DepTree({"app": prog, "mylib": lib})
    order = tree.get_build_order()
    assert order[0] is lib
    assert order[1] is prog


def test_deptree_mixed_library_types() -> None:
    static = StaticLibrary(name="static", languages=[Language.C], sources=["static.c"])
    shared = SharedLibrary(
        name="shared",
        languages=[Language.C],
        sources=["shared.c"],
        dependencies=["static"],
    )
    prog = Program(
        name="app",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["shared"],
    )
    tree = DepTree({"app": prog, "static": static, "shared": shared})
    order = tree.topological_sort()
    assert order.index("static") < order.index("shared")
    assert order.index("shared") < order.index("app")


def test_deptree_find_cycle_empty_remaining() -> None:
    tree = DepTree({})
    tree.graph = {}
    tree.in_degree = {}
    cycle = tree._find_cycle()
    assert cycle == []

from ezbuild import Language, Program, SharedLibrary, StaticLibrary
from ezbuild.commands.build import _collect_public_defines


def test_collect_public_defines_no_dependencies() -> None:
    target = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "myapp": target,
    }
    public_defines = _collect_public_defines(target, targets)
    assert public_defines == []


def test_collect_public_defines_single_dependency() -> None:
    lib = StaticLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        public_defines=["LIB_VERSION=1.0"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["mylib"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "mylib": lib,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert public_defines == ["LIB_VERSION=1.0"]


def test_collect_public_defines_multiple_dependencies() -> None:
    lib1 = StaticLibrary(
        name="lib1",
        languages=[Language.C],
        sources=["lib1.c"],
        public_defines=["LIB1_VERSION=1.0"],
    )
    lib2 = StaticLibrary(
        name="lib2",
        languages=[Language.C],
        sources=["lib2.c"],
        public_defines=["LIB2_VERSION=2.0"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["lib1", "lib2"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "lib1": lib1,
        "lib2": lib2,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert sorted(public_defines) == ["LIB1_VERSION=1.0", "LIB2_VERSION=2.0"]


def test_collect_public_defines_transitive_dependencies() -> None:
    lib1 = StaticLibrary(
        name="lib1",
        languages=[Language.C],
        sources=["lib1.c"],
        public_defines=["LIB1_VERSION=1.0"],
    )
    lib2 = StaticLibrary(
        name="lib2",
        languages=[Language.C],
        sources=["lib2.c"],
        dependencies=["lib1"],
        public_defines=["LIB2_VERSION=2.0"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["lib2"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "lib1": lib1,
        "lib2": lib2,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert sorted(public_defines) == ["LIB1_VERSION=1.0", "LIB2_VERSION=2.0"]


def test_collect_public_defines_mixed_types() -> None:
    lib1 = StaticLibrary(
        name="lib1",
        languages=[Language.C],
        sources=["lib1.c"],
        public_defines=["STATIC_DEFINE=1"],
    )
    lib2 = SharedLibrary(
        name="lib2",
        languages=[Language.C],
        sources=["lib2.c"],
        public_defines=["SHARED_DEFINE=2"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["lib1", "lib2"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "lib1": lib1,
        "lib2": lib2,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert sorted(public_defines) == ["SHARED_DEFINE=2", "STATIC_DEFINE=1"]


def test_collect_public_defines_no_public_defines() -> None:
    lib = StaticLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["mylib"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "mylib": lib,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert public_defines == []


def test_collect_public_defines_private_defines_not_collected() -> None:
    lib = StaticLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        defines=["PRIVATE_DEFINE=1"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["mylib"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "mylib": lib,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert public_defines == []


def test_collect_public_defines_both_public_and_private() -> None:
    lib = StaticLibrary(
        name="mylib",
        languages=[Language.C],
        sources=["lib.c"],
        defines=["PRIVATE_DEFINE=1"],
        public_defines=["PUBLIC_DEFINE=2"],
    )
    app = Program(
        name="myapp",
        languages=[Language.C],
        sources=["main.c"],
        dependencies=["mylib"],
    )
    targets: dict[str, Program | SharedLibrary | StaticLibrary] = {
        "mylib": lib,
        "myapp": app,
    }
    public_defines = _collect_public_defines(app, targets)
    assert public_defines == ["PUBLIC_DEFINE=2"]

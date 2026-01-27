from dataclasses import dataclass, field
from shutil import which
from sys import platform
from typing import TYPE_CHECKING, Any

from typer import Exit

from ezbuild import pkg_config
from ezbuild.log import debug, error

if TYPE_CHECKING:
    from ezbuild.language import Language


@dataclass
class SystemLibrary:
    name: str
    compile_flags: list[str] = field(default_factory=list)
    link_flags: list[str] = field(default_factory=list)


@dataclass
class Program:
    name: str = field(default_factory=str)
    languages: list[Language] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    system_dependencies: list[str] = field(default_factory=list)


@dataclass
class StaticLibrary:
    name: str = field(default_factory=str)
    languages: list[Language] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    system_dependencies: list[str] = field(default_factory=list)


@dataclass
class SharedLibrary:
    name: str = field(default_factory=str)
    languages: list[Language] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    dependencies: list[str] = field(default_factory=list)
    system_dependencies: list[str] = field(default_factory=list)


@dataclass
class Environment:
    programs: list[Program] = field(default_factory=list)
    static_libraries: list[StaticLibrary] = field(default_factory=list)
    shared_libraries: list[SharedLibrary] = field(default_factory=list)
    _vars: dict[str, object] = field(default_factory=dict)

    def __getitem__(self, key: str) -> Any:
        return self._vars.get(key)

    def __setitem__(self, key: str, value: object) -> None:
        self._vars[key] = value

    def __contains__(self, key: str) -> bool:
        return key in self._vars

    def Program(
        self,
        name: str,
        languages: list[Language],
        sources: list[str],
        dependencies: None | list[str] = None,
        system_dependencies: None | list[str] = None,
    ) -> Program:
        program = Program(
            name=name,
            languages=languages,
            sources=sources,
            dependencies=dependencies or [],
            system_dependencies=system_dependencies or [],
        )
        self.programs.append(program)
        return program

    def StaticLibrary(
        self,
        name: str,
        languages: list[Language],
        sources: list[str],
        dependencies: None | list[str] = None,
        system_dependencies: None | list[str] = None,
    ) -> StaticLibrary:
        static_library = StaticLibrary(
            name=name,
            languages=languages,
            sources=sources,
            dependencies=dependencies or [],
            system_dependencies=system_dependencies or [],
        )
        self.static_libraries.append(static_library)
        return static_library

    def SharedLibrary(
        self,
        name: str,
        languages: list[Language],
        sources: list[str],
        dependencies: None | list[str] = None,
        system_dependencies: None | list[str] = None,
    ) -> SharedLibrary:
        shared_library = SharedLibrary(
            name=name,
            languages=languages,
            sources=sources,
            dependencies=dependencies or [],
            system_dependencies=system_dependencies or [],
        )
        self.shared_libraries.append(shared_library)
        return shared_library

    def ensure_cc(self) -> None:
        if not self["CC"]:
            if platform == "linux":
                debug("CC is not set, using cc")

                cc_path = which("cc")
                if not cc_path:
                    error("cc not found")
                    raise Exit

                self["CC"] = cc_path
            else:
                error("Unsupported platform")
                raise Exit
        else:
            debug("CC is set")

    def ensure_ccld(self) -> None:
        if not self["CCLD"]:
            debug("CCLD is not set, using CC")
            self["CCLD"] = self["CC"]
        else:
            debug("CCLD is set")

    def ensure_cxx(self) -> None:
        if not self["CC"]:
            error("CXX requires CC")
            raise Exit

        if not self["CXX"]:
            if platform == "linux":
                debug("CXX is not set, using c++")

                cxx_path = which("c++")
                if not cxx_path:
                    error("c++ not found")
                    raise Exit

                self["CXX"] = cxx_path
            else:
                error("Unsupported platform")
                raise Exit
        else:
            debug("CXX is set")

    def ensure_cxxld(self) -> None:
        if not self["CCLD"]:
            error("CXXLD requires CCLD")
            raise Exit

        if not self["CXXLD"]:
            debug("CXXLD is not set, using CXX")
            self["CXXLD"] = self["CXX"]
        else:
            debug("CXXLD is set")

    def ensure_ar(self) -> None:
        if not self["AR"]:
            if platform == "linux":
                debug("AR is not set, using ar")

                ar_path = which("ar")
                if not ar_path:
                    error("ar not found")
                    raise Exit

                self["AR"] = ar_path
            else:
                error("Unsupported platform")
                raise Exit
        else:
            debug("AR is set")

    def ensure_ranlib(self) -> None:
        if not self["AR"]:
            error("AR requires AR")
            raise Exit

        if not self["RANLIB"]:
            if platform == "linux":
                debug("RANLIB is not set, using ranlib")

                ranlib_path = which("ranlib")
                if not ranlib_path:
                    error("ranlib not found")
                    raise Exit

                self["RANLIB"] = ranlib_path
            else:
                error("Unsupported platform")
                raise Exit
        else:
            debug("RANLIB is set")

    def ensure_pkg_config(self) -> None:
        if platform not in ["linux", "darwin"]:
            error("pkg-config is only supported on Unix systems")
            raise Exit

        if not which("pkg-config"):
            error("pkg-config not found")
            raise Exit
        else:
            debug("pkg-config is available")

    def find_library(
        self,
        package: str,
    ) -> tuple[bool, SystemLibrary | None]:
        debug(f"Checking for library: {package}")

        if not pkg_config.is_available():
            debug("pkg-config is not available")
            return False, None

        try:
            system_lib = pkg_config.query_package(package)
            debug(f"Found library: {package}")
            return True, system_lib
        except RuntimeError:
            debug(f"Library not found: {package}")
            return False, None

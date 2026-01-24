class CompileCommand(dict[str, str]):
    def __init__(
        self,
        directory: str = "",
        command: str = "",
        file: str = "",
        output: str = "",
    ) -> None:
        super().__init__(directory=directory, command=command, file=file, output=output)

    @property
    def directory(self) -> str:
        return self["directory"]

    @directory.setter
    def directory(self, value: str) -> None:
        self["directory"] = value

    @property
    def command(self) -> str:
        return self["command"]

    @command.setter
    def command(self, value: str) -> None:
        self["command"] = value

    @property
    def file(self) -> str:
        return self["file"]

    @file.setter
    def file(self, value: str) -> None:
        self["file"] = value

    @property
    def output(self) -> str:
        return self["output"]

    @output.setter
    def output(self, value: str) -> None:
        self["output"] = value

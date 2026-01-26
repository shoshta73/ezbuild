from os import environ


class PythonEnvironment:
    _debug: bool = environ.get("EZBUILD_DEBUG") == "1"

    @classmethod
    def debug(cls) -> bool:
        return cls._debug

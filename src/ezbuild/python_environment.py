class PythonEnvironment:
    _debug: bool = __debug__

    @classmethod
    def debug(cls) -> bool:
        return cls._debug

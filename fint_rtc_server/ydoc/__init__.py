from .yfile import YFile
from .ynotebok import YNotebook

ydocs = {"file": YFile, "notebook": YNotebook}

__all__ = ["YFile", "YNotebook", "ydocs"]

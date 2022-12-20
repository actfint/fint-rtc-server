from .yfile import YFile
from .ynotebook import YNotebook

ydocs = {"file": YFile, "notebook": YNotebook}

__all__ = ["YFile", "YNotebook", "ydocs"]

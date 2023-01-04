#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

from .yfile import YFile
from .ynotebook import YNotebook

ydocs = {"file": YFile, "notebook": YNotebook}

__all__ = ["YFile", "YNotebook", "ydocs"]

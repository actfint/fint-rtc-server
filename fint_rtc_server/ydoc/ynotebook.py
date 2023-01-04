#  Copyright (c) 2023 actfint
#  Licensed under the BSD 3-Clause License
#  Created by @Wh1isper 2023/1/4

import copy
from typing import Any, Dict
from uuid import uuid4

import jupyter_ydoc
import y_py as Y
from jupyter_ydoc import YNotebook as JYNotebook
from packaging import version


class CompatibleYNotebook(JYNotebook):
    def create_ycell(self, value: Dict[str, Any]) -> Y.YMap:
        # This is a patch for https://github.com/jupyter-server/jupyter_ydoc/issues/111
        """
        Creates YMap with the content of the cell.

        :param value: A cell.
        :type value: Dict[str, Any]

        :return: A new cell.
        :rtype: :class:`y_py.YMap`
        """
        cell = copy.deepcopy(value)
        if "id" not in cell:
            cell["id"] = str(uuid4())
        cell_type = cell["cell_type"]
        cell_source = cell["source"]
        cell_source = "".join(cell_source) if isinstance(cell_source, list) else cell_source
        cell["source"] = Y.YText(cell_source)
        cell["metadata"] = Y.YMap(cell.get("metadata", {}))

        if cell_type in ("raw", "markdown"):
            if "attachments" in cell and not cell["attachments"]:
                del cell["attachments"]
        elif cell_type == "code":
            cell["outputs"] = Y.YArray(cell.get("outputs", []))

        return Y.YMap(cell)


need_patch = version.parse(jupyter_ydoc.__version__) <= version.parse("0.2.2")

if need_patch:
    YNotebook = CompatibleYNotebook
else:
    YNotebook = JYNotebook

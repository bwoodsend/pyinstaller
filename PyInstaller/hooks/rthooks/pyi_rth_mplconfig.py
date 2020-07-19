#-----------------------------------------------------------------------------
# Copyright (c) 2013-2020, PyInstaller Development Team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: Apache-2.0
#-----------------------------------------------------------------------------


import os
import sys

path = os.path.join(sys._MEIPASS, 'matplotlib/mpl-cfg')
if not os.path.exists(path):
    # In earlier version of matplotlib (3.0.3) the config folder may be empty.
    # PyInstaller doesn't copy empty folders so in this case
    # ``matplotlib/mpl-cfg`` will not exist in the PyInstaller build causing
    # matplotlib to rais a ``FileNotFoundError``.
    # Ensure the config folder is made (even if it's empty).
    os.mkdir(path)
os.environ['MPLCONFIGDIR'] = path

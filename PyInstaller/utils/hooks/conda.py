#-----------------------------------------------------------------------------
# Copyright (c) 2005-2020, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------

# language=rst
"""
Additional helper methods for working specifically with Anaconda distributions
are found at :attr:`PyInstaller.util.hooks.conda_support`. These functions find
and parse the distribution metadata from json files located in the
``conda-meta`` directory.

.. versionadded:: 4.1.0

This module is available only if run inside a Conda environment. Usage of this
module should therefore be wrapped in a conditional clause::

    from PyInstaller.utils.hooks import is_pure_conda

    if is_pure_conda:
        from PyInstaller.utils.hooks import conda_support

        # Code goes here. e.g.
        binaries = conda_support.collect_dynamic_libs("numpy")
        ...

Packages are all referenced by the *distribution name* you use to install it,
rather than the *package name* you import it with. i.e Use
``search_distribution("pillow")`` instead of ``search_distribution("PIL")``.

"""

import sys
from pathlib import Path
import json

from PyInstaller import compat
from PyInstaller.log import logger

# Conda virtual environments each get their own copy of `conda-meta` so the use
# of `sys.prefix` instead of `sys.base_prefix`, `sys.real_prefix`  or anything
# from our `compat` module is intentional.
CONDA_ROOT = Path(sys.prefix)
CONDA_META_DIR = CONDA_ROOT / "conda-meta"


def search_distribution(name):
    """
     Finds and extracts the distribution metadata from the distribution json
     files in the ``conda-meta`` directory.

    :param name: Distribution name.
    :type name: str
    :return: The json-parsed distribution information.
    :rtype: dict
    :raises: ModuleNotFoundError: If **distribution** was not installed with
             conda.

    This function collects a single distribution. But this is generally
    discouraged due to Conda's often moving distribution contents to
    base-distributions. e.g. *numpy* itself is empty but depends on
    *numpy-base*, which contains the python files and depends on *mkl* and
    *blas* which contain the DLLs. Instead use :meth:`walk_dependency_tree`.

    """
    # Locate the right json. The name format is:
    #   [distribution name]-[version][ugly build # hash].json

    # The json name can't be determined exactly so they must be glob searched:
    for path in CONDA_META_DIR.glob(name + "-*.json"):
        # But this will include distributions with a prefix of 'name'.
        # e.g. 'numpy' would also pick up 'numpy-base'.
        dic = json.loads(path.read_text())
        if name == dic["name"]:
            # Read the json to check we've found the right one.
            # XXX: Maybe we should make this case and '-'/'_' insensitive?
            return dic
    raise ModuleNotFoundError("Distribution {} is either not installed or was"
                              " not installed using Conda.".format(name))


def walk_dependency_tree(initial, excludes=None):
    """
    Collect metadata for a distribution and all direct and indirect
    dependencies of that distribution.

    :param initial: Distribution name to collect from.
    :type initial: str
    :param excludes: Distributions to exclude, defaults to ``None``.
    :type excludes: iterable  of str, optional
    :return: A **distribution_name** to **metadata** mapping where **metadata**
             is the output of ``search_distribution(distribution_name)``.
    :rtype: dict

    """
    if excludes is not None:
        excludes = set(excludes)

    # Rather than use true recursion, mimic it with a to-do queue.
    from collections import deque
    done = {}
    names_to_do = deque([initial])

    while names_to_do:
        # Grab a distribution name from the to-do list.
        name = names_to_do.pop()

        try:
            # Collect and save it's metadata.
            done[name] = distribution = search_distribution(name)
            logger.debug("Collected Conda distribution '%s', a dependency of "
                         "'%s'." % (name, initial))
        except ModuleNotFoundError:
            logger.warning(
                "Conda distribution '%s', dependency of '%s', was not found. "
                "If you installed this distribution with pip then you may "
                "ignore this warning." % (name, initial))
            continue

        # For each dependency:
        for _name in distribution["depends"]:

            if _name in done:
                # Skip anything already done.
                continue

            if _name == name:
                # Avoid infinite recursion if a distribution depends on itself.
                # This probably will ever happen but I certainly wouldn't
                # chance it.
                continue

            if excludes is not None and _name in excludes:
                # Don't recurse to excluded dependencies.
                continue

            names_to_do.append(_name)
    return done


if compat.is_win:
    lib_dir = Path("Library", "bin")
else:
    lib_dir = Path("lib")


def collect_dynamic_libs(name,
                         dest=".",
                         recurse_dependencies=True,
                         excludes=None):
    """
    Collect DLLs for distribution **name**.

    :param name: The distribution's project-name.
    :type name: str
    :param dest: Target destination, defaults to ``'.'``.
    :type dest: str, optional
    :param recurse_dependencies: Recursively collect libs for dependent
                                 distributions (recommended).
    :type recurse_dependencies: bool, optional
    :param excludes: Dependent distributions to skip, defaults to ``None``.
    :type excludes: iterable, optional
    :return: List of DLLs in PyInstaller's ``(source, dest)`` format.
    :rtype: list

    This collects libraries only from Conda's shared ``lib`` (Unix) or
    ``Library/bin`` (Windows) folders. To collect from inside a distribution's
    installation use the regular
    :meth:`PyInstaller.utils.hooks.collect_collect_dynamic_libs`.

    """
    files = []

    if recurse_dependencies:
        distributions = walk_dependency_tree(name, excludes).values()
    else:
        distributions = [search_distribution(name)]

    for distribution in distributions:
        for file in distribution["files"]:
            # A file is classified as a DLL if it lives inside the dedicated
            # ``lib_dir`` DLL folder.
            if Path(file).parent == lib_dir:
                files.append((str(CONDA_ROOT / file), dest))

    return files

#-----------------------------------------------------------------------------
# Copyright (c) 2013-2021, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------


"""
Automatically build spec files containing a description of the project
"""

import click
import os

from PyInstaller.building import makespec
import PyInstaller.log


def verbose_makespec(*args, **kwargs):
    name = makespec.main(*args, **kwargs)
    print('Wrote %s' % name)
    print(f'Now run pyinstaller {os.path.relpath(name)} to build the executable')


def run():
    main = makespec.__add_options(verbose_makespec)
    # PyInstaller.log.__add_options(p)  worry about this later...
    main = click.argument('scripts', nargs=-1, required=True)(main)

    # args = p.parse_args()
    # PyInstaller.log.__process_options(p, args)

    # Split pathex by using the path separator
    # temppaths = args.pathex[:]
    # args.pathex = []
    # for p in temppaths:
    #     args.pathex.extend(p.split(os.pathsep))

    try:
        name = main(standalone_mode=True)
    except KeyboardInterrupt:
        raise SystemExit("Aborted by user request.")


if __name__ == '__main__':
    run()

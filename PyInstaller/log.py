# -----------------------------------------------------------------------------
# Copyright (c) 2013-2021, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
# -----------------------------------------------------------------------------


"""
Logging module for PyInstaller
"""

__all__ = ['getLogger', 'INFO', 'WARN', 'DEBUG', 'TRACE', 'ERROR', 'FATAL']

import logging
from logging import getLogger, INFO, WARN, DEBUG, ERROR, FATAL

import click

TRACE = logging.TRACE = DEBUG - 5
logging.addLevelName(TRACE, 'TRACE')

FORMAT = '%(relativeCreated)d %(levelname)s: %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)
logger = getLogger('PyInstaller')


def __add_options(func):
    levels = ('TRACE', 'DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL')
    return click.option('--log-level',
                        type=click.Choice(levels),
                        default='INFO',
                        help=f"Amount of detail in build-time console "
                             f"messages. LEVEL may be one of "
                             f"{', '.join(levels)}  (default: %%(default)s)."
                        )(func)


def __process_options(opts):
    try:
        level = getattr(logging, opts.loglevel.upper())
    except AttributeError:
        raise click.ClickException('Unknown log level `%s`' % opts.loglevel)
    else:
        logger.setLevel(level)

#-----------------------------------------------------------------------------
# Copyright (c) 2005-2021, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License (version 2
# or later) with exception for distributing the bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#
# SPDX-License-Identifier: (GPL-2.0-or-later WITH Bootloader-exception)
#-----------------------------------------------------------------------------


import pytest
from click import ClickException

from PyInstaller.building.makespec import __add_options as add_options, main
from PyInstaller.building.makespec import add_command_sep as SEP


# A whitelist of valid argument names.
ARG_NAMES = set(main.__code__.co_varnames[:main.__code__.co_argcount])

# Click does have a special `click.testing` module but it's pretty inadequate.


class DumpOptions(object):
    def main(self, **kwargs):
        for (key, val) in kwargs.items():
            # Catch any wrong argument names.
            if key not in ARG_NAMES:
                raise AssertionError(f"Invalid parameter name '{key}'. "
                                     f"Must be one of {sorted(ARG_NAMES)}.")
        self.options = kwargs


def run(*args):
    """Mimic a CLI run.

    Arguments:
        args (str): Arguments to be passed to the CLI.
    Returns:
        dict: Parsed options.

    The CLI parser has only the options which are shared between
    ``pyi-makespec`` and ``pyinstaller``. i.e. No positional **scripts**
    argument.

    """
    options = DumpOptions()
    add_options(options.main)(args, standalone_mode=False)
    return options.options


def test_defaults():
    # This will fail if there are any click arguments with incorrect name /
    # argument targets.
    args = run()

    # These are the defaults from the original argparse CLI parser.
    # Assert that they are unchanged.
    assert args['binaries'] == ()
    assert args['bootloader_ignore_signals'] is False
    assert args['bundle_identifier'] is None
    assert args['console'] is True
    assert args['datas'] == ()
    assert args['debug'] == ()
    assert args['excludes'] == ()
    assert args['hiddenimports'] == ()
    assert args['hookspath'] == ()
    assert args['icon_file'] is None
    assert args['key'] is None
    assert args['manifest'] is None
    assert args['name'] is None
    assert args['noupx'] is False
    assert args['onefile'] is False
    assert args['pathex'] == ()
    assert args['resources'] == ()
    assert args['runtime_hooks'] == ()
    assert args['runtime_tmpdir'] is None
    assert args['specpath'] is None
    assert args['strip'] is False
    assert args['uac_admin'] is False
    assert args['uac_uiaccess'] is False
    assert args['upx_exclude'] == ()
    assert args['version_file'] is None
    assert args['win_no_prefer_redirects'] is False
    assert args['win_private_assemblies'] is False


# Test the more customised click options.

def test_console():
    # -w and -c oppose each other.
    assert run("--windowed")["console"] is False
    assert run("-w")["console"] is False
    assert run("--console")["console"] is True
    assert run("-c")["console"] is True


def test_binaries_datas():
    # --add-data and --add-binary have a special parser to unpack the : or ;
    # separator.
    assert run(f"--add-data=src{SEP}dest")["datas"] == (("src", "dest"),)
    assert run(f"--add-binary=src{SEP}dest")["binaries"] == (("src", "dest"),)

    with pytest.raises(ClickException, match=f"Wrong syntax.* SRC{SEP}DEST"):
        run("--add-data=src")
    with pytest.raises(ClickException, match="both SRC and DEST"):
        run(f"--add-data=src{SEP}")
    with pytest.raises(ClickException):
        run(f"--add-data=src{';' if SEP == ':' else ':'}dest")


def test_onefile():
    # --onefile and --onedir oppose each other.
    assert run("--onedir")["onefile"] is False
    assert run("--onefile")["onefile"] is True

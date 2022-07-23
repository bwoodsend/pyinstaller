.. TODO: incorporate test/README.md

.. _running-the-test-suite:

Running the Test Suite
===========================

To run the test-suite, please proceed as follows.

1. If you don't have a git clone of PyInstaller, first fetch the current
   development head, either using pip, …::

     pip download --no-deps https://github.com/pyinstaller/pyinstaller/archive/develop.zip
     unzip develop.zip
     cd pyinstaller-develop/

   … or using git::

     git clone https://github.com/pyinstaller/pyinstaller.git
     cd pyinstaller

2. Then setup a fresh virtualenv_ for running the test suite in and install
   all required tools::

     pip install --user virtualenv
     virtualenv /tmp/venv
     . /tmp/venv/bin/activate
     pip install -r test-requirements.txt

3. To run a single test use e.g.::

    pytest tests/unit -k test_collect_submod_all_included

4. Run the test-suite::

     pytest tests/unit tests/functional

   This only runs the tests for the core functionality and some packages from
   the Python standard library.

5. To test the hooks for 3rd party libraries that PyInstaller contains, those
   libraries must also be installed. Generally, it's only necessary to install
   the library whose hook you are currently writing/fixing. Should you want to
   test them all then run::

     pip install -U -r tests/libraries-requirements.txt
     pytest tests/unit tests/functional

.. note:

   This section is still incomplete. For now please refer to the
   |tests/README|_ file.

.. |tests/README| replace:: ``tests/README.md``
.. _tests/README: https://github.com/pyinstaller/pyinstaller/blob/develop/tests/README.md


To learn how we run the test-suite in the continuous integration tests please
have a look at |.travis.yml|_ (for GNU/Linux and macOS) and |appveyor.yml|_
(for Windows).


.. |.travis.yml| replace:: ``.travis.yml``
.. _.travis.yml: https://github.com/pyinstaller/pyinstaller/blob/develop/.travis.yml

.. |appveyor.yml| replace:: ``appveyor.yml``
.. _appveyor.yml: https://github.com/pyinstaller/pyinstaller/blob/develop/appveyor.yml

.. include:: ../_common_definitions.txt

.. Emacs config:
 Local Variables:
 mode: rst
 ispell-local-dictionary: "american"
 End:

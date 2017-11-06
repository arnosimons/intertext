======================================================
Intertext - A tool for the relational analysis of text
======================================================

``intertext`` is a Python package for performing relational analysis of texts. It combines bibliometric (network) analysis and natural language processing (NLP). ``intertext`` can also link to your Zotero library to load and upload data.


Installation
------------
Install the latest version of ``intertext`` via pip from github:

.. code-block:: console

    $ pip install git+https://github.com/arnosimons/intertext.git


Or install the latest release via ``pip``:

.. code-block:: console

    $ pip install intertext

Otherwise, you can download and unzip the source ``tar.gz`` from  PyPi_, then install manually:

.. code-block:: console

    $ python setup.py install



Usage Example
-------------

.. code-block:: pycon

    >>> import intertext
    >>> 


**Note:** In almost all cases, ``intertext`` expects to be working with ``unicode`` text. Better don't use ``str``.


Bugs
----

Please report any bugs that you find `here <https://github.com/arnosimons/intertext/issues>`_.
Or, even better, fork the repository on `GitHub <https://github.com/arnosimons/intertext>`_
and create a pull request (PR). I welcome all changes, big or small.


Credits
-------

Written by Arno Simons

Released under GNU General Public License, version 3.0

Copyright (c) 2017 Arno Simons

.. _PyPi: https://pypi.python.org/pypi/intertext
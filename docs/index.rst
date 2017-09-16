.. Fenix documentation master file, created by
   sphinx-quickstart on Mon Sep 18 07:42:49 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Fenix's documentation!
=================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`search`

.. include:: modules.rst



What is Fenix?
==============

Fenix is a tool to produce core-dumps that are compatible with python debugger tools when your code
raises an uncaught exception. Fenix only works when this happens and therefore there is no runtime
overhead associated with the tool. There are many ways available to trigger this behaviour depending
on the granularity that you want, these can be as little invasive as running your code though a runner
(and therefore you don't need to change yor code) or as granular as context managers and decorators (so
you can generate these core dumps for specific pars or your code).

.. image:: images/fenix.gif

How do I install Fenix?
=======================

The easiest way to install Fenix to try it is by executing setup.py:

.. code-block:: bash

   python setup.py install --user


This will install the code in `~/.local/bin` so be sure that this directory is in your `PATH`.

How to use the runner
=====================

The easiest way of using Fenix is running your code though the provided runner. The runner is basically
the same thing as your default python interpreter only with the fenix behaviour activated.
This will **only** activates the `sys.excepthook` and then run you code, so you don't need to be
worried about the possibility of the runner interfering with your code's behaviour.

.. argparse::
   :filename: ../scripts/fenix
   :func: get_parser
   :prog: fenix

How to use the contextmanager
=============================

You can use fenix as a contextmanger in your code like this:

.. code-block:: python

    from fenix import Fenix
    with Fenix("./path_to_fenix_coredump"):
       mysuperdangerousfunction()

How to use the decorator
========================

To use fenix as a decorator just decorate the function that you want to generate core dumps
if something goes wrong:

.. code-block:: python

    from fenix import Fenix
    @Fenix("./path_to_fenix_coredump")
    def mysuperdangerousfunction():
       ...




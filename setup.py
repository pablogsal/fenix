#!/usr/bin/env python

from setuptools import setup

DESCRIPTION = """
Fenix allows post-mortem debugging for Python programs.

It writes the traceback of an exception into a file and can later load
it in a Python debugger.

Works with the built-in pdb and with other popular debuggers
(pudb, ipdb and pdbpp).
"""

# get version without importing
__version__ = '0.1'

setup(
    name='Fenix',
    version=__version__,
    description='Post-mortem debugging for Python programs',
    long_description=DESCRIPTION,
    author='Pablo Galindo Salgado',
    license='BSL',
    author_email='pablogsal@gmail.com',
    url='https://github.com/pablo/fenix',
    package_dir={'fenix': './fenix'},
    packages=['fenix'],
    scripts=['scripts/fenix'],
    classifiers=[
        'Development Status :: 0 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSL License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Debuggers'
    ], requires=['dill']
)

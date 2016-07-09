#!/usr/bin/env python3
import os, setuptools

metadata = {
  "name": "pyscanprev",
  "version": "0.1",
  "author": "Danilo J. S. Bellini",
  "author_email": "danilo.bellini.gmail.com",
  "url": "http://github.com/danilobellini/pyscanprev",
  "py_modules": ["pyscanprev"],
  "install_requires": ["bytecode"],
}

fname_readme = os.path.join(os.path.split(__file__)[0], "README.rst")
with open(fname_readme, "r") as f:
  data = f.read()

metadata["long_description"] = data
metadata["description"] = data.split("\n\n", 2)[1].replace("\n", " ").strip()

metadata["classifiers"] = """
Development Status :: 2 - Pre-Alpha
Intended Audience :: Developers
Intended Audience :: Other Audience
Operating System :: POSIX :: Linux
Operating System :: OS Independent
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Topic :: Adaptive Technologies
Topic :: Software Development
Topic :: Software Development :: Assemblers
Topic :: Software Development :: Code Generators
Topic :: Software Development :: Disassemblers
Topic :: Software Development :: Libraries
Topic :: Software Development :: Libraries :: Python Modules
""".strip().splitlines()

setuptools.setup(**metadata)

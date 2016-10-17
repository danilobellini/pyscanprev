#!/usr/bin/env python3
import os, setuptools, operator, functools, itertools

not_summary_start = functools.partial(operator.ne, ".. summary")
not_summary_end = functools.partial(operator.ne, ".. summary end")

def get_summary(data):
    return " ".join([line.strip()
                     for line in itertools.takewhile(not_summary_end,
                                 itertools.dropwhile(not_summary_start, data))
                     if line.strip()
                    ][1:]) # The [1:] skips the summary start line

def without_summary(data):
    return "\n".join(list(itertools.takewhile(not_summary_start, data)) +
                     list(itertools.dropwhile(not_summary_end, data))[1:])

metadata = {
  "name": "pyscanprev",
  "version": "0.1",
  "author": "Danilo J. S. Bellini",
  "author_email": "danilo.bellini.gmail.com",
  "url": "http://github.com/danilobellini/pyscanprev",
  "license": "MIT",
  "py_modules": ["pyscanprev"],
  "install_requires": ["bytecode"],
}

fname_readme = os.path.join(os.path.split(__file__)[0], "README.rst")
with open(fname_readme, "r") as f:
    readme_data = f.read().splitlines()

metadata["long_description"] = without_summary(readme_data)
metadata["description"] = get_summary(readme_data)

metadata["classifiers"] = """
Development Status :: 2 - Pre-Alpha
Intended Audience :: Developers
Intended Audience :: Other Audience
License :: OSI Approved :: MIT License
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

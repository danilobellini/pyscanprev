#!/usr/bin/env python3
import os, setuptools, operator, functools, itertools, re, ast

url = "https://github.com/danilobellini/pyscanprev"

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

dname = os.path.dirname(__file__)
fname_module = os.path.join(dname, "pyscanprev.py")
fname_readme = os.path.join(dname, "README.rst")

with open(fname_module, "r") as f:
    ast_body = ast.parse(f.read(), filename=fname_module).body
    version_expression = next(ast.Expression(node.value)
                              for node in ast_body
                              if isinstance(node, ast.Assign)
                              and node.targets[0].id == "__version__")
    version = eval(compile(version_expression, fname_module, "eval"))

with open(fname_readme, "r") as f:
    readme_data = re.sub(r"(\.\. _.+:\n\s*)(examples/.*)",
                         r"\1{0}/blob/v{1}/\2".format(url, version),
                         f.read()).splitlines()

metadata = {
  "name": "pyscanprev",
  "version": version,
  "author": "Danilo J. S. Bellini",
  "author_email": "danilo.bellini.gmail.com",
  "url": url,
  "description": get_summary(readme_data),
  "long_description": without_summary(readme_data),
  "license": "MIT",
  "py_modules": ["pyscanprev"],
  "install_requires": ["bytecode"],
}

metadata["classifiers"] = """
Development Status :: 3 - Alpha
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

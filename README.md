<div align="center" size="15px">

# flake8-get-chaining

A [flake8](https://github.com/PyCQA/flake8) plugin finding likely bugs when chaining dict.get calls

[![CI](https://github.com/Sacrimento/flake8-get-chaining/actions/workflows/ci.yml/badge.svg)](https://github.com/Sacrimento/flake8-get-chaining/actions/workflows/ci.yml)
[![code style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

</div>

`flake8-get-chaining` plugin checks for chained `dict.get` calls and makes sure valid defaults are provided.

## Installation
------------

Install from `pip` with:

```sh
$ pip install flake8-get-chaining
```

It will then automatically be run as part of `flake8`; you can check it has been picked up with:

```sh
$ flake8 --version
5.0.4 (flake8-get-chaining: 0.1.0, mccabe: 0.7.0, pycodestyle: 2.9.1, pyflakes: 2.5.0) CPython 3.10.9 on Linux
```

## List of warnings
------------

**DGC1001**: Missing default argument when chaining dict.get  
This warning is emitted when `dict.get` calls are chained, and no default was provided.  
  
_Example_: `my_dict.get("foo").get("bar")`  
  
  
**DGC1002**: Invalid default argument when chaining dict.get  
This warning is emitted when `dict.get` calls are chained, and the default value is  
invalid (i.e not a dict nor an identifier)  
  
_Example_: `my_dict.get("foo", "bar").get("baz")`  
  
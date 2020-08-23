# Tinkerer

[![pypi](https://img.shields.io/pypi/v/mc-tinkerer)](https://pypi.org/project/mc-tinkerer)
[![python version](https://img.shields.io/pypi/pyversions/mc-tinkerer)](https://pypi.org/project/mc-tinkerer)
[![license](https://img.shields.io/github/license/dmitri-mcguckin/tinkerer)](./LICENSE)
[![unit tests](https://img.shields.io/github/workflow/status/dmitri-mcguckin/tinkerer/Tinkerer%20Unit%20Tests?label=unit%20tests)](https://github.com/dmitri-mcguckin/tinkerer/actions?query=workflow%3A%22Tinkerer+Unit+Tests%22)
[![issues](https://img.shields.io/github/issues/dmitri-mcguckin/tinkerer)](https://github.com/dmitri-mcguckin/tinkerer/issues)

***

An MC Modpack builder, an alternative to both the twitch client pack editor and editing manifest jsons manually.

***

# Run App

**Local Install (current user):**

`$` `python3 -m tinkerer`

**Global Install (all users):**

`$` `tinkerer`

***

# Install via PyPi

`$` `pip3 install mc-tinkerer`

***

# Install Locally

**For Current User:**

`$` `python -m pip install dist/tinkerer*.whl`

**For All Users:**

`$` `sudo python -m pip install dist/tinkerer*.whl`

***

# Development and Contribution

**Install dependencies:**

`$` `pip3 install -r requirements.txt`


**Build the Tinkerer module:**

`$` `python3 setup.py sdist bdist_wheel`


**Deploy Manually to PyPi:**

`$` `python -m twine upload dist/*`

*(This assumes that you have the correct PyPi credentials and tokens set up according to the instructions [outlined here](https://packaging.python.org/guides/distributing-packages-using-setuptools/#id79))*


**Clean Up Build Artifacts:**

`$` `rm -rf build dist *.egg-info`


**Run Unit Tests:**

`$` `pytest tests/*`

***

# TODO

- [ ] Add curseforge deployment support
- [x] Add curses UI
- [x] Recreate into a proper python module

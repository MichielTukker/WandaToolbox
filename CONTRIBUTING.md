# Contributing

We'd love to accept your patches and contributions to this project. There are just a few small 
guidelines you need to follow.

## Guidelines
1. Write your patch
1. Add a test case to your patch
1. Make sure that all tests run properly
1. Send your patch as a PR

## Installation

You can install the WandaToolbox package as follows:
```
pip install wandatoolbox 
```

## Development installation and testing

For development you can use the 'editable' installation:
```
pip install -e . 
pytest
```

## Building the package

Building the backage is done as follows:
```
pip install setuptools wheel
python setup.py sdist bdist_wheel
```

## Creating a release

We use bump2version to update the version numbers. Bump2version will also create a tag and commit the 
changes.  This can then be pushed using
```
git push origin <branch> --tags
```
The Github Actions have been configured to run the tests and flake8 linting and publish to test.Pypi 
on every push. If a commit is also tagged it will also publish to Pypi. 

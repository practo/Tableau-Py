# Contributing

## Getting Started

Fork the repository to your own account.

Clone the repository to a suitable location on your local machine.

```bash
git clone https://github.com/practo/Tableau-Py
```

**Note:** This will clone the entire contents of the repository at the HEAD revision.

To update the project from within the project's folder you can run the following command:

```bash
git pull --rebase
```

Install pre-commit cli:

```bash
pip install pre-commit
```

### Building

Install [pre-commit](http://pre-commit.com) hooks

```bash
pre-commit install
```

This will create automatically create a virtual env `py_env-default`

Install the project's dependencies.

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
python setup.py install_dependencies
```

Last command will install external dependency ([TableauSDK](https://onlinehelp.tableau.com/current/api/sdk/en-us/SDK/tableau_sdk_installing.htm)) for this project looking for supported platform and architecture.

### Testing

```bash
tox
```

For running test for all environments or

```bash
tox -e <env_name>
```

to run for a specific environment.

## Feature Requests

We are always looking for suggestions to improve this project. If you have a suggestion for improving an existing feature, or would like to suggest a completely new feature, please file an issue with my [GitHub repository](https://github.com/anuragagarwal561994/auto_extract/issues).

## Bug Reports

Our project isn't always perfect, but we strive to always improve on that work. You may file bug reports on the [GitHub repository](https://github.com/practo/Tableau-Py/issues) site.

## Pull Requests

Along with my desire to hear your feedback and suggestions, we are also interested in accepting direct assistance in the form of new code or documentation.

Please feel free to file merge requests against this [GitHub repository](https://github.com/practo/Tableau-Py/pulls).

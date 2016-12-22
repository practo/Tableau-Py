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

### Building

Install the project's dependencies.

```bash
$ pip install -r requirements.txt       #library requirements
$ pip install -r requirements-dev.txt   # dev requirements
$ python setup.py install_dependencies  # external dependencies (tableau sdk)
$ pre-commit install                    # install a pre-commit hook in .git repository
$ virtualenv venv                       # create a virtual environment
$ . venv/bin/activate                   # activate created virtual environment
```

**Notes**:
* For more information about pre-commit by yelp click [here](http://pre-commit.com).
* For more information about TableauSDK click [here](https://onlinehelp.tableau.com/current/api/sdk/en-us/SDK/tableau_sdk_installing.htm). `install_dependencies` command will automatically figure out the required sdk for current architecture and system.
* Project is tested with TableauSDK version `10100.16.1103.2343` and supports Tableau version 10.0 for now, more support will be added in future.
* If you find unexpected behaviour while running anything, just check that the venv virtual environment is activated. When a new terminal is opened the virtual environment is not activated by default on it.

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

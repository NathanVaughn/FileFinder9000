# FileFinder9000

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![GitHub license](https://img.shields.io/github/license/NathanVaughn/FileFinder9000)](https://github.com/NathanVaughn/FileFinder9000/blob/main/LICENSE)

---

This is a simple tool to take a `.csv` export from
[Everything](https://www.voidtools.com/) and bulk search various terms. This tool
will return a `.json` or `.csv` file of the results. By using `.csv` files
from Everything, the Everything SDK does not need to be installed.

This tool is useful if you have a list of old documents you are trying
to locate on a file server or something.

![Application window](images/Screenshot.png)

## Development

Use the provided [devcontainer](https://containers.dev/)
or run the following for local development:

```bash
# Install uv
# https://docs.astral.sh/uv/getting-started/installation/
uv tool install vscode-task-runner
vtr install
```

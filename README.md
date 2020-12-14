# M42PL - Commands

Core [M42PL](https://github.com/jpclipffel/m42pl-core) commands.

## What are M42PL commands ?

M42PL commands implements all language-level functionnalities.

## Installation

```shell
git clone https://github.com/jpclipffel/m42pl-commands
pip install -e m42pl-commands
```

## Commands list

| Aliases                           | Module            | Type         | Status |
|-----------------------------------|-------------------|--------------|--------|
| `script`                          | `script.py`       | -            | Alpha  |
| `output`, `print`                 | `output.py`       | `Streaming`  | Alpha  |
| `mpl_commands`, `mpl_command`     | `mpl_commands.py` | `Generating` | Alpha  |
| `ignore`, `comment`               | `ignore.py`       | `Meta`       | Alpha  |
| `echo`                            | `echo.py`         | `Generating` | Alpha  |
| `expand`, `mvexpand`              | `expand.py`       | `Streaming`  | Alpha  |
| `fields`                          | `fields.py`       | `Streaming`  | Alpha  |
| `foreach`                         | `foreach.py`      | `Streaming`  | Alpha  |
| `rename`                          | `rename.py`       | `Streaming`  | Alpha  |
| `eval`                            | `eval.py`         | `Streaming`  | Alpha  |
| `stats`, `aggre`, `aggregate`     | `stats`           | `Streaming`  | Alpha  |
| `xpath`                           | `xpath.py`        | `Streaming`  | Alpha  |
| `make`, `makeevent`, `makeevents` | `make.py`         | `Generating` | Alpha  |
| `read`                            | `read.py`         | `Generating` | Alpha  |
| `process`                         | `process.py`      | `Generating` | Alpha  |
| `url`, `curl`, `wget`             | `url`             | `Generating` | Alpha  |
| `http_server`                     | `http_server`     | `Generating` | Alpha  |

## Tests

The testing mechanism is still being build. Ultimately, each command
must have its own test script with itw own set of `TestScripts`.

| Test type      | Snippet                              | Description                  |
|----------------|--------------------------------------|------------------------------|
| Single command | `python -m unittest tests.<command>` | Test the command `<command>` |
| Single command | `python tests/<command>.py`          | Test the command `<command>` |

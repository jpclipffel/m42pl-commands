# M42PL - Core commands

Most of [M42PL][m42pl-core] functionnalities are implemented by **commands**.
Core commands are required by M42PL and are comparable to a programming
language standard library.

The unstable core commands (in development or being tested) are in a 
[separate repository][m42pl-commands-lab].

## Installation

```shell
git clone https://github.com/jpclipffel/m42pl-commands
pip install -e m42pl-commands
```

## Commands list

| Aliases                              | Module                | Type                 | Short description                               |
|--------------------------------------|-----------------------|----------------------|-------------------------------------------------|
| `script`                             | `script.py`           | -                    | Parse a M42PL script and produces the pipelines |
| `until`                              | `until.py`            | `Generating`         | Runs a sub-pipeline until a field becomes true  |
| `make`, `makeevent`, `makeevents`    | `make.py`             | `Generating`         | Generate events                                 |
| `read`                               | `read.py`             | `Generating`         | Read from file                                  |
| `process`                            | `process.py`          | `Generating`         | Run an external process                         |
| `url`, `curl`, `wget`                | `url/asynchronous.py` | `Generating`         | Performs an HTTP request                        |
| `http_server`                        | `http_server`         | `Generating`         | Start a simple HTTP server                      |
| `mpl_commands`, `commands`           | `mpl_commands.py`     | `Generating`         | List the available commands, their syntax, etc. |
| `echo`                               | `echo.py`             | `Generating`         | Returns an empty event or the latest event      |
| `foreach`                            | `foreach.py`          | `Streaming`          | Runs a sub-pipeline for each event              |
| `where`                              | `where.py`            | `Streaming`          | Filter events using a Python expression         |
| `output`, `print`                    | `output.py`           | `Streaming`          | Print events on the screen                      |
| `expand`, `mvexpand`                 | `expand.py`           | `Streaming`          | Returns one event per field value               |
| `fields`                             | `fields.py`           | `Streaming`          | Filter fields                                   |
| `rename`                             | `rename.py`           | `Streaming`          | Rename fields                                   |
| `eval`                               | `eval.py`             | `Streaming`          | Evaluate new fields using a Python expression   |
| `stats`, `aggre`, `aggregate`        | `stats`               | `Streaming`          | Performs statistical and aggregating operations |
| `regex`, `rex`, `rx`                 | `regex.py`            | `Streaming`          | Extracts fields using regular expressions       |
| `xpath`                              | `xpath.py`            | `Streaming`          | Extracts fields using XPath expressions         |
| `sleep`                              | `sleep.py`            | `Streaming`          | Pause the pipeline execution during N seconds   |
| `ignore`, `comment`                  | `ignore.py`           | `Meta`               | Comment the command                             |

And more to come / to add to this list.

## Tests

The testing mechanism is still being build. Ultimately, each command
must have its own test script with its own set of `TestScripts`.

| Test type      | Snippet                              | Description                  |
|----------------|--------------------------------------|------------------------------|
| All commands   | `python -m unittest tests/test_*.py` | Test all commands at once    |
| Single command | `python -m unittest tests.<command>` | Test the command `<command>` |
| Single command | `python tests/<command>.py`          | Test the command `<command>` |

## Documentation

Commands are documented [on the language website](m42pl-site).

### Documentation generation

The script `docs/generate.mpl` renders the documentation from the commands
templates.

---

[m42pl-core]: https://github.com/jpclipffel/m42pl-core
[m42pl-commands-lab]: https://github.com/jpclipffel/m42pl-commands-lab

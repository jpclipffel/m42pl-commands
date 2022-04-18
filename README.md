<!-- vim: set ft=Markdown ts=2 -->

# M42PL - Core commands

This repository contains the core commands of [M42PL][m42pl-core-git], a
_Data Manipulation Language_.

* [Commands documentation][m42pl-commands-doc]
* [M42PL documentation][m42pl-core-doc]

## Installation

```shell
git clone https://github.com/jpclipffel/m42pl-commands
pip install -e m42pl-commands
```

## Documentation

The commands are [documented here][m42pl-commands-docs].

The M42PL script `docs/generate.mpl` renders the documentation from the
commands' Jinja templates:

```
m42pl run generate.mpl -e '{"render_mode":"markdown", "render_path":"docs/commands"}'
```

## Tests

| Test type      | Snippet                              | Description                  |
|----------------|--------------------------------------|------------------------------|
| Automated      | `run_tests.sh`                       | Automated tests              |
| All commands   | `python -m unittest tests/test_*.py` | Test all commands at once    |
| Single command | `python -m unittest tests.<command>` | Test the command `<command>` |
| Single command | `python tests/<command>.py`          | Test the command `<command>` |

---

[m42pl-core-git]: https://github.com/jpclipffel/m42pl-core
[m42pl-core-docs]: https://jpclipffel.github.io/m42pl-core
[m42pl-commands-docs]: https://jpclipffel.github.io/m42pl-commands

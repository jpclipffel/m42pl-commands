# M42PL - Core commands

Most of [M42PL][m42pl-git-core] functionnalities are implemented by commands.
Core commands are required by M42PL and are comparable to a programming
language standard library.

The unstable core commands (in development or being tested) are in a 
[separate repository][m42pl-git-commands-lab].

## Installation

```shell
git clone https://github.com/jpclipffel/m42pl-commands
pip install m42pl-commands
```

## Commands list

The complete commands documentation [is hosted here][m42pl-docs-commands].

| Aliases                            | Module                 | Type         | Short description                                     |
|------------------------------------|------------------------|--------------|-------------------------------------------------------|
| `stats`, `aggre`, `aggregate`      | `stats`                | `Streaming`  | Performs statistical operations and aggregates events |
| `url`, `curl`, `wget`              | `url/asynchronous.py`  | `Generating` | Performs HTTP request                                 |
| `zmq_pub`                          | `zeromq/publish.py`    | `Streaming`  | Publishes events to ZMQ                               |
| `zmq_sub`                          | `zeromq/subscribe.py`  | `Generating` | Receives events from ZMQ                              |
| `zmq_push`                         | `zeromq/push.py`       | `Streaming`  | Pushes events to ZMQ                                  |
| `zmq_pull`                         | `zeromq/pull.py`       | `Generating` | Pulls events from ZMQ                                 |
| `assert`                           | `assert.py`            | `Meta`       | Asserts an expression                                 |
| `buffer`                           | `buffer.py`            | `Buffering`  | Buffers events                                        |
| `cut`                              | `cut.py`               | `Streaming`  | Splits a field using a regular expression             |
| `echo`                             | `echo.py`              | `Generating` | Yields the latest event                               |
| `encode`                           | `encoding.py`          | `Streaming`  | Encodes event or field(s) in a foreign format         |
| `decode`                           | `encoding.py`          | `Streaming`  | Decodes field(s) from a foreign format                |
| `eval`                             | `eval.py`              | `Streaming`  | Sets fields using Python expression                   |
| `expand`                           | `expand.py`            | `Streaming`  | Duplicates event for each value of a given field      |
| `extract_kv`, `extract_kvs`        | `extract_keyvalues.py` | `Streaming`  | Extracts keys/values pairs from field                 |
| `extract_map`, `extract_maps`      | `extract_maps.py`      | `Streaming`  | Generate new keys/values paeirs from field            |
| `fields`                           | `fields.py`            | `Streaming`  | Filter (keep or remove) fields                        |
| `fieldstats`, `fstats`             | `fieldstats.py`        | `Buffering`  | Yields fields informations                            |
| `foreach`                          | `foreach.py`           | `Streaming`  | Runs a sub-pipeline for each event                    |
| `head`                             | `head.py`              | `Streaming`  | Keeps only the first event of the stream              |
| `http_server`                      | `http_server.py`       | `Generating` | Runs an configurable HTTP server                      |
| `ignore`, `comment`                | `ignore.py`            | `Meta`       | Comment the command                                   |
| `jinja`, `template_jinja`          | `jinja.py`             | `Streaming`  | Renders a Jinja template                              |
| `jsonpath`, `jspath`               | `jsonpath.py`          | `Streaming`  | Evaluates an JSONPath expression                      |
| `kvwrite`, `kv_write`              | `kv.py`                | `Meta`       | Sets a KVStore key                                    |
| `kvread`, `kv_read`                | `kv.py`                | `Meta`       | Reads a KVStore key                                   |
| `macro`                            | `macro.py`             |              | Records, runs or list macros                          |
| `make`                             | `make.py`              | `Generating` | Generate new events                                   |
| `mpl_commands`, `commands`         | `mpl_commands.py`      | `Generating` | List the available commands, their syntax, etc.       |
| `output`, `print`                  | `output.py`            | `Streaming`  | Print events on the standard output                   |
| `parse_json`, `json_parse`         | `parse_json.py`        | `Streaming`  | Parses a JSON string as an event                      |
| `process`                          | `process.py`           | `Generating` | Runs an external process                              |
| `readfile`                         | `readfile.py`          | `Generating` | Reads a file at once                                  |
| `readlines`                        | `readlines.py`         | `Generating` | Reads a file line by line                             |
| `regex`, `rex`, `rx`               | `regex.py`             | `Streaming`  | Extracts fields using regular expressions             |
| `rename`                           | `rename.py`            | `Streaming`  | Rename fields                                         |
| `sleep`                            | `sleep.py`             | `Meta`       | Pause the pipeline execution during N seconds         |
| `split`, `mvsplit`                 | `split.py`             | `Streaming`  | Splits a field into new events                        |
| `tailf`                            | `tailf.py`             | `Streaming`  | Ignore the firsts events                              |
| `until`                            | `until.py`             | `Generating` | Runs a sub-pipeline until a field becomes true        |
| `where`                            | `where.py`             | `Streaming`  | Filter events using a Python expression               |
| `wrap`                             | `wrap.py`              | `Streaming`  | Wraps event into a higher-level event                 |
| `write`, `writefile`               | `writefile.py`         | `Streaming`  | Write event to a file (replace file content)          |
| `write-append`, `writefile-append` | `writefile.py`         | `Streaming`  | Write event to a file (append file content)           |
| `xpath`                            | `xpath.py`             | `Streaming`  | Extracts fields using XPath expressions               |

## Documentation

The commands are documented on the [M42PL's commands page][m42pl-docs-commands].

The script `docs/generate.mpl` renders the documentation from the commands'
Jinja emplates. Example:

```
m42pl run generate.mpl -e \
'{\
    "render_mode": "jekyll",\
    "render_path": "../../../mine42-io.github.io/jekyll/m42pl/m42pl-commands"\
}'
```

## Tests

The testing mechanism is still being build. Ultimately, each command
should have its own test script with its own set of `TestScripts`.

| Test type      | Snippet                              | Description                  |
|----------------|--------------------------------------|------------------------------|
| All commands   | `python -m unittest tests/test_*.py` | Test all commands at once    |
| Single command | `python -m unittest tests.<command>` | Test the command `<command>` |
| Single command | `python tests/<command>.py`          | Test the command `<command>` |

---

[m42pl-docs]: https://docs.mine42.io/m42pl
[m42pl-docs-commands]: https://docs.mine42.io/m42pl/commands
[m42pl-git-core]: https://github.com/jpclipffel/m42pl-core
[m42pl-git-commands-lab]: https://github.com/jpclipffel/m42pl-commands-lab

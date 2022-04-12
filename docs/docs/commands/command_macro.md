# macro

Record a macro, run a macro or return macros list
## Aliases

* `macro`


## Synopsis

```shell
| macro [<name> [pipeline]]
```


The `macro` command will cast itself into one of three other comands when
ran, depending on its arguments:

| Command        | Effect                | Condition                                                   |
|----------------|-----------------------|-------------------------------------------------------------|
| `macros`       | List available macros | No argument                                                 |
| `_recordmacro` | Record a macro        | A pipeline is given in parameters                           |
| `_runmacro`    | Run a macro           | A macro name and optional arguments are given in parameters |

### List the macros

The commands `macro` (without argument) and `macros` behaves identically:

```
| macro
```

```
| macros
```

### Record a macro

```
| macro <name> pipeline
```

> Warning: `macro` currently does not suoport sub-pipelines (one can't record
  a macro which itself uses a sub-pipeline).

#### Examples

`make_10` will generate 10 events when invoked:

```
| macro make_10 [ | make count=10 showinfo=yes ]
```

`make_some` will generate the number of events if the field named `count`.
If `count` is not found in the field, it will generate 1 event:

```
| macro make_some [ | make count=`field(count, 1)` showinfo=yes ]
```

### Run a macro

```
| macro <name> [<arg>=<value>, ...]
```

Examples:

```
| macro make_10
```

```
| macro make_some count=5
```


## Schema

```json
{
  "properties": {}
}
```

## Description

## Examples

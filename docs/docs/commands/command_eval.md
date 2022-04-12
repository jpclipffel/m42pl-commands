# eval

Evaluate a Python expression and assign result to a field
## Aliases

* `eval`
* `evaluate`

## Synopsis

```shell
| eval <field_name> = <expression> [, ...]
```

## Schema

```json
{
  "additionalProperties": {
    "description": "Evaluated fields"
  }
}
```


## Description

`eval` evaluates an expression and returns its results.

The expression is evaluated by the underlying Python interpreter. Unlike
standard evaluation, `eval` uses a set of custom functions and a custom
variables resolution mechanism.

### Evaluation functions

#### Misc.

| Function name   | Aliases | Syntax                       | Description |
|-----------------|---------|------------------------------|-------------|
| `field`         |         | `field(<name> [,<default>])` | Returns the value of `<field>` or `default` (default: `None`) |
| `isnull`        |         | `isnull(<field>)`            | Returns `True` if `<field>` is `None`, `False` otherwise |
| `isnotnull`     |         | `isnotnull(<field>)`         | Returns `True` if `<field>` is not `None`, `True` otherwise |
| `coalesce`      |         | `coalesce(<field> [, ...])`  | Returns the value of the first non-null `<field>` |

#### Time

| Function name | Aliases | Syntax | Description |
|---------------|---------|--------|-------------|
| now |  |  |
| reltime |  |  |
| strftime |  |  |

#### Cast

| Function name | Aliases | Syntax | Description |
|---------------|---------|--------|-------------|
| tostring |  |  |
| toint |  |  |
| tofloat |  |  |

#### String

| Function name | Aliases | Syntax | Description |
|---------------|---------|--------|-------------|
| clean |  |  |

#### List

| Function name | Aliases | Syntax | Description |
|---------------|---------|--------|-------------|
| list |  |  |
| join |  |  |
| slice |  |  |
| index |  |  |
| length |  |  |

#### Map

| Function name | Aliases | Syntax | Description |
|---------------|---------|--------|-------------|
| keys |  |  |

#### Math

| Function name | Aliases | Syntax | Description |
|---------------|---------|--------|-------------|
| round |  |  |
| even |  |  |
| true |  |  |
| false |  |  |

#### Filter

| Function name | Aliases | Syntax | Description |
|---------------|---------|--------|-------------|
| match |  |  |

#### Path

| Function name | Aliases | Syntax | Description |
|---------------|---------|--------|-------------|
| basename |  |  |
| dirname |  |  |
| joinpath |  |  |
| cwd |  |  |



## Examples


```
| make showinfo=yes
| eval some.field = id + 1
```

```
| commands
| eval
    command.name = at(command.aliases, 0),
    command.markdown = joinpath('markdown', at(command.aliases, 0) + '.md')
```


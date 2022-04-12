# until

Run a sub-pipeline until a field become true
## Aliases

* `until`

## Synopsis

```shell
| until <field> <pipeline>
```

## Schema

```json
{
  "properties": {}
}
```


## Description

`until` can be used to construct loops. The command run its given sub-pipeline
until the value of its given field become true.


## Examples


Runs a sub-pipeline ten (10) times:

```
| until `field(foo, 0) == 10` [
    | eval foo = field(foo, 0) + 1 
    | output buffer=1
]
```

Note that the field is encolsed in backquotes (`` `field(foo, 0) == 10` ``):
This is because the example is using an evaluated field. The evaluation command
`field` return the content of the field `foo` or `0` if the field is not found.

Runs a sub-pipeline once and demonstrate the use of non-evaluated fields:

```
| eval foo = False
| foreach [
    | until foo [
        | eval foo = True
    ]
]
```


# foreach

Run a sub-pipeline for each event
## Aliases

* `foreach`

## Synopsis

```shell
| foreach <pipeline>
```

## Schema

```json
{
  "properties": {}
}
```


## Description

`foreach` runs a sub-pipeline for each event.
it is mostly useful to chain generating commands.


## Examples


Query an url for each event:

```
| readline 'urls.txt'
| foreach [
    | curl url=line
]
```


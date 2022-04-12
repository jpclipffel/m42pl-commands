# readlines

Read a file line by line
## Aliases

* `readlines`
* `readline`

## Synopsis

```shell
| readlines [path=]{file path} [field=]{dest field}
```

## Schema

```json
{
  "properties": {
    "{dest field}": {
      "type": "object",
      "properties": {
        "text": {
          "type": "string",
          "description": "Read line"
        },
        "line": {
          "type": "number",
          "description": "Line count"
        }
      }
    }
  }
}
```

## Description

## Examples

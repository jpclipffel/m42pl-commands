# decode

Decodes event or event field
## Aliases

* `decode`

## Synopsis

```shell
| decode {src field} [as {dest field}] with <codec> | {src field} with <codec> [as {dest field}] | [[codec=]<codec>] [[src=]{src field}] [[dest=]{dest field}]
```

## Schema

```json
{
  "properties": {
    "{dest_field}": {
      "description": "Decoded field"
    }
  }
}
```

## Description

## Examples

# zmq_pull

Pull events from ZMQ
## Aliases

* `zmq_pull`

## Synopsis

```shell
| zmq_pull [[url=]<url>] [[codec=]<codec>] [[field=]<field>]
```

## Schema

```json
{
  "properties": {
    "topic": {
      "type": "string",
      "description": "ZMQ topic"
    },
    "chunk": {
      "type": "array",
      "description": "Dispatcher chunk ID and chunks count"
    }
  }
}
```

## Description

## Examples

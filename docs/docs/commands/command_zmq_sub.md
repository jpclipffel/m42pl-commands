# zmq_sub

Subscribe and receive messages from ZMQ
## Aliases

* `zmq_sub`
* `zmq_subscribe`

## Synopsis

```shell
| zmq_sub [[url=]<url>] [[codec=]<codec>] [[field=]<field>] [[topic=]<topic>]
```

## Schema

```json
{
  "properties": {
    "topic": {
      "type": "string",
      "description": "ZMQ topic"
    },
    "frames": {
      "type": "array",
      "description": "Message frames"
    }
  }
}
```

## Description

## Examples

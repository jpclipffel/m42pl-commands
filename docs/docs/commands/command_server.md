# server

Receives data on a given protocol, host IP and port
## Aliases

* `server`
* `serve`
* `listen`

## Synopsis

```shell
| server [[protocol=]<tcp|udp>] [[host=]<ip>] [[port=]<port>]
```

## Schema

```json
{
  "properties": {
    "msg": {
      "type": "object",
      "properties": {
        "data": {
          "description": "received data"
        },
        "host": {
          "description": "client host"
        },
        "port": {
          "description": "client port"
        }
      }
    }
  }
}
```

## Description

## Examples

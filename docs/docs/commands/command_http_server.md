# http_server

Runs an HTTP server
## Aliases

* `http_server`
* `server_http`

## Synopsis

```shell
| http_server [[host=]{host}] [[port]={port}] (<pipeline> | with 'method' on 'path' = <pipeline>, ...)
```

## Schema

```json
{
  "properties": {
    "request": {
      "type": "object",
      "properties": {
        "url": {
          "type": "string",
          "description": "Requested URL"
        },
        "host": {
          "type": "string",
          "description": "Server host"
        },
        "path": {
          "type": "string",
          "description": "Requested path"
        },
        "scheme": {
          "type": "string",
          "description": "Requested URL scheme"
        },
        "jsdata": {
          "type": "object",
          "description": "Request JSON data"
        },
        "query_string": {
          "type": "string",
          "description": "Requested URL query"
        },
        "content_type": {
          "type": "string",
          "description": "Request content type"
        },
        "content_length": {
          "type": "number",
          "description": "Request size"
        }
      }
    }
  },
  "additionalProperties": {
    "description": "Response fields"
  }
}
```


## Description

`http_server` starts an HTTP server and process each requests in the given
pipelines.

The server always returns (answers) the latest event processed, which is by
default the client request.



## Examples


Echo server:

```
| http_server [ | output buffer=1 ]
```

Process GET and POST requests:

```
| http_server with
    'GET' on '/objects/{name}' = [
        | output buffer=1
        | eval response = 'got some ' + at(split(path, '/'), -1)
        | fields response
    ],
    'POST' on '/objects' = [
        | fields jsdata
        | wrap 'stored'
    ]
```

Set host and port:

```
| http_server host='1.2.3.4' port=1234 [ | output buffer=1 ]
```


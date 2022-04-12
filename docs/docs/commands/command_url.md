# url

Performs asynchronous HTTP calls to a given URL
## Aliases

* `url`
* `curl`
* `wget`

## Synopsis

```shell
| url [urls=](url, ...) [[method=]{HTTP method}] [[headers]={headers k/v}][[data=]{data k/v}] [[json=]{json k/v}] [[frequency=]{seconds}][[count=]{integer}]
```

## Schema

```json
{
  "properties": {
    "time": {
      "type": "number"
    },
    "request": {
      "type": "object",
      "description": "HTTP request",
      "properties": {
        "method": {
          "type": "string"
        },
        "url": {
          "type": "string"
        },
        "headers": {
          "type": "object"
        },
        "data": {
          "type": "object"
        }
      }
    },
    "response": {
      "type": "object",
      "description": "HTTP response",
      "properties": {
        "status": {
          "type": "number"
        },
        "reason": {
          "type": "string"
        },
        "mime": {
          "type": "object"
        },
        "headers": {
          "type": "object"
        },
        "content": {}
      }
    }
  }
}
```

## Description

## Examples

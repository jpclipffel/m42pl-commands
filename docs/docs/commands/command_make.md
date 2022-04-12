# make

Generates and returns new events
## Aliases

* `make`
* `makeevent`
* `makeevents`

## Synopsis

```shell
| make [[count=]<number>] [[showinfo=](yes|no)][[chunks=]<number>] [[frequency=]<seconds>]
```

## Schema

```json
{
  "properties": {
    "id": {
      "type": "number",
      "description": "Event count"
    },
    "chunk": {
      "type": "object",
      "properties": {
        "chunk": {
          "type": "number",
          "description": "Current chunk"
        },
        "chunks": {
          "type": "number",
          "description": "Chunks count"
        }
      }
    },
    "count": {
      "type": "object",
      "properties": {
        "begin": {
          "type": "number",
          "description": "Minium event count in chunk"
        },
        "end": {
          "type": "number",
          "description": "Maximum event count in chunk"
        }
      }
    },
    "pipeline": {
      "type": "object",
      "properties": {
        "name": {
          "type": "string",
          "description": "Chunk pipeline name"
        }
      }
    }
  }
}
```


## Description

`make` generates events. It is primarily used in local scripts, REPL mode and
debug operations.


## Examples


Generate a single, empty event:

```
| make
```

Generate 10 events with basic information:

```
| make count=10 showinfo=yes
```

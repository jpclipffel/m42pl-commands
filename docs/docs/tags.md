# Commands type

Each M42PL command have a specific _type_:

* `GeneratingCommand` generates (yields) events
* `StreamingCommand` process events
* `BufferingCommand` process multiple events at once
* `MetaCommand` operate on the pipelines instead of events
* `Command` are low-level commands, not intended for users

[TAGS]

| readfile `joinpath('templates', 'command_.md.j2')` as template
| assert field(render_mode) and field(render_path) and length(template) > 0
| foreach [
    | mpl_commands
    | where not match(command.alias, '^_.*')
    | stats
        values(command.aliases) as command.aliases,
        first(command.type) as command.type,
        first(command.syntax) as command.syntax,
        first(command.schema) as command.schema,
        first(template) as command.template,
        first(render_mode) as render_mode,
        first(render_path) as render_path,
        by command.about
    | buffer 4096
    | eval command.alias = at(command.aliases, 0)
    | encode command.schema with 'json' as command.jsonschema
    | foreach [
        | readfile `joinpath('templates', 'command_' + command.alias + '.md.j2')` as command.template
    ]
    | jinja src=command.template dest=command.render searchpath='templates'
    | write command.render to `joinpath(render_path, 'command_' + command.alias + '.md')`
    | ignore output buffer=1 header=yes
]

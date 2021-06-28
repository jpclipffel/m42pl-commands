| readfile `joinpath('markdown', 'command_.md.j2')` as template
| assert field(render_mode) and field(render_path)
| foreach [
    | mpl_commands
    | stats
        values(command.aliases) as command.aliases,
        first(command.type) as command.type,
        first(command.syntax) as command.syntax,
        first(template) as command.template,
        first(render_mode) as render_mode,
        first(render_path) as render_path
        by command.about
    | eval command.alias = at(command.aliases, 0)
    | foreach [
        | readfile `joinpath('markdown', 'command_' + command.alias + '.md.j2')` as command.template
    ]
    | jinja src=command.template dest=command.render searchpath='markdown'
    | write command.render to `joinpath(render_path, 'command_' + command.alias + '.md')`
    | ignore output buffer=1 header=yes
]

| readfile `joinpath('markdown', 'command_.md.j2')` as template

| ignore assert field(render_mode) and field(render_path)

| foreach [
    | mpl_commands
    | stats
        values(command.aliases) as command.aliases,
        first(command.type) as command.type,
        first(template) as command.template,
        first(render) as render,
        by command.about
    | foreach [
        | readfile `joinpath('markdown', 'command_' + at(command.aliases, 0) + '.md.j2')` as command.template
    ]
    | eval command.alias = at(command.aliases, 0)
    | jinja src=command.template dest=command.render searchpath='markdown'
    | ignore write command.render to `joinpath('command_' + at(command.aliases, 0) + '.md')`
    | output buffer=1 header=yes
]

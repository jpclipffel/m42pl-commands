| readfile path=`joinpath('markdown', 'command_.md.j2')` field='template' mode='file'
| eval mode = field(mode, 'jekyll')
| foreach [
    | mpl_commands
    | stats
        values(command.aliases) as command.aliases,
        first(template) as command.template,
        first(mode) as command.mode
        by command.about
    | foreach [
        | readfile path=`joinpath('markdown', 'command_' + at(command.aliases, 0) + '.md.j2')` field=command.template mode='file'
        | jinja src=command.template dest=command.render searchpath='markdown'
        | output buffer=1 header=yes
    ]
]


| test_void
| test_args 42 21.12 arg 'single quotes string' "double quotes string" {jspath string}
| test_kwargs integer=42 float=21.12 inline=arg string_sq='single quotes string' string_dq="double quotes string" jspath={jspath string}
| test_subc1 [
    | test_subc1_void
    | test_subc1_args 42 21.12 arg 'single quotes string' "double quotes string" {jspath string}
    | test_subc1_kwargs integer=42 float=21.12 inline=arg string_sq='single quotes string' string_dq="double quotes string" jspath={jspath string}
    | test_subc2 [
        | test_subc2_void
        | test_subc2_args 42 21.12 arg 'single quotes string' "double quotes string" {jspath string}
        | test_subc2_kwargs integer=42 float=21.12 inline=arg string_sq='single quotes string' string_dq="double quotes string" jspath={jspath string}
    ]
  ]

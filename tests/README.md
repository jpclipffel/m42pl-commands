# M42PL - Commands - Tests

Tests cases for M42PL core commands.

## How to run the test(s)

To test all commands:

```Shell
./run_tests.sh
# OR
cd tests; python -m unittest *.py
```

To test a single command:

```Shell
cd tests; python -m unittest test[_<command>].py
```

## Tests scripts

We can distinguish two kind of tests scripts:

| Filename pattern | Description                       |
|------------------|-----------------------------------|
| `test.py`        | Run generic tests on all commands |
| `test_*.py`      | Run command-specific test         |

## How the test scripts are designed

The module `m42pl.utils.unittest` from [m42pl-core] provides a generic set of
test utilities to make the creation of test class as simple as possible.

> __Note__  
> The base unit test module `m42pl.utils.unittest` already defines a number of
> of generic tests. When writting a test class, you should only focus on the
> functional part of the command.

Example test class:

```python
import unittest

from m42pl.utils.unittest import StreamingCommand, TestScript
from m42pl.event import Event


class Eval(StreamingCommand):

    # Command name (alias) which is tested
    command_alias = 'eval'

    # List of tests which must succeed
    expected_success = [
        # A `TestScript` is a specifc test instance
        TestScript(
            # Test name
            'simple_int',
            # Test script
            '''| eval simple_int = 42''',
            # Expected result(s)
            [
                Event({'simple_int': 42})
            ]
        )
    ]


if __name__ == '__main__':
    unittest.main()
```

## How to create a test unit

TODO

---

[m42pl-core]: https://github.com/jpclipffel/m42pl-core

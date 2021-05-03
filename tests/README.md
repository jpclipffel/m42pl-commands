# M42PL - Commands - Tests

Tests cases for M42PL core commands.

## How to run the test(s)

* To test all commands: `python -m unittest tests/*.py`
* To test a single command: `python -m unittest tests/test_<command>.py`

## How the test unit are designed

The module `m42pl.utils.unittest` provides a generic set of test utilities
to make the creation of test class as simple as possible.

```python
# Unittest is needed for the __main__ section
import unittest

# M42PL test utilities
from m42pl.utils.unittest import StreamingCommand, TestScript

# M42PL event
from m42pl.event import Event


class Eval(StreamingCommand):
    expected_success = [
        TestScript(
            'simple_int',                   # Test name
            '''| eval simple_int = 42''',   # Test script
            [Event({'simple_int': 42})])    # Expected result
    ]


if __name__ == '__main__':
    unittest.main()
```

## How to create a test unit

TODO

# Deephaven Layout

Plugin prototype for programmatic layouts and callbacks

## Build

To create your build / development environment:

```sh
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip setuptools
pip install build deephaven-plugin
```

To build:

```sh
python -m build --wheel
```

The wheel is stored in `dist/`. 

To test within [deephaven-core](https://github.com/deephaven/deephaven-core), note where this wheel is stored (using `pwd`, for example).
Then, follow the directions in the [deephaven-js-plugins](https://github.com/deephaven/deephaven-js-plugins) repo.


## Usage

You'll need to install the @deephaven/js-plugin-ui JS plugin as well.
TODO: These are very much a rough draft.

### Create nested components:

```python
import deephaven.ui as ui
from deephaven.ui import use_state
# import * from deephaven.ui

# ui._reset_state()

foo_set_value = None
bar_set_value = None

@ui.component
def foo_component(foo='faa'):
    global foo_set_value
    value, set_value = use_state('hello')
    foo_set_value = set_value
    print("foo_component foo=" + foo + ", value=" + str(value))

@ui.component
def bar_component():
    global bar_set_value
    value, set_value = use_state('AAPL')
    bar_set_value = set_value
    return foo_component(foo=value)

bar_component()
```

### Create a TextInput

```python
from deephaven.ui import TextInput
ti = TextInput('hello', on_change=lambda event: print(f"TextInput on_change event: {event}"))
```
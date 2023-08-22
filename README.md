# deephaven.ui Plugin

Plugin prototype for programmatic layouts and callbacks. Currently calling it `deephaven.ui` but that's not set in stone. 

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
Then, follow the directions in the [deephaven-js-plugins](https://github.com/deephaven/deephaven-js-plugins) repo to install the wheel, e.g.:

```sh
pip install /path/to/deephaven-plugin-ui/dist/deephaven_plugin_ui-0.0.1.dev0-py3-none-any.whl --force-reinstall --no-deps
```


## Usage

You'll need to install the @deephaven/js-plugin-ui JS plugin as well: https://github.com/mofojed/deephaven-plugin-ui.
Follow the `README` there for examples.
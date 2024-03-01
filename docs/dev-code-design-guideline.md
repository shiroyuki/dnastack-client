# Developers' Manual: Code Design Guideline

In version 3, the design of the CLI/library is mostly according to [PEP 8](https://peps.python.org/pep-0008/), POJO-like
approach, and the SOLID design principle where applicable. You will see a lot of instances of:

* single responsibility / code isolation
* dependency injection with [Imagination](https://github.com/shiroyuki/Imagination) (wherever possible)
* adapter pattern
* minimal class inheritance
* lazy loading
* minimal test configuration
* progressive enhancements

## The minimum requirements

We are planning to support any versions of Python which are actively supported by the CPython community.

> Currently, we are supported Python 3.7 and newer.

## Lazy loading

In order to minimize the interruptions or the memory footprint, all most everything in the library part is designed to
initiate activities only when it needs. Here are some example:

* All service clients only initiates the authentication process when it needs as described
  in [this diagram](https://docs.google.com/drawings/d/1-yHTY3zul1kcg3T7_ryX65icoSzYVEcMIJHSPa2ukqo/edit).
* The data connect client will only return the iterator to the query result. With no iteration happening, no HTTP
  requests are made here. However, if the iterator runs out of rows in the buffer and can fetch for more, it will make
  the follow-up requests.

## Minimal test configuration

Following the same approach as the other tests, the test will only require the minimal set of configuration, e.g.,
client ID, client secret, etc., in order to run the test suite.

It should not require specific configuration for resource ID, e.g., table name, collection ID, DRS ID, which makes the
test very sensitive to external changes that we may or may nor have control.

## Progressive enhancements

### 1. Disable features if requirements aren't met

By default, the CLI/library is designed to work with the minimal set of dependencies. Some features require additional
packages, e.g., `DrsClient` requires `pandas` to download files.

This would be the pattern we have used so far.

```python
...

try:
    import pandas

    pandas_installed = True
except ImportError:
    pandas_installed = False

...


def foo():
    if pandas_installed:
        ...  # do something with pandas
    else:
        ...  # do something without pandas or raise an exception
```


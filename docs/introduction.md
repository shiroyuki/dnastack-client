# DNAstack Client Library v3

## Dependencies

* Required:
  * **Python 3.7** or newer
* Optional:
  * **Pandas 1.4** or newer for DRS functionalities
  * **pip 21.3** or newer for a 64-bit ARM-based system, e.g., ARM-based MacOS machines

## Installation

You can check out [the public version of the documentation](public/library.md#installation).

## For developers and testers only

### Build the package locally and install the built package

Before getting started, you will need:
* the source code
* `git`
  * Most developers' machine should have this already.
* Python packages: `build` and `setuptools`
  * The build script will attempt to automatically install the package.

Once you have everything, from the root you may just run:

```shell
./scripts/build-package.py
```

The package will be in the `dist` folder.

To install the built package, run:

```shell
pip3 install dist/dnastack_client_library-3.0.<patch_release_number>-py3-none-any.whl
```

### Install the package from the source code without building a package

Before getting started, you will need:
* the source code
* Python package: `setuptools`
  * **NOTE:** This approach will not install this package automatically.

Once you have everything

```shell
pip3 install -IU .
```

### Install the pre-release version via PyPI

As `pip3` (or `pip` on a Python-3-only system) does not install the pre-release package by default, we need to install
the package by specifying the version. For example,

```shell
pip3 download dnastack-client-library==<pre_release_version>
```

For the list of available versions, please check out [the release history on PyPI](https://pypi.org/project/dnastack-client-library/#history).

## Troubleshooting

### There are dependency conflicts.

While the library imposes a small set of dependencies, if it has conflicts with your current environment (and you only
need the CLI part of it), you may install the package with [pipx](https://pypa.github.io/pipx/).

Please be aware that this approach will only install the package as a command line tool in isolation. You will not be
able to use the installed package in your Python code or Jupyter notebook.

1. Ensure that you have [pipx](https://pypa.github.io/pipx/).
2. Run `pipx install dnastack-client-library`.

## Next step
* [CLI Tool](cli.md)
* Library
  * [Getting started with library](introduction-library.md)
  * [Full API Reference](full-api-reference.md)
* [Code Design Guideline](dev-code-design-guideline.md)

# Developers' Guide: Windows

As we cannot automate the tests on Windows containers, **we have to test the package manually**.

## Setup

You can use any Windows machines but it is recommended to test with a virtual machine to ensure the repeatability.

### Recommended testing environment

* OS: Windows 10 or 11
* Storage: SSD 128/256 GB
* RAM: 8GB

## Compatibility

### Anaconda 3's Python
* The `dnastack` command is available ONLY on Anaconda Powershell Prompt.
* Does not work the new Windows Terminal app.
* _This is the easiest setup as it works pretty much right after the installation._

### Python from Windows App Store
* The `dnastack` command is NOT available on any terminal apps.
* But the user can access the CLI tool as `python -m dnastack`.
* There is a warning about Python's `Scripts` folder is not the `Path` environment variable.
  * As of 2022-06-14, even after modifying `Path`, it is not possible to get `dnastack` to work.

### Python from Python.org
* As the `python` command is not available in this method, **the command line tool and library are not installable.**

## Installation

### Install the package alongside Anaconda 3 on Windows 10/11 with Powershell

To install with **Powershell**,

1. Open "Anaconda Powershell Prompt". You can do it from the start menu or **Anaconda Navigator**<sup>5</sup>.
2. Then, when the Powershell is ready, run [the `pip` command previously mentioned above](#normal-installation).

This package will come with the command line tool which is available as:
* `dnastack`
* `python -m dnastack`

### Install the package alongside Windows App Store-distributed Python on Windows 10/11

With your terminal of choices, run [the `pip` command previously mentioned aboce](#normal-installation).

This package will come with the command line tool which is available as:
* `dnastack` (see the troubleshooting section below)
* `python -m dnastack`

> **Troubleshooting:**
>
> *This troubleshooting is still work in progress and it doesn't really work.*
>
> After successful installation, if you see a warning message like this:
>
> ```
> WARNING: The script dnastack.exe is installed in 'C:\Users\dev\AppData\Local\Packages\PythonSoftwareFoundation.Python.3.10_qbz5n2kfra8p0\LocalCache\local-packages\Python310\Scripts' which is not on PATH.
> ```
>
> this means that the `Scripts` folder is on `Path`.
>
> To solve this issue, please try the following steps.
> 1. You need to go to **System Properties** → **Advanced**.
> 2. Click on **Environment Variables**.
> 3. Edit the `Path` variable by adding the directory path shown in the error message.

### Install the package alongside Python.org-distributed Python on Windows 10/11

As the `python` command is not available in this method, **the command line tool and library are not installable.**

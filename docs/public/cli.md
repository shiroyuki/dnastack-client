---
title: "Command Line Interface"
weight: 1
draft: false
lastmod: 2021-2-17
type: docs
layout: single-col
---

#### Installation

This guide will help you install **dnastack-client-library 3.0**.
If you need to install a specific version,  please check out the list
of available versions on
[the release history page](https://pypi.org/project/dnastack-client-library/#history).

{{<code/float-window>}}
{{< tabs tabTotal="2" tabID="1" tabName1="Normal Installation" tabName2="Windows 10/11">}}
{{% tab tabNum="1" %}}

##### Normal installation

First, you need to have
* **Python 3.7** or higher,
* and optionally **pip 21.3** or newer are required for ARM-based systems, e.g., ARM-based MacOS machines.

You just need to run the `pip` command:

{{%code/code-block%}}
```shell
pip3 install -U dnastack-client-library
```
{{%/code/code-block%}}

> **Tips:**
>
> If `pip3` is not available on your system, please try `pip`, `python -m pip`, or `python3 -m pip`.

This package will come with the command line tool which is available as:
* `dnastack`
* `python3 -m dnastack` or `python -m dnastack` (depending on your Python installation)

{{% /tab %}}
{{% tab tabNum="2" %}}

##### Install the package alongside Anaconda 3 on Windows 10/11 with Powershell

Assume that you have Anaconda 3 installed.

To install with **Powershell**,

1. Open "Anaconda Powershell Prompt". You can do it from the start menu or **Anaconda Navigator**<sup>1</sup>.
2. Then, when the Powershell is ready, run [the `pip` command previously mentioned above](#normal-installation).

This package will come with the command line tool which is available as:
* `dnastack`
* `python -m dnastack`

{{% /tab %}}
{{< /tabs >}}
{{</code/float-window>}}

---

#### Use the command line tool

##### Set up with a service registry

You can easily set up your environment by using the `dnastack use` command. For example, we set up the CLI to work with
the service endpoints available at `viral.ai`.

{{%code/code-block%}}
```shell
dnastack use viral.ai
```
{{%/code/code-block%}}

##### List all collections

You can list all collections with:

{{%code/code-block%}}
```shell
dnastack collections list
```
{{%/code/code-block%}}

##### List items in a particular collection

You can list all items in a particular collection with `dnastack collections list-items -c SLUG_NAME` where `SLUG_NAME`
is the slug name of the collection. Here is an example.

{{%code/code-block%}}
```shell
dnastack collections list-items -c ncbi-sra
```
{{%/code/code-block%}}

where the item can be a blob<sup>2</sup> or table<sup>3</sup>.

##### Run a query

You can run query like this:

{{%code/code-block%}}
```shell
dnastack collections query -c ncbi-sra "SELECT * FROM collections.ncbi_sra.public_variants LIMIT 10"
```
{{%/code/code-block%}}

Alternatively, you can do this.

{{%code/code-block%}}
```shell
dnastack data-connect query --endpoint-id data-connect-ncbi-sra "SELECT * FROM collections.ncbi_sra.public_variants LIMIT 10"
```
{{%/code/code-block%}}

Although the former method is recommended.

##### Download blobs

You can run `dnastack files download` to download blobs with its ID or metadata URL, for example:

{{%code/code-block%}}
```shell
dnastack files download drs://viral.ai/faux-blob-id-001 faux-blob-id-002
```
{{%/code/code-block%}}

#### Footnotes

1. The normal Powershell or Window Terminal does not work in this case.
2. For a "blob" item, the metadata URL is what you need to download a file with the "files" command.
3. For a "table" item, the name of the item is the name of the table that you can use in the query.
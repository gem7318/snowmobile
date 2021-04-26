## Setup

<hr class="sn-grey">
<br>

### 1. Install
`pip install snowmobile`

<hr class="sn-spacer">

### 2. Save *snowmobile.toml*
Download {download}`snowmobile-template.toml <../snowmobile/core/pkg_data/snowmobile-template.toml>` 
and save it in anywhere on your file system as **`snowmobile.toml`**.
+++

<hr class="sn-spacer">

### 3. Store Credentials
The first few lines of [](./usage/snowmobile_toml.md) are outlined below; **for 
minimum configuration,** populate lines 6-12 with a valid set of {xref}`snowflake` 
credentials.

`````{literalinclude} ../snowmobile/core/pkg_data/snowmobile-template.toml
:class: toggle-shown, sn-indent-h
:language: toml
:lineno-start: 2
:lines: 2-12
`````

```{admonition} Tip: see [here](https://toml.io/en/) if unfamiliar with *.toml* syntax
:class: tip, sn-inherit-overflow, sn-clear-title, sn-indent-h-cell-m, sn-dedent-v
&nbsp;
```

````{admonition} More Info
:class: note, toggle, sn-indent-h-cell-m, sn-dedent-v-t-container

<hr class="sn-spacer-thick">

```{div} sn-left-pad 
On line **3**, `default-creds` enables specifying the default *alias*
of the connection arguments to authenticate with by default if not specified 
in the *creds* parameter of {meth}`snowmobile.connect()`.
 
If left empty and also not provided as a parameter, arguments under the alias
`creds1` will be authenticated with as it's the first set of credentials stored 
at the level of **`connection.credentials.*`**
```

<hr class="sn-grey-dotted">
<hr class="sn-spacer">

```{div} sn-left-pad, sn-increase-margin-v-container
See
[**Connector: Parameter Resolution**](./usage/snowmobile.md#parameter-resolution)
for details on how <a class="fixture-sn" href="../index.html#fixture-sn"></a>
determines what gets passed to {xref}`snowflake.connector.connect()`
```

````

<hr class="sn-spacer">

### 4. Connect to {xref}`snowflake`
Successful setup and connection can be verified with:
```python
import snowmobile

sn = snowmobile.connect()
"""
Looking for snowmobile.toml in local file system..
(1 of 1) Located 'snowmobile.toml' at ../Snowmobile/snowmobile.toml
..connected: snowmobile.Snowmobile(creds='creds1')
"""
```

```{div} sn-link-container 
{link-badge}`./usage/snowmobile.html#executing-raw-sql,cls=badge-primary text-white sn-usage,Related: Executing Raw SQL,tooltip=Usage Documentation on Connecting to Snowflake`
{link-badge}`./usage/snowmobile.html#connecting-to-snowflake,cls=badge-warning text-dark,Issues? See Docs,tooltip=Usage Documentation on Connecting to Snowflake`
```

<br>

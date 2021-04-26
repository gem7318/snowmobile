(usage/snowmobile)=
# Snowmobile
<hr class="sn-grey">
<a 
    class="sphinx-bs badge badge-primary text-white reference external sn-api sn-link-container2" 
    href="../autoapi/snowmobile/core/connection/index.html" 
    title="API Documentation">
        <span>snowmobile.core.connection</span>
</a>

An instance of {class}`~snowmobile.Snowmobile`, 
<a class="fixture-sn" href="../index.html#fixture-sn"></a>, represents a distinct 
[session](https://docs.snowflake.com/en/sql-reference/functions/current_session.html)
along with the contents of the [snowmobile.toml](./snowmobile_toml.md#snowmobiletoml) 
with which it was instantiated.

```{div} sn-dedent-v-t-h, sn-dedent-v-b-h
Its purpose is to provide an entry point that will:
```
1.  Locate, parse, and instantiate [snowmobile.toml](./snowmobile_toml.md#snowmobiletoml) 
    as a {class}`~snowmobile.Configuration` object, 
    {attr}`sn.cfg <snowmobile.core.connection.Snowmobile.cfg>`
1.  Establish connections to {xref}`snowflake`
1.  Store the {xref}`SnowflakeConnection`, 
    {attr}`sn.con <snowmobile.core.connection.Snowmobile.con>`, and execute commands 
    against the database
+++

<hr class="sn-spacer-thick">
<hr class="sn-grey">
<hr class="sn-spacer-thick">

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

(snowmobile/usage)=
## Usage

```{div} sn-dedent-list, sn-depth1
- [Connecting](usage/snowmobile/connecting)
- [Executing Raw SQL](usage/snowmobile/executing)
- [Aliasing Credentials](usage/snowmobile/aliasing-credentials)
- [Parameter Resolution](usage/snowmobile/parameter-resolution)
- [Delaying Connection](usage/snowmobile/delaying-connection)
- [Specifying snowmobile.toml](usage/snowmobile/specifying-snowmobiletoml)
- [Using *ensure_alive*](usage/snowmobile/using-ensure-alive)
```


<hr class="sn-spacer-thick">

````{admonition} Setup
:class: toggle, todo, is-setup, toggle-shown, toggle-color-setup

(connector/usage/setup)=
**This section assumes the following about the contents of** 
[**snowmobile.toml**](./snowmobile_toml.md#snowmobiletoml):
1.  {ref}`[connection.credentials.creds1] <connection.credentials.creds1>`
    and {ref}`[connection.credentials.creds2]<connection.credentials.creds2>` are:
    1.  Populated with valid credentials
    1.  The first and second credentials stored respectively
    1.  Aliased as *creds1* and *creds2* respectively
1.  {ref}`default-creds<connection.default-creds>` has been left blank
````

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

(usage/snowmobile/connecting)=
### Connecting to {xref}`snowflake`
<hr class="sn-green-thick-g">

``````{div} sn-tabbed-section

`````{tabbed} &nbsp;

 ````{div} sn-pre-code-s, sn-dedent-v-t-container
 ```{div} sn-dedent-v-t-container-neg2 
 Establishing a connection can be done with:
 ```
 ```` 
 ```{literalinclude} ../snippets/snowmobile/connecting.py
 :language: python
 :lines: 4-6
 ```

 ```{div} sn-pre-code-s 
 Here's some basic information on the composition of `sn`:
 ```
 ```{literalinclude} ../snippets/snowmobile/connecting.py
 :language: python
 :lines: 8-10
 ```

 <hr class="sn-green-thin" style="margin-top: 0.9rem; margin-bottom: -0.2rem;">

 ````{div} sn-pre-code-s
 Given [{fa}`cog`](connector/usage/setup), `sn` is implicitly using the same connection 
 arguments as:
 ````
 ```{literalinclude} ../snippets/snowmobile/connecting.py
 :language: python
 :lines: 12-12
 ```

```{div} sn-pre-code-s
 Here's some context on how to think about these two instances of
 {class}`~snowmobile.core.Snowmobile`:
 ```
 ```{literalinclude} ../snippets/snowmobile/connecting.py
 :language: python
 :lines: 14-16
 ```
 ```{div} sn-snippet
 [{fa}`file-code-o` connecting.py](../snippets.md#connectingpy)
 ```
`````
```````

<hr class="sn-spacer-thick">

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

(usage/snowmobile/executing)=
### Executing Raw SQL
<hr class="sn-green-thick-g">

````````{div} sn-tabbed-section
 
 ``````{tabbed} &nbsp;
 ```{div} sn-dedent-v-b-container-neg2
 *The following three methods are available for statement execution directly 
 off* <a class="fixture-sn" href="../index.html#fixture-sn"></a>.
 ```
 
 `````{tabbed} sn.query()
 ````{div} sn-rm-code-margin
 ```{literalinclude} ../snippets/snowmobile/executing.py
 :language: python
 :lines: 9-10
 ```
 ````
 `````

 ````{tabbed} +
  {meth}`~snowmobile.core.connection.Snowmobile.query()` implements 
  {meth}`pandas.read_sql` for querying results into a {class}`pandas.DataFrame`. 

  ```{literalinclude} ../snippets/snowmobile/executing.py
  :language: python
  :lines: 9-17
  :emphasize-lines: 4-10
  ```

  <hr class="sn-green">
  
 ````

 ````{tabbed} sn.ex()
 :new-group:
 ```{literalinclude} ../snippets/snowmobile/executing.py
 :language: python
 :lines: 21-22
 ```
 ````
 ````{tabbed} +
    
   {meth}`~snowmobile.core.connection.Snowmobile.ex()` implements
   {meth}`SnowflakeConnection.cursor().execute()` for executing commands 
   within a {xref}`SnowflakeCursor`.
 
   ```{literalinclude} ../snippets/snowmobile/executing.py
   :language: python
   :lines: 21-27
   :emphasize-lines: 4-8 
   ```
   
   <hr class="sn-green">
   
 ````

 ````{tabbed} sn.exd()
 :new-group:
 ```{literalinclude} ../snippets/snowmobile/executing.py
 :language: python
 :lines: 31-32
 ```
 ````

 ````{tabbed} +
  {meth}`~snowmobile.core.connection.Snowmobile.exd()` implements
  {meth}`SnowflakeConnection.cursor(DictCursor).execute()` for 
  executing commands within {xref}`DictCursor`. 

  ```{literalinclude} ../snippets/snowmobile/executing.py
  :language: python
  :lines: 31-39
  :emphasize-lines: 4-10
  ```
  
  <hr class="sn-green">
  
 ````

 ```{div} sn-snippet-trunc
 [{fa}`file-code-o` executing.py](../snippets.md#executingpy)
 ```


`````{admonition} SnowflakeCursor / DictCursor
:class: note, toggle, toggle-shown, sn-indent-cell, sn-indent-h-sub-cell-right

 ````{tabbed} Note
 The accessors `sn.cursor` and `sn.dictcursor` are **properties** of
 {attr}`~snowmobile.Snowmobile` that return a new instance each time they are 
 accessed. Depending on the intended use of {xref}`SnowflakeCursor` or
 {xref}`DictCursor`, it could be better to store an instance for re-referencing
 as opposed to repeatedly instantiating new instances off `sn`.
 ````
 
 ````{tabbed} +
 The below demonstrates the difference between calling two methods on
 the {attr}`~snowmobile.Snowmobile.cursor` property compared to on the same
 instance of {xref}`SnowflakeCursor`.
 ```{literalinclude} ../snippets/snowmobile/connector_cursor_note.py
  :language: python
  :lines: 5-17
 ```
 
 ```{div} sn-snippet
 [{fa}`file-code-o` connector_cursor_note.py](../snippets.md#connector_cursor_notepy)
 ```
 ````

`````
``````
````````


+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

`````{admonition} Naming Convention
:class: tip, toggle

````{tabbed} Tip
The following convention of variable/attribute name to associated object is
used throughout {ref}`snowmobile`'s documentation and source code, including in 
method signatures:
- **`sn`**: {class}`snowmobile.Snowmobile`
- **`cfg`**: {class}`snowmobile.Configuration`
- **`con`**: {xref}`snowflake.connector.SnowflakeConnection`
- **`cursor`**: {xref}`snowflake.connector.cursor.SnowflakeCursor`
````

````{tabbed} +

```{div} sn-pre-code-s
For example, see the below attributes of {class}`~snowmobile.core.Snowmobile`:
```
```{literalinclude} ../snippets/snowmobile/inspect_connector.py
:language: python
:lines: 5-15
```
```{div} sn-snippet-hanging
[{fa}`file-code-o` inspect_connector.py](../snippets.md#inspect_connectorpy)
```
<hr class="sn-spacer">

````
`````

<hr class="sn-spacer">

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

(usage/snowmobile/aliasing-credentials)=
### Aliasing Credentials
<hr class="sn-green-thick-g">

````````{div} sn-tabbed-section
 
 ``````{tabbed} &nbsp;
 The [default snowmobile.toml](./snowmobile_toml.md#file-contents) contains
 scaffolding for two sets of credentials, aliased `creds1` and `creds2` 
 respectively.

 By changing `default-creds = ''` to `default-creds = 'creds2'`, 
 [Snowmobile](/usage/snowmobile) will use the credentials from `creds2` 
 regardless of where it falls relative to all the other credentials stored.
 
 ```{div} sn-pre-code-s
 The change can be verified with:
 ```
 ```{literalinclude} ../snippets/snowmobile/verify_default_alias_change.py
 :language: python
 :lines: 5-11
 ```
 ```{div} sn-snippet
 [{fa}`file-code-o` verify_default_alias_change.py](../snippets.md#verify_default_alias_changepy)
 ```
 ``````

````````

<hr class="sn-spacer-thick">

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

(usage/snowmobile/parameter-resolution)=
### Parameter Resolution
<hr class="sn-green-thick-g">

````````{div} sn-tabbed-section

 ```````{tabbed} -
 
  ```{div} sn-hanging-p
  <a class="fixture-sn" href="../index.html#fixture-sn"></a> will look in the following 
  three places to compile the connection arguments that it passes to 
  {xref}`snowflake.connector.connect()` when establishing a connection:
  ```
  1. {ref}`[connection.default-arguments]<connection.default-arguments>`
  1. {ref}`[connection.credentials.alias_name]<connection.credentials.creds1>`
  1. Keyword arguments passed to {meth}`snowmobile.connect()`
  
  <hr class="sn-spacer2">
  <hr class="sn-green-thin">
  
  ```{div} sn-dedent-v-b-h
  If the same argument is defined in more than one entry point, the **last** 
  value found will take precedent; the purpose of this resolution order is 
  to enable:
  ```
  -   Embedding connection arguments (e.g. timezone or transaction mode) 
      within an aliased credentials block whose **values** differ from defaults
      specified in {ref}`[connection.default-arguments]<connection.default-arguments>`
  -   Superseding any connection parameters configured in [](./snowmobile_toml.md) 
      with keyword arguments passed directly to {meth}`snowmobile.connect()`
      
  ```````
  
 ```````{tabbed} Details
 
 The way <a class="fixture-sn" href="../index.html#fixture-sn"></a> implements 
 resolving connection parameters from multiple entry points is outlined below.
 
 <hr class="sn-green-thin">
 
 ```{div} sn-pre-code-s
 The {ref}`[connection.default-arguments]<connection.default-arguments>` and 
 {ref}`[connection.credentials.alias_name]<connection.credentials.creds1>` are 
 merged as the {attr}`~snowmobile.core.cfg.connection.Connection.connect_kwargs` 
 property of {attr}`~snowmobile.core.cfg.connection.Connection` with:
 ```
 ```{code-block} python
 :emphasize-lines: 4,4
     @property
     def connect_kwargs(self) -> Dict:
         """Arguments from snowmobile.toml for `snowflake.connector.connect()`."""
         return {**self.defaults, **self.current.credentials}
 ```
  
 +++
 ```{div} sn-post-code, sn-pre-code-s
   {attr}`~snowmobile.core.cfg.connection.Connection.connect_kwargs`
   is then combined with keyword arguments passed to {meth}`snowmobile.connect()` 
   within the method itself as the {attr}`~snowmobile.Snowmobile.con` attribute
   of <a class="fixture-sn" href="../index.html#fixture-sn"></a> is being set:
 ```
 ```{code-block} python
 :emphasize-lines: 8-9
 
     def connect(self, **kwargs) -> Snowmobile:
         """Establishes connection to Snowflake.
         ...
         """
         try:
             self.con = connect(
                 **{
                     **self.cfg.connection.connect_kwargs,  # snowmobile.toml
                     **kwargs,  # any kwarg over-rides
                 }
             )
             self.sql = sql.SQL(sn=self)
             print(f"..connected: {str(self)}")
             return self
 
         except DatabaseError as e:
             raise e
 ```
 ```````
````````

<hr class="sn-spacer-thick">

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

(usage/snowmobile/delaying-connection)=
### Delaying Connection
<hr class="sn-green-thick-g">

````````{div} sn-tabbed-section

 ```````{tabbed} -
 ```{div} sn-hanging-p
 Sometimes it's helpful to create a {class}`~snowmobile.Snowmobile` without 
 establishing a connection; this is accomplished with:
 ```
 
 ```{code-block} python
 :emphasize-lines: 3,3
 import snowmobile
 
 sn = snowmobile.connect(delay=True)
 ```
 
 When provided with `delay=True`, the 
 <a class="fixture-sn" href="../index.html#fixture-sn"></a> that's returned omits 
 connecting to {xref}`snowflake` upon its instantiation; its 
 {attr}`~snowmobile.Snowmobile.con` attribute is *None*, but its 
 {attr}`~snowmobile.Snowmobile.cfg` attribute is a
 fully valid {class}`~snowmobile.core.configuration.Configuration` object.
 
 See the tabbed *Examples* for additional information.
 ```````
 
 ```````{tabbed} Example: Implicit Connection
 (delaying-connection-example)=
 When provided with `delay=True`, the {attr}`~snowmobile.Snowmobile.con` 
 attribute of <a class="fixture-sn" href="../index.html#fixture-sn"></a> will 
 be *None* until a method is called on it that requires a connection. 
 
 If such a method is invoked, a call is made by 
 <a class="fixture-sn" href="../index.html#fixture-sn"></a> to
 {xref}`snowflake.connector.connect()`, a connection established, and the 
 attribute set.
 ```{literalinclude} ../snippets/snowmobile/connector_delayed1.py
 :language: python
 :lines: 5-15
 ```
 
 ```{div} sn-snippet
 [{fa}`file-code-o` connector_delayed1.py](../snippets.md#connector_delayed1py)
 ```
 ```````
 
 ```````{tabbed} Example: Explicit Connection
 In addition to implictly connecting by executing a query, the
 {meth}`~snowmobile.connect()` method can be called on 
 an existing instance of 
 <a class="fixture-sn" href="../index.html#fixture-sn"></a>; this
 will establish an initial connection if 
 <a class="fixture-sn" href="../index.html#fixture-sn"></a>
 was created with `delay=True` or a new session with the existing connection
 arguments otherwise.
 ```{literalinclude} ../snippets/snowmobile/connector_delayed2.py
 :language: python
 :lines: 5-21
 ```
 
 ```{div} sn-snippet
 [{fa}`file-code-o` connector_delayed2.py](../snippets.md#connector_delayed2py)
 ```
 ```````
 
````````

<hr class="sn-spacer-thick">

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

(usage/snowmobile/specifying-snowmobiletoml)=
### Specifying [snowmobile.toml](./snowmobile_toml.md)
<hr class="sn-green-thick-g">

````````{div} sn-tabbed-section

 ```````{tabbed} From File Path
 A full path ({class}`pathlib.Path` or {class}`str`) to a 
 [snowmobile.toml](./snowmobile_toml.md) file can be provided to the 
 `from_config` parameter to instantiate <a class="fixture-sn" href="../index.html#fixture-sn"></a> 
 from a specific configuration file. 
    
 ```{div} sn-pre-code-s
 In practice, this looks like:
 ```
 ```{literalinclude} ../snippets/snowmobile/specifying_configuration.py
 :language: python
 :lines: 5-11
 :emphasize-lines: 6,6
 ```
 
 ```{div} sn-snippet
 [{fa}`file-code-o` specifying_configuration.py](../snippets.md#specifying_configurationpy)
 ```
 
 ```{div} sn-hanging-p
 This will bypass any checks for a cached path and is useful for:
 ```
 1. Testing different sets of configuration options without altering the 
    original [snowmobile.toml](./snowmobile_toml.md) file
 1. Binding a specific configuration with a process for sql-parsing purposes 
 1. Hard coding the configuration source in processes that have access to 
    limited file systems (e.g. containers or VMs)  
 ```````
 
 ```````{tabbed} From File Name
 [Snowmobile](#snowmobile) caches locations based on the file **name** 
 provided to the `config_file_nm` parameter of {meth}`snowmobile.connect()`,
 the default value of which is `snowmobile.toml`.
 
 If an alternate file name is provided, it will be located and its location
 cached in the same way as the global [snowmobile.toml](./snowmobile_toml.md) 
 file so that future instances of 
 <a class="fixture-sn" href="../index.html#fixture-sn"></a> 
 on the same machine can make use of it upon instantiation without having to
 re-locate it.
 
 <hr class="sn-spacer2">
 <hr class="sn-green-thin">
  
 (specifying_configuration/setup)=
 The below codes are a contrived example demonstrating this behavior in practice. 
 
 ````{admonition} Setup
 :class: todo, is-setup, toggle-shown, toggle, sn-dedent-v-t-container
 All code blocks in this example are from 
 [the same code file](../snippets.md#specifying_configuration2py), assumed
 to be executed in full starting with code directly below in which 
 a second configuration file called *snowmobile2.toml* is created in the same 
 folder as the global [*snowmobile.toml*](./snowmobile_toml.md) file.
 ```{literalinclude} ../snippets/snowmobile/specifying_configuration2.py
 :language: python
 :lines: 7-17
 ```
 <hr class="sn-spacer-thin">
 ````
 
 ```{div} sn-hanging-p
 Below, {any}`alt_sn()` is used to create `sn_alt1` and `sn_alt2`,
 representing an initial and future instance of 
 <a class="fixture-sn" href="../index.html#fixture-sn"></a> respectively:
 ```
 ```{literalinclude} ../snippets/snowmobile/specifying_configuration2.py
 :language: python
 :lines: 22-39
 :emphasize-lines: 12-13
 ``` 
 
 <hr class="sn-spacer2">
 
 ```{div} sn-hanging-p
 Cleanup is done with the following two lines which remove the 
 *snowmobile2.toml* file created during the 
 [{fa}`cog`](specifying_configuration/setup) for this example:
 ```
 ```{literalinclude} ../snippets/snowmobile/specifying_configuration2.py
 :language: python
 :lines: 45-46
 ```
 ```{div} sn-snippet
 [{fa}`file-code-o` specifying_configuration2.py](../snippets.md#specifying_configuration2py)
 ```
 ```````

````````

<hr class="sn-spacer-thick">

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

(usage/snowmobile/using-ensure-alive)=
### Using ensure_alive
<hr class="sn-green-thick-g">

````````{div} sn-tabbed-section

 ```````{tabbed} &nbsp;
 Controlling the behavior of {class}`~snowmobile.Snowmobile` when a connection 
 is lost or intentionally killed is done through the 
 {attr}`~snowmobile.Snowmobile.ensure_alive` parameter. 
 
 Its default value is *True,* meaning that if the 
 {attr}`~snowmobile.Snowmobile.alive` property evaluates to *False*, **and a 
 method is invoked that requires a connection,** it will re-connect to 
 {xref}`snowflake` before continuing execution.
 
 ```{admonition} Note
 :class: note, sn-dedent-v-container, sn-indent-cell, sn-indent-h-sub-cell-right
 A re-established connection will not be on the same session as the original 
 connection.
 
 See [this snippet](../snippets.md#ensure_alivepy) for additional details.
 ```
 ```````

````````

<hr class="sn-spacer-thick">

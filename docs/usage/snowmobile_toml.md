(snowmobile.toml)=
# *snowmobile.toml*
<hr class="sn-grey">
<div class="sn-link-container2">
<a 
    class="sphinx-bs badge badge-primary text-white reference external sn-api" 
    href="../autoapi/snowmobile/core/configuration/index.html" 
    title="API Documentation">
        <span>snowmobile.core.configuration</span>
</a>
<a 
    class="sphinx-bs badge badge-primary text-white reference external sn-api" 
    href="../autoapi/snowmobile/core/cfg/index.html" 
    title="API Documentation">
        <span>snowmobile.core.cfg</span>
</a>
</div>

The parsed and validated form of [snowmobile.toml](#snowmobiletoml) is a 
{class}`~snowmobile.core.configuration.Configuration` object. 

All parsing of the file is done within {mod}`snowmobile.core.cfg`, in which 
sections are split at the root and fed into {xref}`pydantic's` glorious 
API to define the schema and impose (evolving) validation where needed.

Once validated, the {class}`~snowmobile.core.Configuration` object serves as a 
namespace for the contents/structure of the configuration file and utility 
methods implemented on top of them, with the rest of the API accessing it as the 
{attr}`~snowmobile.Snowmobile.cfg` attribute of
<a class="fixture-sn" href="../index.html#fixture-sn"></a>.


<hr class="sn-grey">
<hr class="sn-spacer-thick">

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

(inspecting-cfg)=
### Inspecting {attr}`sn.cfg`
<hr class="sn-green-thick-g">

````````{div} sn-tabbed-section

 ```````{tabbed} &nbsp;
 ```{div} sn-pre-code-s
 The {class}`~snowmobile.Configuration` model is accessed as the 
 {attr}`~snowmobile.Snowmobile.cfg`
 attribute of {class}`~snowmobile.Snowmobile`; a straight-forward way to inspect
 its composition is to instantiate
 a [delayed instance](./snowmobile.md#delaying-connection) of
 <a class="fixture-sn" href="../index.html#fixture-sn"></a>: 
 ```
 ```{literalinclude} ../snippets/configuration/inspect_configuration.py
 :language: python
 :lines: 5-10
 ```
 
 ```{div} sn-pre-code-s 
 The following attributes of `sn.cfg` map to the root configuration 
 sections of [](#snowmobiletoml):
 ```
 ```{literalinclude} ../snippets/configuration/inspect_configuration.py
 :language: python
 :lines: 12-16
 ```
 
 ```{div} sn-snippet
 [{fa}`file-code-o` inspect_configuration.py](../snippets.md#inspect_configurationpy)
 ```
 
 ```{admonition} Tip
 :class: tip
 The usage documentation contains detail on how changes to 
 [snowmobile.toml values](#file-contents) flow through to
 <a class="fixture-sn" href="../index.html#fixture-sn"></a>
 and impact the its implementation.
 ```
 ```````

````````

<hr class="sn-green-rounded-g">
<hr class="sn-spacer-thick">

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

(connection.root)=
## Glossary
<hr class="sn-green-thick">

<br>

````{div} sn-def

+++++++++++++
+++++++++++++
+++++++++++++
 
 (connection.default-creds)=
 `[connection]`\
 *Configuration options
 used by* <a class="fixture-sn" href="../index.html#fixture-sn"></a> 
 *when establishing connections to {xref}`snowflake`*
 
 (connection.credentials)=
 `default-creds`\
 *The credentials (alias) to use by default in absence of one provided to
 the* `creds` *keyword argument to {meth}`snowmobile.connect()`*


 (connection.credentials.creds1)=
 `[connection.credentials]`\
 *Groups subsections of credentials, each declared with the structure of
 ``[connection.credentials.credentials_alias]``*


 (connection.credentials.creds2)=
 `[connection.credentials.creds1]`\
 *Store your first set of credentials here;* `creds1` *is a credentials alias*

 (connection.default-arguments)=
 `[connection.credentials.creds2]`\
 *Store as many credentials as you want following this format; aliases must be unique*


 (loading.root)=
 `[connection.default-arguments]`\
 *Credentials-agnostic keyword arguments to pass to 
 {xref}`snowflake.connector.connect()`*
 
 <hr class="sn-spacer">

+++++++++++++
+++++++++++++
+++++++++++++

 (loading.default-table-kwargs)=
 `[loading]`\
 *Configuration options for data loading used by [snowmobile.Table](./table)*

 (loading.put)=
 `[loading.default-table-kwargs]`\
 *Default specifications for a* [**snowmobile.Table**](./table.ipynb) *object*

 (loading.copy-into)=
 `[loading.put]`\
 *Default arguments to include in Snowflake's {xref}`put file from stage` command*

 (loading.save-options)=
 `[loading.copy-into]`\
 *Default arguments to include in Snowflake's {xref}`copy into table` command*

 <hr class="sn-spacer">

 (loading.save-options.snowmobile_default_csv)=
 `[loading.save-options]`\
 *Groups subsections of save-options*

 (loading.save-options.snowmobile_default_psv)=
 `[loading.save-options."snowmobile_default_csv"]`\
 *Default file-save options for **snowmobile_default_csv***

 (external-sources.root)=
 `[loading.save-options."snowmobile_default_psv"]`\
 *Default file-save options for **snowmobile_default_psv***

 <hr class="sn-spacer">
 
+++++++++++++
+++++++++++++
+++++++++++++

 (script.root)=
 `[external-sources]`\
 *Defines paths to custom sources referenced by different {xref}`snowmobile` objects*

  `ddl`\
  *Posix path to a sql file containing DDL for file formats*

  `extension`\
  *Posix path to [snowmobile-ext.toml](file-contents-snowmobile-ext-toml)*
  
  <hr class="sn-spacer">

+++++++++++++
+++++++++++++
+++++++++++++

 (script.export-dir-name)=
 `[script]`\
 *Configurations for [*snowmobile.Script*](./script.ipynb)*

 (script.patterns.core)=
 `export-dir-name`\
 *Directory name for generated exports (markup and stripped sql scripts)* 

 <hr class="sn-spacer">
 
 (script.patterns.wildcards)=
 `[script.patterns.core]`\
 *Core patterns used for markup identification*

 `open-tag`\
 *Open-pattern for in-script tags*
 
 `close-tag`\
 *Close-pattern for in-script tags*
 
 `description-delimiter`\
 *Delimiter separating description from other statement attributes*
 
 `description-index-prefix`\
 *String with which to prepend a statement's index position when deriving 
 {attr}`~snowmobile.core.name.Name.desc_ge`*

 <hr class="sn-spacer">
 
 (script.qa)=
 `[script.patterns.wildcards]`\
 *Defines wildcards for attribute names within script tags*

 `wildcard-character`\
 *The literal character to use as a wildcard*
 
 `wildcard-delimiter`\
 *The literal character with which to delimit wildcards*
 
 `denotes-paragraph`\
 *Indicates the attribute **value** should be rendered as free-form markdown as opposed to a plain text bullet*
 
 `denotes-no-reformat`\
 *Indicates the attribute **name** should be left exactly as it is entered in the script as opposed to title-cased*
 
 `denotes-omit-name-in-output`\
 *Indicates to omit the attribute's **name** in rendered output*

 <hr class="sn-spacer">

 (script.qa.default-tolerance)=
 `[script.qa]`\
 *Default arguments for **QA-Diff** and **QA-Empty** Statements*
 
 `partition-on`\
 *Pattern to identify the field on which to partition data for comparison*

 `compare-patterns`\
 *Pattern to identify fields being compared*

 `ignore-patterns`\
 *Pattern to identify fields that should be ignored in comparison*

 `end-index-at`\
 *Pattern to identify the field marking the last index column*
 
 <hr class="sn-spacer">
 
 (script.markdown)=
 `[script.qa.default-tolerance]`\
 *Default values for QA-Delta tolerance levels*

  `relative`\
  *Default relative-difference tolerance*

  `absolute`\
  *Default absolute-difference tolerance*

 <hr class="sn-spacer">

 (script.markdown.attributes)=
 `[script.markdown]`\
 *Configuration for markdown generated from .sql files*

 `default-marker-header`\
 *Header level for [markers](./script.ipynb#markers) (h1-h6)*

 `default-statement-header`\
 *Header level for statements (h1-h6)*

 `default-bullet-character`\
 *Character to use for bulleted lists*

 `wrap-attribute-names-with`\
 *Character to wrap attribute **names** with*

 `wrap-attribute-values-with`\
 *Character to wrap attribute **values** with*

 `include-statement-index-in-header`\
 *Denotes whether or not to include a statement's relative index number in its header along with its name*

 `limit-query-results-to`\
 *Maximum number of rows to include for a statement's rendered **Results***

 <hr class="sn-spacer">

 (script.markdown.attributes.markers)=
 `[script.markdown.attributes]`\
 *Configuration options for specific attributes*

 <hr class="sn-spacer">

 (script.markdown.attributes.script)=
 `[script.markdown.attributes.markers]`\
 *Pre-defined marker configurations*

 <hr class="sn-spacer">

 (script.markdown.attributes.markers.appendix)=
 `[script.markdown.attributes.markers."__script__"]`\
 *Scaffolding for a template marker called '\_\_script\_\_'*

 `as-group`\
 *The literal text within which to group associated attributes as sub-bullets*

 `team`\
 *A sample attribute called 'team'*

 `author-name`\
 *A sample attribute called 'author-name'*

 `email`\
 *A sample attribute called 'email'*

 <hr class="sn-spacer">

 (script.markdown.attributes.reserved.rendered-sql)=
 `[script.markdown.attributes.markers."__appendix__"]`\
 *Scaffolding for a second template marker called '\_\_appendix\_\_'*

 <hr class="sn-spacer">

 (script.markdown.attributes.reserverd.query-results)=
 `[script.markdown.attributes.reserved.rendered-sql]`\
 *Configuration options for a reserved attribute called 'rendered-sql'*

 `include-by-default`\
 *Include attribute by default for each {class}`~snowmobile.core.Section`*

 `attribute-name`\
 *The attribute's name as it is declared within a [tag](./script.md#tags)*

 `default-to`\
 *The attribute name as it should be interpreted when parsed*
 
 <hr class="sn-spacer">
 
 (script.markdown.attributes.from-namespace)=
 `[script.markdown.attributes.reserved.query-results]`\
 *Configuration for a reserved attributes called `query-results`*

 `include-by-default`\
 *Include attribute by default for each {class}`~snowmobile.core.Section`*

 `attribute-name`\
 *The attribute's name as it is declared within a [tag](./script.md#tags)*

 `default-to`\
 *The attribute name as it should be interpreted when parsed*

 `format`\
 *Render format for the tabular results; markdown or html*
 
  <hr class="sn-spacer">
 
 (script.markdown.attributes.groups)=
 `[script.markdown.attributes.from-namespace]`\
 *List of {class}`~snowmobile.core.Statement` attributes to include in 
 its {class}`~snowmobile.core.Section`; includes non-default attributes
 set on an instance*

 <hr class="sn-spacer">

 (script.markdown.attributes.order)=
 `[script.markdown.attributes.groups]`\
 *Defines attributes to be grouped together within a sub-bulleted list*

 <hr class="sn-spacer">

 (script.tag-to-type-xref)=
 `[script.markdown.attributes.order]`\
 *Order of attributes within a {class}`~snowmobile.core.Statement`-level section*

 <hr class="sn-spacer">

 (sql.root)=
 `[script.tag-to-type-xref]`\
 *Maps tagged attributes to data types; will error if an attribute included here
 cannot be parsed into its specified data type*

 <hr class="sn-spacer">

 (file-contents-ref)=
 `[sql]`\
 *SQL parsing specifications for a {class}`~snowmobile.core.Statement`*

 (desc-is-simple)=
 `provided-over-generated`\
 *{class}`~snowmobile.core.name.Name.nm_pr` 
 takes precedent over {class}`~snowmobile.core.name.Name.nm_ge`*

 (named-objects)=
 `desc-is-simple`\
 *`True` invokes additional parsing into {class}`~snowmobile.core.name.Name.desc` 
 and {class}`~snowmobile.core.name.Name.obj`*

 (generic-anchors)=
 `named-objects`\
 *Literal strings to search for matches that qualify as a {xref}`snowflake`
 object if included within the first line of a statement's sql and not equal
 to its first keyword*

 (keyword-exceptions)=
 `generic-anchors`\
 *Generic anchors to use for a given keyword; will be used for generated statements
 if* `desc-is-simple` *is* **True**
 
 (information-schema-exceptions)=
 `keyword-exceptions`\
 *Alternate mapping for first keyword found in a command*
 
 `information-schema-exceptions`\
 *Map {xref}`snowflake` objects to their `information_schema.*` table name
 if different than the plural form of the object; (e.g. `schema` information 
 is in `information_schema.schemata` not `information_schema.schemas`)*

````

<hr class="sn-spacer-thick3">

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

## File Contents
<hr class="sn-green-thick">

```{literalinclude} ../../snowmobile/core/pkg_data/snowmobile-template.toml
:language: toml
:lineno-start: 1
```

<hr class="sn-spacer-thick2">

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

(file-contents-snowmobile-ext-toml)=
## snowmobile-ext.toml
<hr class="sn-green-thick">

```{literalinclude} ../../snowmobile/core/pkg_data/snowmobile-ext.toml
:language: toml
:lineno-start: 1
```


% indentation for glossary
<style>

.md-typeset .tabbed-set.docutils {
    margin-top: 0;
    margin-bottom: -0.5rem;
}

.sn-dedent-v-container .tabbed-content.docutils  {
    margin-bottom: -0.5em;
}

.sn-def :last-child {
    margin-bottom: -0.2em;
}

.tabbed-content.docutils {
    padding-left: 1rem;
    margin-bottom: 0.5rem;
    border-top: unset;
}

.tabbed-content {
    box-shadow: none;
}

@media only screen and (max-width: 59.9375em) {
    .tabbed-set>label {
        padding: 0.8rem 0.1rem 0;
    }
}
</style>

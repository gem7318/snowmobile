(usage/script)=
# Script
<!--suppress ALL -->
<hr class="sn-grey">
<a
    class="sphinx-bs badge badge-primary text-white reference external sn-api sn-link-container2"
    href="../autoapi/snowmobile/core/script/index.html"
    title="API Documentation">
    <span>snowmobile.core.script</span>
</a>

```{admonition} Warning: This page is incomplete.
 :class: error, sn-inherit-overflow
 &nbsp;
```

```{div} sn-dedent-v-b-h
{class}`snowmobile.Script` parses a raw sql file into a composition of objects 
that can be leveraged for:
```
```{div} sn-indent-h-cell-left-m, sn-block-list
>Documentation and standardization of sql
> 
>Access to individual statements within a script
> 
>Lightweight control flow and QA
> 
>Code generation and warehouse cleanup
```

<hr class="sn-spacer-thick">
<hr class="sn-grey">
<hr class="sn-spacer-thick">

````{admonition} Simplest Execution Mechanism
:class: tip, toggle, sn-code-pad

 ```{div} sn-unset-code-margins
 [](#script) is useful for operating on deep, analytic sql that is otherwise 
 difficult to manage; *the {xref}`execute_stream() method` 
 from the {xref}`snowflake.connector2` is the most straight-forward way to
 execute a raw sql file,* the API for which can be accessed from an instance of 
 <a class="fixture-sn" href="../index.html#fixture-sn"></a> with: 
 ```
 ```{code-block} python
 :emphasize-lines: 4,4
 from codecs import open
 
 with open(sqlfile, 'r', encoding='utf-8') as f:
    for cur in sn.con.execute_stream(f):
        for ret in cur:
            print(ret)
 ```

````

<hr class="sn-spacer-thick">

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

## Overview

```{div} sn-dedent-list
- [](script/model-intro)
  - [](script/model-intro/core-objects)
  - [Sections & Markup](script/model-intro/sections-markup)
- [](#statements)
  - [Quick Intro](script/statements/quick-intro)
  - [Statement Names](script/statements/statement-names)
- [](#markup)
  - [](#tags)
   - [Single-Line](#single-line-tags)
   - [Multi-Line](#multi-line-tags)
  - [](#markers)
  - [](#patterns)
```

<hr class="sn-spacer-thick2">

<body>
 <div class="sn-section-parent">

 (script/model-intro)=
 ### Model Intro
 ---

 <div class="sn-section-connector">&nbsp;</div>
 <div class="sn-section">

 (script/model-intro/script)=
 #### Script
 ----

  <div class="sn-sub1 sn-dedent-sub">

 ```{admonition} Missing
  :class: error, sn-inherit-overflow
  &nbsp;
 ```


 </div>
 <br>

 (script/model-intro/core-objects)=
 #### Core Objects
 ----

  <div class="sn-sub1">
  <hr class="sn-sub-h4">

 When [](#script) parses a string of sql, it identifies and stores 
 [statements](#statements), [tags](#tags), and [markers](#markers):

 ````{div} sn-def, sn-dedent-v-t-container-neg, sn-linear-gradient-background, sn-thin-left-border-g
 
  <hr class="sn-spacer-thin2">
 
  {class}`~snowmobile.core.statement.Statement`\
  *A valid sql command, a standard set of attributes, and 
  any information (optionally) provided in a [tag](#tags)*
  
  [**Tag**](#tags)\
  *An arbitrary amount of information wrapped in a pre-defined, sql-compliant 
  pattern that is parsable by {xref}`snowmobile`*
  
  [**Marker**](#markers)\
  *A collection of information within a [tag](#tags) that is associated with
  the script (or a subset of it) as opposed to an individual statement*

  <hr class="sn-spacer">
  
 ````

 These can be used to clearly define the following within a sql script:
 ```{div} sn-caret-list, sn-blue-list
 - Setup / DDL commands
 - Processing / DML commands
 - Descriptive / contextual statements
 - Simple QA checks
 - Tear-down / drop commands 
 - Statement-level context 
 - Script-level information
 ```

 The zen of the class is to enable unambiguously denoting text and code
 that serve a purpose within a sql script; in particular, implemented in a way 
 that is easily identifiable/human-readable, can be post-processed 
 programmatically, and allows for other content to exist within the file that 
 is ignored by {xref}`snowmobile`.

 ```{admonition} Note
 :class: note, sn-indent-h-cell-left-m, sn-indent-h-cell-right-m
 [](#script) intentionally ignores **all** comments that are not part of a [tag](#tags). 
 ```

 </div>
 <br>

 (script/model-intro/sections-markup)=
 #### Sections & Markup
 ----

 <div class="sn-sub1 sn-dedent-sub">
 <hr class="sn-sub-h4">

 A {class}`~snowmobile.core.section.Section` can be instantiated from 
 a {class}`~snowmobile.core.statement.Statement` or a [Marker](#markers), and
 the {class}`~snowmobile.core.markup.Markup` class combines multiple
 sections into a single document:

 ````{div} sn-def, sn-dedent-v-t-container-neg, sn-linear-gradient-background, sn-thin-left-border-g
  
  <hr class="sn-spacer-thin2">
 
  {class}`~snowmobile.core.section.Section`\
  *Performs additional operations on the attributes from a 
  {class}`~snowmobile.core.statement.Statement` or a [Marker](#markers), typically
  to generate a 'headered' section in a markdown file or a sql statement stripped 
  of surrounding comments*
  
  [**Markup**](#markup)\
  *A context-specific collection of all sections within a script; capable of
  exporting markdown and tidied sql files*

  <hr class="sn-spacer">
  
 ````

 Calling the {meth}`doc()<snowmobile.core.script.Script.doc()>` method on a
 [](#script) will return a {class}`~snowmobile.core.cfg.script.Markup`
 of its contents.

 The {meth}`Markup.save()<snowmobile.core.markup.Markup.save()>` method will
 (by default) export a pair of files into a `.snowmobile` folder directly
 adjacent to the file with which the [](#script) was instantiated.
 
 A base case for this in practice is outlined in
 <a class="sn-example sn-link-pad" href="./script.html#script-example-intro-sql">
 <span>Example: **intro.sql** </span>
 </a>

 ```{admonition} Note
 :class: note, sn-indent-h-cell-left-m, sn-indent-h-cell-right-m
 (script-example-intro-sql)=
 The following options can be configured on an instance of
 {class}`~snowmobile.core.cfg.script.Markup` prior to calling
 {meth}`save()<snowmobile.core.markup.Markup.save()>`:
 - Target location
 - File names
 - File types
 - File contents   
 ```

   </div>
  </div>

 <br>
 <br>

 `````{admonition} Example: **intro.sql**
 :class: sn-example, toggle, toggle-shown

 <hr class="sn-spacer-thick2">
 
 ```{literalinclude} ../snippets/script/intro.sql
 :language: sql
 :lines: 6-21
 ```
 ```{div} sn-snippet
 [{fa}`file-code-o` intro.sql](../snippets.md#introsql)
 ```
 
 ````{div} sn-pre-code-s
 With a `path` to *intro.sql*, the following can be run:
 ````
 ```{literalinclude} ../snippets/script/intro.py
 :language: python
 :lines: 13-21
 :emphasize-lines: 9,9
 ```
 
 ```{div} sn-pre-code-s, sn-post-code
 Given *intro.sql* is here:
 ```
 ````{div} sn-inline-block-container 
 ```{code-block} bash
 sql/
 └─ intro.sql
 ```
 ````
 
 ```{div} sn-pre-code-s
 {meth}`markup.save()<snowmobile.core.markup.Markup.save()>` 
 created the `.snowmobile` directory and exported the following files:
 ```
 ````{div} sn-inline-block-container
 ```{code-block} bash
 :emphasize-lines: 4,5
 sql/
 ├─ intro.sql
 └─ .snowmobile/
    ├─ intro.md
    └─ intro.sql
 ```
 ````
 
 <hr class="sn-spacer-thick2">
 
 ````{tabbed} intro.md
 
 <div class="sn-markdown">
 <h1>intro.sql</h1>
 
 * **Authored-By**: _Some Chap or Lass_
 * **Authored-On**: _Some Day or Year_
 
 **Impetus**: *SQL is older than time and isn't going anywhere; might we allow a simple markup syntax?*
 
 <br>
 
 <h2>(1) create table~sample_table; DDL</h2>
 
 * **Description**: _This is an example statement description_
 
 ```sql
 create or replace table sample_table (
     col1 number(18,0),
     col2 number(18,0)
 );
 ```
 
 </div>
 
 ````

 ````{tabbed} intro.sql
 ```{literalinclude} ../snippets/script/.snowmobile/intro/intro.sql
 :language: sql
 :lines: 1-18
 ```
 ```` 
 
 `````

 </div>

<br>

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++


<div class="sn-section-parent">

 (script/statements/quick-intro)=
 ### Statements
 ---

 <div class="sn-section-connector">&nbsp;</div>
 <div class="sn-section toggle toggle-shown">


<hr class="sn-spacer-thick2">

`````{admonition} **script**
 :class: toggle, sn-fixture, sn-fixture-local, sn-unset-margins, sn-block, sn-code-pad, toggle-shown

 
 ```{div} sn-pre-code
 This section performs operations on the following {fa}`fixture script`: 
 ```
 ````{div} sn-indent-h-cell-even
 ```{literalinclude} ../snippets/script/overview-statement-intro.py
 :language: python
 :lines: 17-17
 ```
 ````
 ```{div} sn-indent-h-cell-text
 Where `path` ({class}`pathlib.Path` or {class}`str`) is a full path to 
 [overview.sql](script/statements/quick-intro).
 ```
 
 <div class="sn-indent-h-cell-even">
 <hr class="sn-blue">
 
 The 7 generic sql statements within 
 [overview.sql](script/statements/quick-intro) are arbitrary and chosen based only 
 on the loose criteria of:
 ```{div} sn-bold-list
 1.  Includes the minimum variety of [Statements](#statements) and [](#markup) 
     to demonstrate the fundamentals of how [](#script) parses sql
 1.  Is executable from top to bottom without requiring external setup
 ```
 
 </div>
 
 <hr class="sn-spacer-thick">
 
 ```{div} sn-snippet-h, sn-indent-h-cell
 [{fa}`file-code-o` overview.sql](../snippets.md#overviewsql)
 ```
 ````{div} sn-indent-h-cell-even
 ```{literalinclude} ../snippets/script/overview.sql
 :language: sql
 :lines: 3-32
 :emphasize-lines: 1, 6, 17, 20, 22, 24, 30
 ```
 ````
`````

<hr class="sn-spacer-thick">


 #### Intro
 ----

 <div class="sn-sub1">
 <hr class="sn-sub-h4">

 ```{div} sn-pre-code-s
 When a sql file is parsed by {class}`~snowmobile.Script`, each statement is
 identified and instantiated as its own
 {class}`~snowmobile.core.statement.Statement`.
  
 An overview of the statements within a script's context can be sent to the 
 console with {meth}`script.dtl()<snowmobile.Script.dtl()>`; in the case
 of [{fa}`fixture script`](script/statements/quick-intro), this looks like:
 ```
 ```{literalinclude} ../snippets/script/overview-statement-intro.py
 :language: python
 :lines: 18-18
 ```
 ````{div} sn-output
 ```{literalinclude} ../snippets/script/overview-statement-intro.py
 :language: python
 :lines: 21-29
 ```  
 ````
 
 <hr class="sn-grey-dotted sn-top-pad-hr-thick">
  
 ```{div} sn-pre-code-s
 Accessing the first and last statements of 
 [{fa}`fixture script`](script/statements/quick-intro)
 and inspecting a few of their attributes can be done with:
 ``` 
 ```{literalinclude} ../snippets/script/overview-statement-intro.py
 :language: python
 :lines: 33-42
 ```
 
 ```{div} sn-pre-code-s, sn-post-code
 A {class}`~snowmobile.core.Statement` can be interacted with from its parent
 [](#script) or stored and interacted with independently; for 
 example, here are two ways that the first statement in 
 [overview.sql](script/statements/quick-intro) can be executed: 
 ```
 ```{literalinclude} ../snippets/script/overview-statement-intro.py
 :language: python
 :lines: 45-46
 ```

 <hr class="sn-grey-dotted sn-top-pad-hr-thick">

 Those above are several amongst a set of {class}`~snowmobile.core.Statement` 
 attributes that can be used to alter the scope of a 
 [](#script).

 For example, the following snippet filters out `drop` and `select` statements 
 based on their {attr}`~snowmobile.core.name.Name.kw` attribute
 and returns a modified [{fa}`fixture script`](script/statements/quick-intro), `s`, 
 that can be operated on within that context:
 ```{literalinclude} ../snippets/script/overview-statement-intro.py
 :language: python
 :lines: 50-58
 ```
 ````{div} sn-output
 ```{literalinclude} ../snippets/script/overview-statement-intro.py
 :language: python
 :lines: 61-66
 ```
 ````  
 ```{div} sn-snippet, sn-indent-to-output
 [{fa}`file-code-o` overview-statement-intro.py](../snippets.md#overview-statement-intropy)
 ```
 
 (script/statements/statement-names)= 
 The following section outlines how these components are constructed.


 </div>

 <br>

 #### Statement Names
 ----

 <div class="sn-sub1">
 <hr class="sn-sub-h4">
 
 ```{div} sn-dedent-v-b-h-m
 *The intent of the following taxonomy is to define a standard such that the 
 name for a given statement is:*
 ```
 ```{div} sn-bold-list
 1. Constructed from attributes that can be unambiguously parsed from 
    a piece of raw sql
 1. Structured such that user *provided* names can be easily
    implemented and loosely parsed into the same set of attributes 
    as those *generated* from (**1**)
 ```
 
 <hr class="sn-grey-dotted sn-top-pad-hr">
 
 Every statement has a {class}`~snowmobile.core.name.Name` with a set of
 underlying properties that are used by the rest of the API; for each property, 
 there is a *generated* (**_ge**) and *provided* (**_pr**) attribute from 
 which its final value is sourced.

 (script/note1)=
 *Generated* attributes are populated for all statements, whereas only those
 with a name specified in a [tag](#tags) have populated *provided* attributes;
 consequently, a *provided* value takes precedent over its *generated* counterpart. 
 
 ````{admonition} Example: **nm**
 :class: sn-example
 ```{div} sn-pre-code-s
 The {class}`~snowmobile.core.name.Name.nm` value for a given statement will 
 be equivalent to its {attr}`~snowmobile.core.name.Name.nm_pr` if present and 
 its {attr}`~snowmobile.core.name.Name.nm_ge` otherwise.
 ```
 ````

 (script/statement/nm)=
 This resolution order is repeated across the underlying 
 components of {class}`~snowmobile.core.name.Name.nm`, documented in the
 following sections.

 <hr class="sn-grey-dotted">
 <hr class="sn-spacer-thick2">
 
 `````{admonition} **s1** & **s4**
 :class: toggle, toggle-shown, sn-fixture, sn-fixture-local, sn-block, sn-increase-margin-v-container, sn-code-pad
 
 The below statements, `s1` and `s4`, from 
 [{fa}`fixture script`](script/statements/quick-intro) are used throughout the 
 remaining examples in [this section](#statement-names). 
 ```{literalinclude} ../snippets/script/overview-statement-names.py
 :language: python
 :lines: 21-22
 :emphasize-lines: 4-5
 ```
 `````

 <hr class="sn-spacer-thick2">

 % (nm)
 ##### ***nm***
 
 ````{div} sn-def, sn-dedent-v-t-container-neg, sn-linear-gradient-background, sn-def-container-side-border
  
  <hr class="sn-spacer">
 
  ```{div} sn-block-indented-h
  >{anchor}{delimiter}{desc}
  ```
  {attr}`~snowmobile.core.name.Name.anchor`\
  *what operation is a statement performing*<br>
  <p class="sn-def-p"><em>on what kind of object is it operating</em></p>
    
  {attr}`~snowmobile.core.cfg.script.Core.delimiter`
  ```{div} sn-multiline-def
  *a* <a class="sn-conf" href="./snowmobile_toml.html#script-patterns-core">
   <span>configured value</span>
  </a>
  *with which to delimit the {attr}`~snowmobile.core.name.Name.anchor` and
  {attr}`~snowmobile.core.name.Name.desc`*
  ```
    
  {attr}`~snowmobile.core.name.Name.desc`\
  *A free-form piece of text associated with the statement*
  
  <hr class="sn-spacer">
  
  ````

% (-)
 ``````{tabbed} -
 :class-content: sn-light-shadow
 
 {attr}`~snowmobile.core.name.Name.nm` is the highest-level accessor
 for a {class}`~snowmobile.core.statement.Statement`.
 
 Its values for <a class="sn-local-fixture" href="./script.html#script-statement-nm">
  <span>s1 & s4</span>
 </a> (for example) can be inspected with:
 ```{literalinclude} ../snippets/script/overview-statement-names.py
 :language: python
 :lines: 24-25
 ```
 ``````
 
 ``````{tabbed} nm_pr
 :class-content: sn-light-shadow
 :class-label: sn-rm-background
 
 In determining the {attr}`~snowmobile.core.name.Name.nm` 
 for <a class="sn-local-fixture" href="./script.html#script-statement-nm">
  <span>s1</span> </a> specifically, [{fa}`fixture script`](script/statements/quick-intro) 
 is considering the following two lines of [overview.sql](script/statements/quick-intro):
  
 ```{literalinclude} ../snippets/script/overview.sql
 :language: sql
 :lines: 21-22
 ```
 
 ```{div} sn-post-code
 Each of these two lines above is the respective source for *provided* and 
 *generated* information about the statement called out 
 in <a class="sn-example" href="./script.html#script-note1">
 <span>Example: **nm**</span>
 </a>, the underlying values for which can be inspected in the same way:
 ```
 ```{literalinclude} ../snippets/script/overview-statement-names.py
 :language: python
 :lines: 36-46
 ```
 ``````
 

 <hr class="sn-spacer-thick">
 
 % (anchor =======================================================)
 ##### ***anchor***
 
 ````{div} sn-def, sn-dedent-v-t-container-neg, sn-linear-gradient-background, sn-def-container-side-border
 
 <hr class="sn-spacer">
 
 ```{div} sn-block-indented-h
 >{kw} {obj}
 ```
 {attr}`~snowmobile.core.name.Name.kw`\
 *the literal first sql keyword the statement contains*
 
 {attr}`~snowmobile.core.name.Name.obj`\
 *the in-warehouse object found in the first line of the statement* 
 
 <hr class="sn-spacer">
 ````

 ``````{tabbed} -
 :class-content: sn-light-shadow
 
 {attr}`~snowmobile.core.name.Name.anchor` represents all text to the left of
 the first {attr}`~snowmobile.core.cfg.script.Core.delimiter` and when 
 [*generated*](#statement-names) will fit the above structure to a varying
 degree depending on the sql being parsed and configurations in
 [](./snowmobile_toml.md). 

 For <a class="sn-local-fixture" href="./script.html#script-statement-nm">
  <span>s1 & s4</span>
 </a>:
 ```{literalinclude} ../snippets/script/overview-statement-names.py
 :language: python
 :lines: 30-31
 ```
 ``````

 <hr class="sn-spacer-thick">
 
 % (kw ===========================================================)
 (script-kw)=
 ##### ***kw***

 ``````{tabbed} -
 :class-content: sn-light-shadow

 {attr}`~snowmobile.core.name.Name.kw` is the literal first *keyword* 
 within the [command](https://docs.snowflake.com/en/sql-reference/sql-all.html)
 being executed by a statement's sql.
 
 For <a class="sn-local-fixture" href="./script.html#script-statement-nm">
  <span>s1 & s4</span></a>:
 ```{literalinclude} ../snippets/script/overview-statement-names.py
 :language: python
 :lines: 59-60
 ```
 
 ``````

 ``````{tabbed} keyword-exceptions
 :class-content: sn-light-shadow
 
 The {ref}`keyword-exceptions <keyword-exceptions>` section in the
 {ref}`[sql] <sql.root>` block of 
 {ref}`snowmobile-ext.toml <file-contents-snowmobile-ext-toml>`
 enables
 specifying an alternate keyword for a literal keyword parsed from a statement's
 sql; alternate keywords will populate the statement's  
 {attr}`~snowmobile.core.name.Name.kw_ge` as opposed to the literal keyword
 identified at the start of the statement:
 ```toml
    [sql.keyword-exceptions]
        "with" = "select"
 ```
 The default included above is the reason that the
 {attr}`~snowmobile.core.name.Name.kw` for both the following statements
 is `select` as opposed to `select` and `with` respectively:
 ```{literalinclude} ../snippets/script/keyword_exceptions.sql
 :language: sql
 :lines: 3-10
 ```
 ``````

 <hr class="sn-spacer-thick">
 
 % (obj ==========================================================)
 (script-obj)=
 ##### ***obj***


 ``````{tabbed} -
 :class-content: sn-light-shadow

 {attr}`~snowmobile.core.name.Name.obj` is determined by a case-insensitive, 
 full ('word-boundaried') search through the **first** line of a statement's
 sql for a match within a pre-defined set of values.
 
 ``````

 ``````{tabbed} named-objects
 :class-content: sn-light-shadow
 
 The values for which a match is checked are configured in the 
 {ref}`named-objects <named-objects>` section within the {ref}`[sql] <sql.root>` 
 block of {ref}`snowmobile-ext.toml<file-contents-snowmobile-ext-toml>`,
 included below.
 
 Matching is peformed against values in the **literal** order as they are 
 configured in {ref}`snowmobile-ext.toml<file-contents-snowmobile-ext-toml>`
 until a match is found or the list is exhausted; it is enforced that the object
 found cannot be equal to the {attr}`~snowmobile.core.name.Name.kw`
 for the statement.
 
 ```{code-block} toml
    named-objects = [
        # 'grant' statements
        "select",
        "all",
        "drop",

        # base objects
        "temp table",
        "transient table",
        "table",
        "view",
        "schema",
        "warehouse",
        "file format",

        # plural bases
        "tables",
        "views",
        "schemas",
    ]
 ```
 ````{admonition} Note
 :class: note, toggle, toggle-shown, sn-rm-t-m-code, sn-increase-margin-v-container

 The above order is as such so that table qualifiers for the following three 
 (types of) statements are reflected in the
 {attr}`~snowmobile.core.name.Name.obj` for each.
 
 <hr class="sn-spacer-thick">
 
 ```sql
 -- obj = 'table'
 create table any_table as 
 select 1 as any_col;
 
 -- obj = 'transient table'
 create transient table any_table2 as 
 select 1 as any_col;
 
 -- obj = 'temp table'
 create temp table any_table3 as 
 select 1 as any_col;
 ``` 

 ````
 ``````

 ``````{tabbed} generic-anchors
 :class-content: sn-light-shadow
 
 A mapping of sql keywords to generic anchor names can be configured in the 
 {ref}`generic-anchors<generic-anchors>` block within the {ref}`[sql] <sql.root>` 
 section of {ref}`snowmobile-ext.toml<file-contents-snowmobile-ext-toml>`,
 included below.
 ```{code-block} toml
 [sql.generic-anchors]
     "select" = "select data"
     "set" = "set param"
     "unset" = "unset param"
     "insert" = "insert into"
     "delete" = "delete from"
 ``` 
 
 ``````

 <hr class="sn-spacer-thick">
  
 % (delimiter ====================================================)
 (script-delimiter)=
 ##### ***delimiter***
 
 ``````{tabbed} -
 :class-content: sn-light-shadow
 
 {attr}`~snowmobile.core.cfg.script.Core.delimiter` is a literal constant specified
 in the `description-delimiter` field within the
 {ref}`[script.patterns.core]<script.patterns.core>` section
 of [](./snowmobile_toml.md), the value for which can be accessed directly off
 <a class="fixture-sn" href="../index.html#fixture-sn"></a> with: 
 
 ```{literalinclude} ../snippets/script/overview-statement-names.py
 :language: python
 :lines: 33-33
 ```
 
 ``````

 <hr class="sn-spacer-thick">
 
 % (desc =========================================================)
 (script-desc)=
 ##### ***desc***
  
 `````{tabbed} -
 :class-content: sn-light-shadow
 
 <hr class="sn-spacer">
 
 {attr}`~snowmobile.core.name.Name.desc` is a free-form text field loosely 
 intended to be short-hand *description* for the statement.
 
 <hr class="sn-grey-dotted sn-top-pad-hr">

 The **generated** description for a statement, 
 {attr}`~snowmobile.core.name.Name.desc_ge`, is a concatenation of a constant
 prefix and its index position within the script.
  
 The prefix used is configurable in the `description-index-prefix` field within 
 the {ref}`[script.patterns.core]<script.patterns.core>` 
 section of [](./snowmobile_toml.md), the value for which can be accessed
 directly off <a class="fixture-sn" href="../index.html#fixture-sn"></a>
 with:
 ```python
 print(sn.cfg.script.patterns.core.prefix)  #> s
 ```
 
 <hr class="sn-grey-dotted sn-top-pad-hr">
 
 The **provided** description for a statement, 
 {attr}`~snowmobile.core.name.Name.desc_pr`, is all text to the right
 of the first *character* found matching the {ref}`script-delimiter`
 within a statement's {attr}`~snowmobile.core.name.Name.nm_pr`.
 
 <hr class="sn-spacer-thick">
 
 `````

 `````{tabbed} using *desc-is-simple*
 :class-content: sn-light-shadow
 
 <hr class="sn-spacer">
 
 ```{admonition} Warning
 :class: warning, sn-inherit-overflow
 The functionality outlined below is experimental and not under test.
 ```

 Using parsed values for the {attr}`~snowmobile.core.name.Name.obj_ge`
 and {attr}`~snowmobile.core.name.Name.desc_ge`
 can be enabled by setting the {ref}`desc-is-simple<desc-is-simple>` field to 
 `true` in {ref}`snowmobile-ext.toml<file-contents-snowmobile-ext-toml>` or by
 modifying the attribute's value on an instance of 
 <a class="fixture-sn" href="../index.html#fixture-sn"></a>.

 In the case of [{fa}`fixture script`](script/statements/quick-intro), this looks
 like: 
 ```{literalinclude} ../snippets/script/overview-statement-names.py
 :language: python
 :lines: 64-68
 ```
 ````{div} sn-output2
 ```{literalinclude} ../snippets/script/overview-statement-names.py
 :language: python
 :lines: 71-79
 ```  
 ````
 
 <hr class="sn-spacer">
 
 `````
  
  </div>
 </div>  
</div>
</body>

+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

<hr class="sn-green-rounded-g">
<hr class="sn-spacer-thick">


(tags)=
### Tags
<hr class="sn-green-thick-g">

``````{div} sn-tabbed-section

 `````{tabbed} &nbsp;
 A tag contains an abitrary amount of information wrapped in a pre-defined opening/closing pattern.
 It can be associated with a {class}`~snowmobile.core.statement.Statement`, identified by its literal
 position relative to the statement's sql, or with a {class}`~snowmobile.core.cfg.script.Marker`,
 identified by its contents.

 The default pattern, highlighted in the below snippet from [snowmobile.toml](./snowmobile_toml.md),
 mirrors that of a standard sql block comment with an additional dash (`-`) on the inside of each component:
 ```{literalinclude} ../../snowmobile/core/pkg_data/snowmobile-template.toml
 :class: sn-dedent-v-b-container-neg
 :language: toml
 :lineno-start: 64
 :lines: 64-66
 :emphasize-lines: 2-3
 ```
 `````

```````

<hr class="sn-green-rounded-g">
<hr class="sn-spacer-thick">

### Markers
<hr class="sn-green-thick-g">

``````{div} sn-tabbed-section

 `````{tabbed} Overview
 ```{admonition} TODO
 :class: error
 Missing
 ```
 `````

 `````{tabbed} +-
 MORE CONTENT GOES HERE
 `````

```````

<hr class="sn-green-rounded-g">
<hr class="sn-spacer-thick">

### Markup
<hr class="sn-green-thick-g">

``````{div} sn-tabbed-section

 `````{tabbed} &nbsp;

 ```{div} sn-hanging-p
 Using markup within a script enables:
 ```
 - Defining accessors for individual statements
 - Adding descriptive information to individual statements or to the script itself
 - Finer-grained control of the script's execution
 - Generating documentation and cleansed sql files from the working version of a script

 ```{div} sn-dedent-v-b-h
 {xref}`snowmobile` introduces two sql-compliant forms of adding markup to a sql file:
 ```
 1. [Tags](#tags) enable constructing collections of attributes amidst sql statements, including
 those directly associated with a particular statement
 2. [Markers](#markers) are a collection of attributes that are **not** associated with a
 particular statement

 The following sections outline the different ways that [](#tags) and [](#markers) are
 implemented and utilized.

 `````

```````

+++
<hr class="sn-green-rounded-g">
<hr class="sn-spacer-thick">

##### Single-Line Tags
<hr class="sn-green-thin-g">

``````{div} sn-tabbed-section

 `````{tabbed} Overview
 Single-line tags are the simplest form of [markup](#markup) and can be used to succinctly
 denote a name for a given statement.

 When a single-line string directly precedes a statement and is wrapped in [a valid open/close pattern](#tags),
 it will be recognized as the *provided* name ({attr}`~snowmobile.core.name.Name.nm_pr`) and used as
 the statement's name ({attr}`~snowmobile.core.name.Name.nm`) as opposed to its *generated*
 name  ({attr}`~snowmobile.core.name.Name.nm_ge`).
 `````

`````{tabbed} +

 Consider the sql file, *tags_single-line.sql*, containing two statements, the first and second of which have valid and invalid
 single-line tags respectively:
 ````{div} sn-inline-flex-container
 ```{literalinclude} ../snippets/script/tags_single-line.sql
 :language: sql
 :lines: 1-8
 ```
 ````

 Given a `path` to *tags_single-line.sql* and [{fa}`fixture sn`](../index.ipynb#fixture-sn), the following `script` can be created:
 ```python
 # Instantiate a Script from sql file
 script = snowmobile.Script(path=path, sn=sn)

 # Store individual statements for inspection
 s1, s2 = script(1), script(2)

 print(s1)        #> Statement('I am a tag')
 print(s1.nm_ge)  #> select data~s1
 print(s1.nm_pr)  #> I am a tag
 print(s1.nm)     #> I am a tag

 print(s2)        #> Statement('select data~s2')
 print(s2.nm_ge)  #> select data~s2
 print(s2.nm_pr)  #> ''
 print(s2.nm)     #> select data~s2
 ```

 ````{div} sn-indent-h-cell
  ```{admonition} Note
  :class: note, toggle, toggle-shown, sn-dedent-v-b-h-container

  The first statement has a valid tag directly preceding it, so its  name
  ({attr}`~snowmobile.core.name.Name.nm`) is populated by the *provided* name within
  the tag ({attr}`~snowmobile.core.name.Name.nm_pr`) as opposed to the name that was
  *generated* for the statement ({attr}`~snowmobile.core.name.Name.nm_ge`).

  The second statement does **not** have a valid tag directly preceding it, so
  its generated name, `select data~s2`, is used and the line
  `/*-I am a tag that isn't positioned correctly-*/` is ignored.
  ```
 ````
`````

``````

<hr class="sn-green-rounded-g">
<hr class="sn-spacer-thick">

##### Multi-Line Tags
<hr class="sn-green-thin-g">

```````{div} sn-tabbed-section

`````{tabbed} Overview
```{div} sn-hanging-p
 Multi-line tags provide a method of associating multiple attributes with
 a {class}`~snowmobile.core.statement.Statement` according to the following syntax:
- Attribute **names** must:
   1. Start at the beginning of a new line
   1. Have leading double underscores (`__`)
   1. End with a single colon (`:`)
- Attribute **values** have no restrictions except for several reserved attributes documented
  in the *reserved attributes* (LINK NEEDED) section below
```
`````

``````{tabbed} +
 In practice, this looks something like the following:
 ```{literalinclude} ../snippets/script/tags_multi-line.sql
 :language: sql
 :lines: 1-13
 ```

 `````{div} sn-dedent-v-t-container
  ````{admonition} Tip
  :class: tip, toggle, toggle-shown

  Trailing wildcards can be appended to attribute **names** to denote how information
  will be rendered in generated documentation; this is covered in [Patterns - Wildcards](#wildcards) below.
  ````
 `````
``````

```````

<hr class="sn-green-rounded-g">
<hr class="sn-spacer-thick">

#### Patterns
<hr class="sn-green-thick-g">

``````{div} sn-tabbed-section

 `````{tabbed} &nbsp;
 ```{admonition} TODO
 :class: error
 Missing
 ```
 `````

 `````{tabbed} +-
 MORE CONTENT GOES HERE
 `````

```````

<hr class="sn-green-rounded-g">
<hr class="sn-spacer-thick">

##### Core
<hr class="sn-green-thin-g">

``````{div} sn-tabbed-section

 `````{tabbed} Overview
 ```{admonition} TODO
 :class: error
 Missing
 ```
 `````

 `````{tabbed} +-
 MORE CONTENT GOES HERE
 `````

```````

<hr class="sn-green-rounded-g">
<hr class="sn-spacer-thick">

##### Wildcards
<hr class="sn-green-thin-g">

``````{div} sn-tabbed-section

 `````{tabbed} Overview
 ```{admonition} TODO
 :class: error
 Missing
 ```
 `````

 `````{tabbed} +-
 MORE CONTENT GOES HERE
 `````

```````

<hr class="sn-green-rounded-g">
<hr class="sn-spacer-thick">


<style>
div.md-sidebar.md-sidebar--secondary :not(label.md-nav__title) {
    font-weight: 300;
}
div.sn-def p.sn-def-p + p {margin-bottom: 0.0rem;}

h5 + .tabbed-set.docutils {
    margin-top: -0.4rem;
    margin-left: -0.1em;
}

h3 ~ hr ~ div ~ button.toggle-button {
    position: sticky;
    margin-top: -1.3rem;
/*     margin-right: 0.2rem; */
    font-size: 85%;
    background-color: #656d720a;
    margin-right: 0.1rem;
}
h3 ~ hr ~ div ~ button.toggle-button:before {
    /*content: "hide section";*/
    /*background-color: #02080e;*/
    margin-left: -5rem;
    font-style: italic;
    color: #f0f8ff33;
    position: static;
    z-index: 2;
    display: initial;
}
h3 ~ hr ~ div ~ button.toggle-button-hidden:before {
    content: initial;
    padding-left: 1.8rem;
    color: aliceblue;
/*     display: none; */
}
h3 ~ hr ~ div ~ button.toggle-button .bar {
    background: #f0f8ff94;
}

@media only screen and (max-width: 500px) {
 div.sn-def p.sn-def-p + p {margin-bottom: 0.6rem;}

}


</style>

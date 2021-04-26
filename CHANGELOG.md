Changelog
=========

---

#### v0.1.13
- Addition of `snowprocess` - background module, no user-facing changes

---

#### v0.1.12
- Removing `from_file` argument from `snowquery.query`
- Added manual commits to `snowloader` between commands ensure DDL execution is realized by the warehouse 
  before data is attempted to load into table

---

#### v0.1.11
- `snowscripter`
    - Adding additional logic to strip comments from object such that script.run() only runs on executable sql

---

#### v0.1.10

---

#### v0.1.9
- Fixing issue with caching syncing up across classes

---

#### v0.1.8

---

#### v0.1.7

---

#### v0.1.6
- `snowscripter`
    - Addition of sql parsing logic for comment cleansing
- `snowcreds`
    - Additional caching logic

---

#### v0.1.5
- Docs addition only

---

#### v0.1.4
- Switching dynamic tags to include beta indicator

---

#### v0.1.3
- Quick patch of HTML tag causing explosion in the docs

---

#### v0.1.2
- `snowquery`
    - Change from `snowquery.Snowflake()` to `snowquery.Connector()` for semantic purposes / clarity of instantiation
- `snowscripter`
    - Addition of `snowscripter.Script` methods:
        - `.reload_source()`
        - `.get_statements()`
        - `.fetch()`
    - Addition of `snowscripter.Statement` methods
        - `.execute()` w/ keyword args `return_results`, `render`, and `describe`
        - `.render()`
        - `.raw()`

---

#### v0.1.1
- Simplifying `snowscripter.raw()`

---

#### v0.1.0
- Initial upload for Python 3.7 and 3.8

---


<style>
.md-typeset ul {
    list-style-type: circle;
    margin-bottom: -0.15rem;
}
.md-typeset hr {
    border-bottom: .1rem dotted #6a94bf73;
    margin-left: 0.2rem;
    padding-top: 0.3rem;
    padding-bottom: 0.5rem;
    margin-right: 0.2rem;
}
.md-typeset h2 {
    font-weight: 800;
    padding-left: 0.5rem;

}
li::marker {
    color: rgb(138, 255, 255);
}
</style>

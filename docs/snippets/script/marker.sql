

/*-
__intro.sql__
__authored-by: Some Chap or Lass
__authored-on: Some Day or Year
__\*impetus\***: **SQL is as old as time and isn't disappearing; a simple markup syntax might be alright?**
__description*_***: This is now a blank canvas of markdown..

---

## *Explanation*

**The string spanning lines 3-38 in *intro.sql* were identified by *snowmobile*
as a marker because:**
-   It begins and ends (lines 3/38) with the patterns specified in *snowmobile.toml*
	- see: `open-tag`, `close-tag`
-   Its second line contains only a string that is wrapped in double underscores (line 4)

**The rendered markdown for this marker is formatted as such for the following reasons:**
-   The marker title, `intro.sql`, is an h1 header based on a *snowmobile.toml* specification
	- see: `default-marker-header`
-   The first two attributes, `authored-by` and `authored-on`, are title-cased and bulleted by default;
    whether to bold/italicize the names/values is a *snowmobile.toml* specification
	- see: `wrap-attribute-names-with`, `wrap-attribute-values-with`
-   The third attribute, `impetus`, and its associated value have not been reformatted due to
    the *unescaped* trailing wildcard, `**`, placed at the end of its attribute name; additionally,
    literal characters matching the configured wildcard were escaped and ignored by *snowmobile*
	- see: `denotes-no-reformat`
-   The final attribute, `description`, is treated as free-form markdown (as opposed to a bullet)
    and the attribute name itself is omitted from the output, achieved by providing multiple unescaped
    wildcards delimited by a specified character
	- see: `wildcard-delimiter`, `denotes-paragraph`, `denotes-omit-name-in-output`

-*/


/*-ddl table~initial_table-*/
create initial_table (any_col int);

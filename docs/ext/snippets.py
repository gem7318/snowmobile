"""
This file populates snippets.md based on a source directory and the parameters
defined within this file directly below.

It is not under test and was written to serve a single purpose of generating
this reference page.
"""
from typing import List, Dict, Tuple
from pathlib import Path

# --/ Hard Codes /-------------------------------------------------------------

GENERIC_DIR_NAME = "General"  # header for snippets in base directory
FLAG = 'snowmobile-include'  # string that indicates the include the file

OFFSET_TOP = 0  # offset from top of files to start
OFFSET_BOTTOM = 2  # offset from bottom of files to start

TITLE_CASE_DIR_NAMES = True  # whether to title case directory names in headers

MAP_LANGUAGE = {  # maps file extensions to :language: directive
    '.bashrc': 'bash',
    '.bat': 'shell',
    '.html': 'html',
    '.ini': 'ini',
    '.json': 'json',
    '.py': 'python',
    '.rst': 'rst',
    '.sh': 'sh',
    '.sql': 'sql',
    '.toml': 'toml',
    '.R': 'R',
    '.xml': 'xml',
    '.yml': 'yaml'
}

# HERE = Path.cwd() / 'docs' / 'ext' / 'snippets.py'
HERE = Path(__file__).absolute()  # current file location
DOC_ROOT = HERE.parent.parent     # documentation root directory
SNIPPETS_DIR_NAME = 'snippets'    # directory containing code snippets

TARGET_FILE_NAME = "snippets.md"  # file name to save raw text in

DIV_WRAP = True  # wrap {literalinclude} directive in a div
DIV_CLASSES = ['sn-indent-h-cell']  # classes for div


# INCL_HR = True
INCL_HRS = ['###']
INCL_LINE_NUMBERS = True

ALT_HEADERS = {
    'h2': {'sql': 'SQL'}
}

GIT_ROOT = r'https://github.com/GEM7318/Snowmobile/tree/0.2.0/docs'
DIVS_DOWNLOAD = ['sn-download-snippet']
DIVS_GIT_LINK = ['sn-snippet-git-link']
DIVS_PARENT_CONTAINER = ['sn-link-group', 'sn-snippet-only']

INCL_DOWNLOAD = True
INCL_GIT_LINK = True
INCL_PARENT_CONTAINER = True  # must be True if either _DOWNLOAD or _GIT_LINK is True


# --/ Derived /----------------------------------------------------------------
offsets = (OFFSET_TOP, OFFSET_BOTTOM)
root = DOC_ROOT / 'snippets'
target_file_path = DOC_ROOT / TARGET_FILE_NAME


def line_nos(txt: str, offsets: Tuple[int, int]) -> Tuple[int, int]:
    """Determines lines to include based on the raw text and offsets.

    Args:
        txt:
            Raw file contents.
        offsets:
            Tuple containing (top-offset, bottom-offset)

    Returns:
        Tuple containing (start-line, end-line)

    """
    _start, _end = offsets
    depth = len(txt.split('\n'))
    start_line = 0 + _start if _start else 1
    end_line = depth - _end
    return start_line, end_line


def download(file_path: Path) -> str:
    """Generates 'download' container"""
    p_rel = list(file_path.relative_to(root).parts)
    p_rel.insert(0, root.name)
    p_download_v0 = '/'.join(p_rel)
    p_download = f"./{p_download_v0}"
    _div = "{div}"
    _download = "{download}"
    return f"""
```{_div} {', '.join(DIVS_DOWNLOAD)} 
{_download}`Download<{p_download}>`
```
""".strip('\n')


def git(file_path: Path, root_url: str = GIT_ROOT) -> str:
    """Generates 'git' container"""
    p_rel = list(file_path.relative_to(root).parts)
    p_rel.insert(0, root.name)
    url_git_v0 = '/'.join(p_rel)
    url_git = f"{root_url}/{url_git_v0}"
    _div = "{div}"
    return f"""
```{_div} {', '.join(DIVS_GIT_LINK)} 
<a class="reference external" href="{url_git}"><span>text</span></a>
```
""".strip('\n')


def link_container(file_path: Path, root_url: str = GIT_ROOT) -> str:
    """Generates link container."""
    div_download = ''
    div_git_url = ''
    _div = "{div}"
    if INCL_DOWNLOAD:
        div_download = download(file_path)
    if INCL_GIT_LINK:
        div_git_url = git(file_path, root_url=root_url)
    return f"""\n
````{_div} {', '.join(DIVS_PARENT_CONTAINER)}
{div_download}
{div_git_url}
````"""


def header(file_path: Path, root: Path):
    """Generates literal header text from a file path within a root path."""
    offset = list(file_path.relative_to(root).parts)[:-1]
    h_prefix = (2 + len(offset)) * '#'
    h_final = f"{h_prefix} *{file_path.name}*"
    return h_final if h_prefix not in INCL_HRS else f"{h_final}\n---"


def rst_literal_incl(
    file_path: Path,
    root: Path,
    offsets: Tuple[int, int],
    flag: str,
    suffix_map: Dict[str, str],
    first_of_dirs: Dict[str, Path],
    root_url: str = GIT_ROOT,
    title_dir_names: bool = TITLE_CASE_DIR_NAMES
) -> str:
    """DOCSTRING"""
    with open(file_path, 'r') as r:
        raw = r.read()

    parent_header = str()
    parent = file_path.parent.name

    if flag not in raw:
        return str()

    if parent in first_of_dirs:
        _ = first_of_dirs.pop(parent)
        alt_h2 = ALT_HEADERS.get('h2')
        parent = alt_h2.get(
            parent.lower(),
            parent.title() if title_dir_names else parent
        )
        parent_header = f"<br>\n\n## {parent}"
    child_header = header(file_path, root)
    header_final = (
        f"{parent_header}\n\n{child_header}" if parent_header
        else child_header
    )

    path_sub = '/'.join(file_path.relative_to(root).parts)
    path_final = f"/{root.name}/{path_sub}"

    start_line, end_line = line_nos(raw, offsets)
    language = suffix_map[file_path.suffix]
    incl = "{literalinclude}"
    lines = '' if not INCL_LINE_NUMBERS else "\n:lineno-start: 1"

    literal_include = (
        f"""
```{incl} {path_final}
:language: {language}
:lines: {start_line}-{end_line}{lines}
```
"""
    )

    if DIV_WRAP:
        _div = "{div}"
        _classes = ', '.join(DIV_CLASSES)
        div = f"{_div} {_classes}"
        literal_include = f"````{div}{literal_include}````"

    _links = ''
    if INCL_PARENT_CONTAINER:
        _links = link_container(file_path, root_url=root_url)

    return (
        f"""
{header_final}{_links}
{literal_include}
<br>
"""
    )


def get_first_of_dir(files_sorted: Dict[str, Path]):
    """DOCSTRING"""
    first_of_dir = {}
    for f in files_sorted.values():
        if f.parent.name not in first_of_dir.values():
            first_of_dir[f.parent.name] = f
    return first_of_dir


def snippets_total(
    files: List[Path],
    root: Path,
    offsets: Tuple[int, int],
    flag: str,
    suffix_map: Dict[str, str],
    first_of_dirs: Dict[str, Path],
    root_url: str = GIT_ROOT,
):
    """docstring"""
    print("----/ Starting Snippets /----")
    total_rst = []
    for f in files:
        rst = rst_literal_incl(
            file_path=f,
            root=root,
            offsets=offsets,
            flag=flag,
            suffix_map=suffix_map,
            first_of_dirs=first_of_dirs,
            root_url=root_url
        )
        if rst:
            total_rst.append(rst)
            print(f"\tsnippet: {f.name}")
    return total_rst


def write(root_url: str = GIT_ROOT):
    """docstring"""
    files = {
        f.as_posix(): f
        for f in root.rglob('**/*.*')
        if f.is_file() and f.suffix in MAP_LANGUAGE
    }

    files_sorted = {files[k].name: files[k] for k in sorted(files)}
    first_of_dirs = get_first_of_dir(files_sorted)

    total = snippets_total(
        files=list(files_sorted.values()),
        root=root,
        offsets=offsets,
        flag=FLAG,
        suffix_map=MAP_LANGUAGE,
        first_of_dirs=first_of_dirs,
        root_url=root_url,
    )

    with open(target_file_path, 'r') as r:
        current = r.read()

    page_heading, _ = current.split("+++")
    to_write = f"{page_heading}+++{''.join(total)}"

    # to_write = f"{PAGE_HEADER}{''.join(total)}"
    # if ADD_STYLE:
    #     to_write = f"{to_write}\n\n{PAGE_STYLE}"

    with open(target_file_path, 'w') as f:
        f.write(to_write)

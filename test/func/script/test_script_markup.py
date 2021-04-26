"""
This file stores setup and tests for snowmobile.Markup.

See `context.md` within `/tests/func/data/sql` for more information on the
directory structure/approach to this part of the testing.
"""
import pytest

from typing import Dict

from test import script as get_script, contents_are_identical, get_validation_file

import snowmobile


# noinspection PyProtectedMember
def export_markup_combinations_from_script(
    script: snowmobile.Script, run: bool, run_args: Dict = None
):
    """Exports different versions of a `Script` object given sets of args.

    Args:
        script (Script):
            Script object under test.
        run (bool):
            Indicates whether or not to run the script before exporting.
        run_args (dict):
            Arguments to pass to `script.run()` if `run=True`

    Returns (List[Path]):
        A list of the paths that were exported which is used within the body
        of the test method to fetch the validation file and assert their equality.

    export_args (explanation)
        *   config:
                Arguments to pass to markup.config() or to the markup object as
                a callable; i.e. markup()(**args) as opposed to
                markup.config(**args)
        *   save:
                Arguments to pass to markup.save() to modify the contents
                that are exported and the target file name.

    """

    export_args = [
        {"config": {"prefix": "(default) "}, "save": {}},
        {"config": {"prefix": "(no sql) "}, "save": {"sql": False}},
        {
            "config": {"incl_markers": False, "prefix": "(no markers) "},
            "save": {},
        },
        {
            "config": {
                "incl_markers": False,
                "incl_exp_ctx": False,
                "prefix": "(no disclaimer, no markers) ",
            },
            "save": {"md": False},
        },
    ]

    if run:
        # excluding execution time from unit test as this can vary run to run
        script.sn.cfg.attrs.exclude("execution_time_txt")
        script.run(**run_args or dict())
    file_paths = []
    for arg in export_args:
        markup = script.doc()(**arg["config"])
        markup.save(**arg["save"])
        for p in markup.exported:
            file_paths.append(p)
    return file_paths


@pytest.mark.markup
def test_markup_with_results(sn):
    """Unit test for markup save including as_df."""
    script = get_script("markup_with_results.sql")

    exported_paths_for_current_test = export_markup_combinations_from_script(
        script=script, run=True, run_args={"on_failure": "c", "on_exception": "c"}
    )
    paths_under_test_mapped_to_validation_paths = {
        p: get_validation_file(path1=p) for p in exported_paths_for_current_test
    }

    for (
        p_under_test,
        p_validation,
    ) in paths_under_test_mapped_to_validation_paths.items():
        assert contents_are_identical(path1=p_under_test, path2=p_validation)


@pytest.mark.markup
def test_markup_no_results(sn):
    """Unit test for markup save including as_df."""
    script = get_script("markup_no_results.sql")

    exported_paths_for_current_test = export_markup_combinations_from_script(
        script=script, run=False, run_args={}
    )
    paths_under_test_mapped_to_validation_paths = {
        p: get_validation_file(path1=p) for p in exported_paths_for_current_test
    }

    for (
        p_under_test,
        p_validation,
    ) in paths_under_test_mapped_to_validation_paths.items():
        assert contents_are_identical(path1=p_under_test, path2=p_validation)


@pytest.mark.markup
def test_markup_using_template_anchor_attributes(sn):
    """Unit test for markup save using an __anchor__ that is included in
    the `script.markdown.attributes.markers` section of ``snowmobile.toml``.."""
    script = get_script("markup_template_anchor.sql")

    exported_paths_for_current_test = export_markup_combinations_from_script(
        script=script, run=False, run_args={}
    )
    paths_under_test_mapped_to_validation_paths = {
        p: get_validation_file(path1=p) for p in exported_paths_for_current_test
    }

    for (
        p_under_test,
        p_validation,
    ) in paths_under_test_mapped_to_validation_paths.items():
        assert contents_are_identical(path1=p_under_test, path2=p_validation)


@pytest.mark.markup
def test_markup_scaffolding(sn, tmpdir):
    """Verifies calling markup.save() without a pre-existing directory."""
    from pathlib import Path

    # given
    script = get_script("markup_template_anchor.sql")

    # when
    script.path = Path(tmpdir) / script.path.name
    markup = script.doc()
    markup.save()

    # then
    assert not script.path.exists()  # script path is set but never written to
    assert Path(markup._path_md).exists()  # doc paths take directory of script path
    assert Path(markup._path_sql).exists()


@pytest.mark.markup
def test_markup_dunder_methods(sn):
    """Verifies __str__ and __repr__ do not cause errors."""
    script = get_script("markup_template_anchor.sql")
    markup = script.doc()
    assert str(markup)
    assert repr(markup)

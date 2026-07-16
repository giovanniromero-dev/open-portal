from open_portal import detect


def test_is_project_dir_true_for_git(tmp_path):
    (tmp_path / ".git").mkdir()
    assert detect.is_project_dir(tmp_path) is True


def test_is_project_dir_false_for_plain_folder(tmp_path):
    assert detect.is_project_dir(tmp_path) is False


def test_detect_language_prefers_typescript_over_javascript(tmp_path):
    (tmp_path / "package.json").write_text("{}")
    (tmp_path / "tsconfig.json").write_text("{}")
    assert detect.detect_language(tmp_path) == "TypeScript"


def test_detect_language_javascript(tmp_path):
    (tmp_path / "package.json").write_text("{}")
    assert detect.detect_language(tmp_path) == "JavaScript"


def test_detect_language_python(tmp_path):
    (tmp_path / "pyproject.toml").write_text("")
    assert detect.detect_language(tmp_path) == "Python"


def test_detect_language_none_when_no_markers(tmp_path):
    assert detect.detect_language(tmp_path) is None


def test_detect_git_branch_none_without_git_dir(tmp_path):
    assert detect.detect_git_branch(tmp_path) is None


def test_find_projects_discovers_nested_marker(tmp_path):
    nested = tmp_path / "group" / "my-repo"
    nested.mkdir(parents=True)
    (nested / "package.json").write_text("{}")
    (tmp_path / "not-a-project" / "empty").mkdir(parents=True)

    found = detect.find_projects(tmp_path)
    assert nested in found


def test_find_projects_does_not_descend_into_found_project(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".git").mkdir()
    (repo / "nested-not-counted").mkdir()
    (repo / "nested-not-counted" / "package.json").write_text("{}")

    found = detect.find_projects(tmp_path)
    assert found == [repo]

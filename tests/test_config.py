import pytest

from open_portal import config as cfg


@pytest.fixture(autouse=True)
def isolated_config(tmp_path, monkeypatch):
    config_dir = tmp_path / ".open-portal"
    monkeypatch.setattr(cfg, "CONFIG_DIR", config_dir)
    monkeypatch.setattr(cfg, "CONFIG_FILE", config_dir / "config.json")


def make_project(name="demo", favorite=False, last_opened=None):
    return cfg.Project(name=name, path=f"/tmp/{name}", favorite=favorite, last_opened=last_opened)


def test_load_returns_empty_config_when_no_file():
    config = cfg.load()
    assert config.projects == []
    assert config.default_editor == "code"


def test_add_and_find():
    config = cfg.Config()
    cfg.add(config, make_project("demo"))
    found = cfg.find(config, "demo")
    assert found is not None
    assert found.name == "demo"
    assert cfg.find(config, "missing") is None


def test_add_replaces_existing_by_name():
    config = cfg.Config()
    cfg.add(config, make_project("demo", favorite=False))
    cfg.add(config, make_project("demo", favorite=True))
    assert len(config.projects) == 1
    assert cfg.find(config, "demo").favorite is True


def test_remove():
    config = cfg.Config()
    cfg.add(config, make_project("demo"))
    assert cfg.remove(config, "demo") is True
    assert cfg.find(config, "demo") is None
    assert cfg.remove(config, "demo") is False


def test_toggle_favorite():
    config = cfg.Config()
    cfg.add(config, make_project("demo", favorite=False))
    project = cfg.toggle_favorite(config, "demo")
    assert project.favorite is True
    project = cfg.toggle_favorite(config, "demo")
    assert project.favorite is False
    assert cfg.toggle_favorite(config, "missing") is None


def test_search_is_case_insensitive_substring():
    config = cfg.Config()
    cfg.add(config, make_project("DockPortal"))
    cfg.add(config, make_project("other"))
    results = cfg.search(config, "dock")
    assert [p.name for p in results] == ["DockPortal"]


def test_sorted_projects_favorites_first_then_alphabetical():
    config = cfg.Config()
    cfg.add(config, make_project("zeta", favorite=False))
    cfg.add(config, make_project("alpha", favorite=True))
    cfg.add(config, make_project("beta", favorite=False))
    ordered = [p.name for p in cfg.sorted_projects(config)]
    assert ordered == ["alpha", "beta", "zeta"]


def test_recent_orders_by_last_opened_desc_and_limits():
    config = cfg.Config()
    cfg.add(config, make_project("old", last_opened="2024-01-01T00:00:00+00:00"))
    cfg.add(config, make_project("new", last_opened="2025-01-01T00:00:00+00:00"))
    cfg.add(config, make_project("never", last_opened=None))
    ordered = cfg.recent(config, limit=1)
    assert [p.name for p in ordered] == ["new"]


def test_save_and_load_roundtrip():
    config = cfg.Config(default_editor="cursor")
    cfg.add(config, make_project("demo", favorite=True))
    cfg.save(config)

    reloaded = cfg.load()
    assert reloaded.default_editor == "cursor"
    assert len(reloaded.projects) == 1
    assert reloaded.projects[0].name == "demo"
    assert reloaded.projects[0].favorite is True

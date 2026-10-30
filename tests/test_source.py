import json

import pytest

from stackgraph.source import GitHubCache


class Response:
    status_code = 200
    headers = {"Date": "Thu, 01 Jan 2026 12:00:00 GMT", "ETag": "fixture"}
    links = {}

    def json(self):
        return {"number": 1, "title": "synthetic cache fixture"}


def test_cache_records_provenance_and_replays_without_network(tmp_path, monkeypatch):
    client = GitHubCache(tmp_path)
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: Response())
    saved = client.get("/repos/lab/project/pulls/1")
    assert saved["source_url"] == "https://api.github.com/repos/lab/project/pulls/1"
    assert saved["retrieved_at"].endswith("+00:00")
    assert len(saved["data_sha256"]) == 64
    replay = GitHubCache(tmp_path, offline=True)
    def forbidden(*args, **kwargs):
        pytest.fail("Offline replay attempted network access")
    monkeypatch.setattr(replay.session, "get", forbidden)
    assert replay.get("/repos/lab/project/pulls/1") == saved
    assert replay.network_requests == 0
    assert replay.cache_hits == 1


def test_cache_detects_modified_source_json(tmp_path, monkeypatch):
    client = GitHubCache(tmp_path)
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: Response())
    client.get("/repos/lab/project/pulls/1")
    path = next(tmp_path.glob("*.json"))
    content = json.loads(path.read_text(encoding="utf-8"))
    content["data"]["number"] = 999
    path.write_text(json.dumps(content), encoding="utf-8")
    with pytest.raises(ValueError, match="integrity"):
        GitHubCache(tmp_path, offline=True).get("/repos/lab/project/pulls/1")


def test_offline_cache_miss_fails_clearly(tmp_path):
    with pytest.raises(FileNotFoundError, match="Offline cache miss"):
        GitHubCache(tmp_path, offline=True).get("/repos/lab/project/pulls/1")


def test_failed_stack_endpoint_is_cached_as_error_not_empty_membership(tmp_path, monkeypatch):
    response = Response()
    response.status_code = 404
    monkeypatch.setattr(response, "json", lambda: {"message": "Not Found"})
    client = GitHubCache(tmp_path)
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: response)
    saved = client.get("/repos/lab/project/stacks?pull_request=1")
    assert saved["http_status"] == 404
    assert saved["data"] == {"message": "Not Found"}


def test_refresh_archives_the_previous_dated_snapshot(tmp_path, monkeypatch):
    client = GitHubCache(tmp_path)
    monkeypatch.setattr(client.session, "get", lambda *args, **kwargs: Response())
    old = client.get("/repos/lab/project/pulls/1")
    refreshed = GitHubCache(tmp_path, refresh=True)
    monkeypatch.setattr(refreshed.session, "get", lambda *args, **kwargs: Response())
    refreshed.get("/repos/lab/project/pulls/1")
    assert len(list(tmp_path.glob("*.json"))) == 2
    assert any(json.loads(p.read_text(encoding="utf-8")) == old
               for p in tmp_path.glob("*.json"))

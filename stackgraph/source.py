"""Read-only GitHub acquisition with dated, integrity-checked JSON snapshots."""

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def digest(data):
    canonical = json.dumps(data, sort_keys=True, ensure_ascii=True).encode()
    return hashlib.sha256(canonical).hexdigest()


class GitHubCache:
    def __init__(self, directory, offline=False, refresh=False):
        if offline and refresh:
            raise ValueError("offline and refresh are mutually exclusive")
        self.directory = Path(directory)
        self.offline = offline
        self.refresh = refresh
        self.session = requests.Session()
        self.session.headers.update({
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2026-03-10",
            "User-Agent": "StackGraph-research-prototype",
        })
        token = os.environ.get("GITHUB_TOKEN")
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"
        retry = Retry(total=2, backoff_factor=0.5, status_forcelist=[502, 503, 504])
        self.session.mount("https://", HTTPAdapter(max_retries=retry))
        self.sources = []
        self.network_requests = 0
        self.cache_hits = 0

    def get(self, api_path):
        url = "https://api.github.com" + api_path
        key = hashlib.sha256(url.encode()).hexdigest()[:20]
        path = self.directory / f"{key}.json"
        if path.exists() and not self.refresh:
            self.cache_hits += 1
            snapshot = json.loads(path.read_text(encoding="utf-8"))
            if snapshot["source_url"] != url or digest(snapshot["data"]) != snapshot["data_sha256"]:
                raise ValueError(f"Cache integrity check failed: {path}")
        else:
            if self.offline:
                raise FileNotFoundError(f"Offline cache miss: {url}")
            response = self.session.get(url, timeout=(10, 45))
            self.network_requests += 1
            # Store API errors as evidence too; never equate a 404 with no stack.
            data = response.json()
            snapshot = {
                "source_url": url,
                "retrieved_at": datetime.now(timezone.utc).isoformat(),
                "http_status": response.status_code,
                "response_date": response.headers.get("Date"),
                "api_version": self.session.headers["X-GitHub-Api-Version"],
                "etag": response.headers.get("ETag"),
                "next_page": response.links.get("next", {}).get("url"),
                "data_sha256": digest(data),
                "data": data,
            }
            self.directory.mkdir(parents=True, exist_ok=True)
            # Refresh preserves all earlier snapshots instead of overwriting them.
            if path.exists():
                previous = json.loads(path.read_text(encoding="utf-8"))
                stamp = previous["retrieved_at"].replace(":", "-")
                path.rename(self.directory / f"{key}.{stamp}.json")
            path.write_text(json.dumps(snapshot, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
        self.sources.append({k: snapshot[k] for k in (
            "source_url", "retrieved_at", "http_status", "data_sha256"
        )})
        return snapshot

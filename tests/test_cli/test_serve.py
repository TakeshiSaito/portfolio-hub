import socket
import subprocess
import sys
import time
from pathlib import Path

import httpx2
import pytest

from portfolio_hub import applications


def test_serve(monkeypatch: pytest.MonkeyPatch):
    project = applications.create_project("sample_project")
    with socket.socket() as probe:
        probe.bind(("127.0.0.1", 0))
        port = probe.getsockname()[1]
    monkeypatch.setenv("PORTFOLIO_HUB_PORT", str(port))

    server = subprocess.Popen([Path(sys.executable).with_name("phub"), "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        response = None
        for _ in range(100):
            try:
                response = httpx2.get(f"http://127.0.0.1:{port}/api/projects")
                break
            except httpx2.TransportError:
                time.sleep(0.1)
    finally:
        server.terminate()
        server.wait(timeout=10)

    assert response is not None
    assert response.status_code == 200
    assert response.json() == [{"id": str(project.id), "name": "sample_project"}]

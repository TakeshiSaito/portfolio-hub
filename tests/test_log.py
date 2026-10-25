import logging

import pytest

from portfolio_hub import applications
from portfolio_hub.applications import dto


def test_launch_writes_a_log(project: dto.Project, caplog: pytest.LogCaptureFixture):
    environment = applications.create_environment(project.id, "anim", [("greeter", "2.0.0")], tools=["greet"])
    caplog.set_level(logging.INFO, logger="portfolio_hub")
    caplog.clear()

    result = applications.launch(environment.id, "greet")

    assert caplog.messages == [f"launched greet in environment anim ({environment.id}) with pid {result.pid}"]

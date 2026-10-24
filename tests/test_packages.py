from portfolio_hub import applications
from portfolio_hub.applications import dto


def test_list_packages():
    assert set(applications.list_packages()) == {
        dto.Package(name="greeter", version="1.0.0"),
        dto.Package(name="greeter", version="2.0.0"),
        dto.Package(name="greeter_plugin", version="1.0.0"),
        dto.Package(name="hello", version="1.0.0"),
    }

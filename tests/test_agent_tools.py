"""Test the research tools without invoking the model."""
from wofo.agent import dispatch_tool, TOOLS


def test_tools_registry_shape():
    names = {t["name"] for t in TOOLS}
    assert names == {"list_local_filings", "summarize_panel", "top_holdings", "qoq_activity"}
    for t in TOOLS:
        assert "input_schema" in t and t["input_schema"]["type"] == "object"


def test_list_local_filings_returns_periods():
    r = dispatch_tool("list_local_filings", {})
    assert r.ok and "periods" in r.content
    assert len(r.content["periods"]) >= 5


def test_summarize_panel():
    r = dispatch_tool("summarize_panel", {})
    assert r.ok
    assert r.content["manager"] == "Situational Awareness LP"
    assert r.content["cik"] == "0002045724"
    assert len(r.content["periods"]) >= 5


def test_top_holdings_known_period():
    r = dispatch_tool("top_holdings", {"period": "2025-12-31", "n": 3})
    assert r.ok
    issuers = [h["issuer"] for h in r.content["holdings"]]
    assert "COREWEAVE INC" in issuers
    assert len(r.content["holdings"]) == 3


def test_unknown_period_errors_cleanly():
    r = dispatch_tool("top_holdings", {"period": "1999-12-31"})
    assert not r.ok and "unknown period" in r.error


def test_unknown_tool_errors_cleanly():
    r = dispatch_tool("place_trade", {})
    assert not r.ok and "unknown tool" in r.error

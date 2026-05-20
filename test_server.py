"""Quick test script for the SCUEC Campus News MCP server.

Run with: python test_server.py
Requires the server to be running: python server.py --sse
"""

import json
import httpx

BASE = "http://localhost:8001"


def test(endpoint: str, params: dict = None):
    print(f"\n{'='*60}")
    print(f"Testing: {endpoint}")
    print(f"Params: {params}")
    try:
        # SSE endpoint health check
        resp = httpx.get(f"{BASE}/sse", timeout=5)
        print(f"SSE endpoint: HTTP {resp.status_code}")
    except Exception as e:
        print(f"SSE endpoint unavailable: {e}")
        return


if __name__ == "__main__":
    print("Testing SCUEC Campus News MCP...")
    print("Note: Full MCP testing requires MCP Inspector or MaxKB.")
    print("Run: mcp dev server.py")
    print()

    # Check SSE health
    try:
        resp = httpx.get(f"{BASE}/sse", timeout=5)
        print(f"SSE endpoint: HTTP {resp.status_code}")
    except Exception as e:
        print(f"SSE endpoint check: {e}")
        print("Make sure the server is running: python server.py --sse")

    print()
    print("To test individual tools, use MCP Inspector:")
    print("  pip install mcp[cli]")
    print("  mcp dev server.py")

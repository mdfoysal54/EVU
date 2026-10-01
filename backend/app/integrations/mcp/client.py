from __future__ import annotations

import json
import os
import subprocess
import threading
import urllib.error
import urllib.request
from itertools import count
from typing import Any

from .schemas import MCPResponse, MCPServerConfig, MCPTool


class MCPClient:
    """Small MCP JSON-RPC client supporting HTTP and stdio transports."""

    def __init__(self, config: MCPServerConfig) -> None:
        self.config = config
        self._ids = count(1)
        self._process: subprocess.Popen[str] | None = None
        self._lock = threading.RLock()

    def _http_call(self, method: str, params: dict[str, Any] | None) -> MCPResponse:
        request_id = next(self._ids)
        payload = json.dumps({
            "jsonrpc": "2.0", "id": request_id,
            "method": method, "params": params or {},
        }).encode("utf-8")
        request = urllib.request.Request(
            self.config.url or "", data=payload,
            headers={"Content-Type": "application/json", **self.config.headers},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=self.config.timeout) as response:
                data = json.loads(response.read().decode("utf-8"))
        except urllib.error.URLError as exc:
            raise ConnectionError(f"MCP HTTP request failed: {exc}") from exc
        return MCPResponse(data.get("result"), data.get("error"), data.get("id"))

    def _ensure_process(self) -> subprocess.Popen[str]:
        if self._process and self._process.poll() is None:
            return self._process
        if not self.config.command:
            raise ValueError("MCP stdio transport requires command")
        env = os.environ.copy()
        env.update(self.config.env)
        self._process = subprocess.Popen(
            [self.config.command, *self.config.args],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, env=env,
            bufsize=1,
        )
        return self._process

    def _stdio_call(self, method: str, params: dict[str, Any] | None) -> MCPResponse:
        process = self._ensure_process()
        request_id = next(self._ids)
        message = json.dumps({
            "jsonrpc": "2.0", "id": request_id,
            "method": method, "params": params or {},
        })
        with self._lock:
            if process.stdin is None or process.stdout is None:
                raise RuntimeError("MCP process streams unavailable")
            process.stdin.write(message + "\n")
            process.stdin.flush()
            line = process.stdout.readline()
        if not line:
            raise ConnectionError("MCP server closed stdout")
        data = json.loads(line)
        return MCPResponse(data.get("result"), data.get("error"), data.get("id"))

    def call(self, method: str, params: dict[str, Any] | None = None) -> MCPResponse:
        if not self.config.enabled:
            raise RuntimeError(f"MCP server {self.config.name!r} is disabled")
        if self.config.url:
            return self._http_call(method, params)
        return self._stdio_call(method, params)

    def initialize(self) -> dict[str, Any]:
        response = self.call("initialize", {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "evu", "version": "1.0"},
        })
        return response.raise_for_error()

    def list_tools(self) -> list[MCPTool]:
        result = self.call("tools/list").raise_for_error() or {}
        return [MCPTool(
            name=item["name"],
            description=item.get("description", ""),
            input_schema=item.get("inputSchema", {}),
            server=self.config.name,
        ) for item in result.get("tools", [])]

    def call_tool(self, name: str, arguments: dict[str, Any] | None = None) -> Any:
        return self.call("tools/call", {
            "name": name,
            "arguments": arguments or {},
        }).raise_for_error()

    def close(self) -> None:
        with self._lock:
            if self._process and self._process.poll() is None:
                self._process.terminate()
                try:
                    self._process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    self._process.kill()
            self._process = None

    def __enter__(self) -> "MCPClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

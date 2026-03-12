# SPDX-License-Identifier: EUPL-1.2
"""Entrypoint voor `python -m mcp_server`."""

from .server import mcp

mcp.run()

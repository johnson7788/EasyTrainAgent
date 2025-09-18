#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/9/17 16:30
# @File  : mcp_config_load.py
# @Author: johnson
# @Contact : github: johnson7788
# @Desc  : 读取mcp的配置文件

import json

def load_mcp_servers(config_path: str):
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)

    servers_config = config.get("mcpServers", {})
    servers = {}
    for name, entry in servers_config.items():
        if entry.get("disabled", False):
            continue
        if entry.get("transport") == "stdio":
            servers[name] = {
                "command": entry["command"],
                "args": entry.get("args", []),
                "env": entry.get("env", {}),
                "transport": "stdio",
            }
        else:
            servers[name] = {
                "url": entry["url"],
                "transport": entry["transport"],
            }
    return servers

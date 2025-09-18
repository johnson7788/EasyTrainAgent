#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date  : 2025/09/18
# @File  : test_api.py
# @Author: johnson
# @Contact: github: johnson7788
# @Desc  : 测试用例

import os
import time
import json
import base64
import unittest
from httpx import AsyncClient

class TrainingControllerApiTestCase(unittest.IsolatedAsyncioTestCase):
    """
    简易测试：训练控制后端接口（需先启动服务）
    默认地址：http://127.0.0.1:8600
    可通过环境变量覆盖：
        host=http://127.0.0.1   port=8600
    """
    host = os.environ.get("host", "http://127.0.0.1")
    port = os.environ.get("port", 8600)
    base_url = f"{host}:{port}"

    # --------- 小工具 ---------
    @staticmethod
    def _uid(prefix: str) -> str:
        return f"{prefix}-{int(time.time()*1000)}"

    @staticmethod
    def _b64_to_text(s: str) -> str:
        try:
            return base64.b64decode(s).decode("utf-8", errors="replace")
        except Exception:
            return ""

    # --------- 根路由与 /ping ---------
    async def test_root(self):
        url = f"{self.base_url}/"
        async with AsyncClient() as client:
            r = await client.get(url, timeout=20)
        self.assertEqual(r.status_code, 200, "GET / 应返回 200")
        data = r.json()
        self.assertIn("name", data)
        self.assertIn("endpoints", data)
        print("[root] name:", data.get("name"))

    async def test_ping(self):
        url = f"{self.base_url}/ping"
        async with AsyncClient() as client:
            r = await client.get(url, timeout=10)
        self.assertEqual(r.status_code, 200, "GET /ping 应返回 200")
        self.assertIn("Pong", r.text)
        print("[ping] text:", r.text)

    # --------- 项目：初始化 / 读取 / 列表 / 保存 ---------
    async def test_projects_init(self):
        url = f"{self.base_url}/api/projects/init"
        pid = self._uid("proj-init")
        req = {
            "project_id": pid,
            "name": "训练任务-初始化",
            "model": "gpt-4o",
            "mcp_tools": ["toolA", "toolB"],
            "extra": {"seed": 42}
        }
        async with AsyncClient() as client:
            r = await client.post(url, json=req, timeout=30)
        self.assertEqual(r.status_code, 200, "/api/projects/init 应返回 200")
        data = r.json()
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("config", {}).get("project_id"), pid)
        print("[projects/init] project_id:", pid)

    async def test_projects_get_config(self):
        # 先确保存在
        pid = self._uid("proj-get")
        init_url = f"{self.base_url}/api/projects/init"
        get_url = f"{self.base_url}/api/projects/{pid}/config"
        async with AsyncClient() as client:
            await client.post(init_url, json={"project_id": pid, "name": "get-config"}, timeout=30)
            r = await client.get(get_url, timeout=20)
        self.assertEqual(r.status_code, 200, "GET config 应返回 200")
        data = r.json()
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("project_id"), pid)
        self.assertIn("config", data)
        print("[projects/get_config] name:", data["config"].get("name"))

    async def test_projects_list(self):
        # 先插入一个项目以保证列表非空且可验证
        pid = self._uid("proj-list")
        init_url = f"{self.base_url}/api/projects/init"
        list_url = f"{self.base_url}/api/projects"
        async with AsyncClient() as client:
            await client.post(init_url, json={"project_id": pid, "name": "list-me"}, timeout=30)
            r = await client.get(list_url, timeout=20)
        self.assertEqual(r.status_code, 200, "GET /api/projects 应返回 200")
        data = r.json()
        self.assertTrue(data.get("ok"))
        projects = data.get("projects", [])
        self.assertIsInstance(projects, list)
        hit = [p for p in projects if p.get("project_id") == pid]
        self.assertTrue(len(hit) >= 1, "列表中应包含刚创建的项目")
        print(f"[projects/list] count={len(projects)}, found={pid}")

    async def test_projects_save_config(self):
        pid = self._uid("proj-save")
        init_url = f"{self.base_url}/api/projects/init"
        put_url = f"{self.base_url}/api/projects/{pid}/config"
        cfg = {
            "project_id": pid,
            "name": "save-config",
            "model": "gpt-4o",
            "mcp_tools": ["toolX"],
            "extra": {"lr": 1e-4, "epochs": 3}
        }
        async with AsyncClient() as client:
            await client.post(init_url, json={"project_id": pid}, timeout=30)
            r = await client.put(put_url, json={"project_id": pid, "config": cfg}, timeout=30)
        self.assertEqual(r.status_code, 200, "PUT config 应返回 200")
        data = r.json()
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("config", {}).get("extra", {}).get("epochs"), 3)
        print("[projects/save_config] saved extra:", data["config"].get("extra"))

    # --------- 文件：写 / 读 / 改 ---------
    async def test_fs_write(self):
        url = f"{self.base_url}/api/fs/write"
        path = f"workspace/tests/{self._uid('write')}.txt"
        req = {"path": path, "content": "hello\nworld\n", "append": False}
        async with AsyncClient() as client:
            r = await client.post(url, json=req, timeout=30)
        self.assertEqual(r.status_code, 200, "/api/fs/write 应返回 200")
        data = r.json()
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("path"), f"workspace/tests/{os.path.basename(path)}" if "/" in path else path)
        print("[fs/write] size:", data.get("size"))

    async def test_fs_read(self):
        # 先写再读
        w_url = f"{self.base_url}/api/fs/write"
        r_url = f"{self.base_url}/api/fs/read"
        path = f"workspace/tests/{self._uid('read')}.txt"
        content = "readable content 😀\n"
        async with AsyncClient() as client:
            await client.post(w_url, json={"path": path, "content": content}, timeout=30)
            r = await client.post(r_url, json={"path": path, "binary": False, "max_bytes": 1024 * 1024}, timeout=30)
        self.assertEqual(r.status_code, 200, "/api/fs/read 应返回 200")
        data = r.json()
        self.assertTrue(data.get("ok"))
        self.assertEqual(data.get("content"), content)
        print("[fs/read] sha256:", data.get("sha256"))

    async def test_fs_modify(self):
        # 用正则把 lr: xxx 替换为 0.0001
        w_url = f"{self.base_url}/api/fs/write"
        m_url = f"{self.base_url}/api/fs/modify"
        r_url = f"{self.base_url}/api/fs/read"
        path = f"workspace/tests/{self._uid('modify')}.yaml"
        init_text = "lr: 0.1\nmomentum: 0.9\n"
        async with AsyncClient() as client:
            await client.post(w_url, json={"path": path, "content": init_text}, timeout=30)
            m_req = {
                "path": path,
                "op": "regex_replace",
                "find": r"lr:\s*[\d\.eE+-]+",
                "replacement": "lr: 0.0001",
                "occurrence": 0
            }
            m_resp = await client.post(m_url, json=m_req, timeout=30)
            self.assertEqual(m_resp.status_code, 200, "/api/fs/modify 应返回 200")
            r = await client.post(r_url, json={"path": path}, timeout=30)
        data = r.json()
        self.assertIn("lr: 0.0001", data.get("content", ""))
        print("[fs/modify] content:", data["content"].strip().replace("\n", " | "))

    # --------- 运行：Python / 命令行 ---------
    async def test_run_python_inline(self):
        url = f"{self.base_url}/api/run/python"
        req = {
            "code": "print('hi-from-python');import sys;print('args=',sys.argv[1:])",
            "args": ["--epochs", "2"],
            "timeout_sec": 15,
            "max_output_kb": 64
        }
        async with AsyncClient() as client:
            r = await client.post(url, json=req, timeout=40)
        self.assertEqual(r.status_code, 200, "/api/run/python 应返回 200")
        data = r.json()
        self.assertEqual(data.get("returncode"), 0)
        out = self._b64_to_text(data.get("stdout_b64", ""))
        self.assertIn("hi-from-python", out)
        self.assertIn("--epochs", out)
        print("[run/python] stdout:", out.strip())

    async def test_run_cmd(self):
        url = f"{self.base_url}/api/run/cmd"
        # 尽量通用：调用 python -c 打印一行
        req = {
            "cmd": ["pwd"],
            "timeout_sec": 15,
            "max_output_kb": 64
        }
        async with AsyncClient() as client:
            r = await client.post(url, json=req, timeout=40)
        self.assertEqual(r.status_code, 200, "/api/run/cmd 应返回 200")
        data = r.json()
        self.assertEqual(data.get("returncode"), 0)
        out = self._b64_to_text(data.get("stdout_b64", ""))
        self.assertIn("hello-cmd", out)
        print("[run/cmd] stdout:", out.strip())

if __name__ == "__main__":
    unittest.main(verbosity=2)

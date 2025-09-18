# -*- coding: utf-8 -*-
import os
import re
import io
import json
import time
import base64
import tempfile
import hashlib
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

"""
训练控制后端 API（无状态 + 轻沙箱）
能力：
1) 项目配置：初始化、读取、保存
2) 文件：读取、写入、修改（基于简单操作）
3) 运行：Python 脚本/代码、任意命令（带超时与输出截断）

安全与约束：
- 所有文件操作均限制在 BASE_DIR (WORKSPACE_DIR 环境变量或 ./workspace) 内
- 写入采用原子写，防止半写
- 运行命令有超时与输出大小上限
"""

# ================================
# ---------- 基础设置 ------------
# ================================

BASE_DIR = Path(os.environ.get("WORKSPACE_DIR", ".")).resolve()
PROJECTS_DIR = BASE_DIR / "projects"
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)

def _ensure_under_base(path: Path) -> Path:
    """确保路径位于 BASE_DIR 沙箱内"""
    path = path.resolve()
    if os.path.commonpath([str(path), str(BASE_DIR)]) != str(BASE_DIR):
        raise HTTPException(status_code=400, detail="路径不允许越过工作区（BASE_DIR）")
    return path

def _resolve(path_str: str, base: Optional[Path] = None) -> Path:
    base = base or BASE_DIR
    p = (base / path_str).resolve() if not os.path.isabs(path_str) else Path(path_str).resolve()
    return _ensure_under_base(p)

def _sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def _atomic_write_bytes(target: Path, content: bytes):
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=str(target.parent), delete=False) as tf:
        tf.write(content)
        tmp = Path(tf.name)
    os.replace(tmp, target)

def _read_bytes_limited(path: Path, max_bytes: int) -> (bytes, bool, int):
    size = path.stat().st_size
    truncated = False
    if size > max_bytes:
        truncated = True
        with open(path, "rb") as f:
            data = f.read(max_bytes)
    else:
        data = path.read_bytes()
    return data, truncated, size

# ================================
# ---------- FastAPI -------------
# ================================

app = FastAPI(title="Training Controller API", version="0.1.0")

# 允许所有源，方便联调
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

# ================================
# ---------- 数据模型 ------------
# ================================

class ProjectConfig(BaseModel):
    project_id: str = Field(..., description="项目唯一 ID（目录名）")
    name: Optional[str] = Field(None, description="项目名称（可读）")
    model: Optional[str] = Field(None, description="使用的模型名称")
    mcp_tools: List[str] = Field(default_factory=list, description="使用的 MCP 工具列表")
    extra: Dict[str, Any] = Field(default_factory=dict, description="其他自定义配置")

class InitProjectReq(BaseModel):
    project_id: str
    name: Optional[str] = None
    model: Optional[str] = None
    mcp_tools: List[str] = Field(default_factory=list)
    extra: Dict[str, Any] = Field(default_factory=dict, description="自定义配置")

class SaveProjectReq(BaseModel):
    project_id: str
    config: Dict[str, Any]

class FSReadReq(BaseModel):
    path: str = Field(..., description="工作区内的相对路径，或位于工作区内的绝对路径")
    binary: bool = Field(False, description="是否按二进制返回（否则按文本返回）")
    encoding: str = "utf-8"
    max_bytes: int = Field(5 * 1024 * 1024, description="最大读取字节数，超出会截断")

class FSWriteReq(BaseModel):
    path: str
    content: Optional[str] = Field(None, description="文本内容（和 content_b64 二选一）")
    content_b64: Optional[str] = Field(None, description="base64 内容（优先级高于 content）")
    encoding: str = "utf-8"
    append: bool = Field(False, description="是否追加到文件末尾")
    create_dirs: bool = True
    overwrite: bool = True

class FSModifyReq(BaseModel):
    path: str
    op: Literal["regex_replace", "replace", "append", "prepend", "insert_after"] = "replace"
    # 针对 replace/regex_replace/insert_after：
    find: Optional[str] = Field(None, description="要查找的文本或正则")
    replacement: Optional[str] = Field(None, description="替换文本（append/prepend 可忽略）")
    occurrence: int = Field(0, description="0=全部；>0 仅替换第 N 次匹配")

class RunPythonReq(BaseModel):
    # 二选一：script_path 或 code
    script_path: Optional[str] = None
    code: Optional[str] = None
    args: List[str] = Field(default_factory=list)
    workdir: Optional[str] = None
    env: Dict[str, str] = Field(default_factory=dict)
    timeout_sec: int = 600
    max_output_kb: int = 1024

class RunCmdReq(BaseModel):
    cmd: List[str] = Field(..., description="命令及参数（强烈推荐 list 形式，避免 shell 注入）")
    shell: bool = Field(False, description="如必须传字符串命令，可设为 True（自行确保安全）")
    workdir: Optional[str] = None
    env: Dict[str, str] = Field(default_factory=dict)
    timeout_sec: int = 600
    max_output_kb: int = 1024

# ================================
# ---------- 项目配置 ------------
# ================================

def _project_dir(pid: str) -> Path:
    return _ensure_under_base(PROJECTS_DIR / pid)

def _config_path(pid: str) -> Path:
    return _project_dir(pid) / "config.json"

@app.post("/api/projects/init")
def api_project_init(req: InitProjectReq):
    pdir = _project_dir(req.project_id)
    pdir.mkdir(parents=True, exist_ok=True)
    cfg = ProjectConfig(
        project_id=req.project_id,
        name=req.name,
        model=req.model,
        mcp_tools=req.mcp_tools,
        extra=req.extra,
    ).dict()
    cfg_path = _config_path(req.project_id)
    if cfg_path.exists():
        # 保留已有字段，更新传入字段
        old = json.loads(cfg_path.read_text(encoding="utf-8"))
        old.update({k: v for k, v in cfg.items() if v is not None})
        cfg = old
    _atomic_write_bytes(cfg_path, json.dumps(cfg, ensure_ascii=False, indent=2).encode("utf-8"))
    return {"ok": True, "project_id": req.project_id, "config_path": str(cfg_path.relative_to(BASE_DIR)), "config": cfg}

@app.get("/api/projects/{project_id}/config")
def api_project_get_config(project_id: str):
    cfg_path = _config_path(project_id)
    if not cfg_path.exists():
        raise HTTPException(status_code=404, detail="项目配置不存在")
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    return {"ok": True, "project_id": project_id, "config": cfg}

@app.put("/api/projects/{project_id}/config")
def api_project_save_config(project_id: str, req: SaveProjectReq):
    if project_id != req.project_id:
        raise HTTPException(status_code=400, detail="路径与请求体的 project_id 不一致")
    cfg_path = _config_path(project_id)
    _atomic_write_bytes(cfg_path, json.dumps(req.config, ensure_ascii=False, indent=2).encode("utf-8"))
    return {"ok": True, "project_id": project_id, "config": req.config}

@app.get("/api/projects")
def api_project_list():
    items = []
    for d in PROJECTS_DIR.glob("*/config.json"):
        try:
            cfg = json.loads(d.read_text(encoding="utf-8"))
            items.append({"project_id": cfg.get("project_id"), "name": cfg.get("name"), "path": str(d.parent.relative_to(BASE_DIR))})
        except Exception:
            pass
    return {"ok": True, "projects": items}

# ================================
# ---------- 文件读/写/改 --------
# ================================

@app.post("/api/fs/read")
def api_fs_read(req: FSReadReq):
    path = _resolve(req.path)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")
    data, truncated, total_size = _read_bytes_limited(path, req.max_bytes)
    if req.binary:
        content_b64 = base64.b64encode(data).decode("ascii")
        return {
            "ok": True, "path": str(path.relative_to(BASE_DIR)),
            "size": total_size, "sha256": _sha256_bytes(data),
            "content_b64": content_b64, "truncated": truncated
        }
    else:
        try:
            text = data.decode(req.encoding, errors="replace")
        except Exception:
            raise HTTPException(status_code=400, detail="文本解码失败")
        return {
            "ok": True, "path": str(path.relative_to(BASE_DIR)),
            "size": total_size, "sha256": _sha256_bytes(data),
            "content": text, "truncated": truncated, "encoding": req.encoding
        }

@app.post("/api/fs/write")
def api_fs_write(req: FSWriteReq):
    path = _resolve(req.path)
    if not req.overwrite and path.exists() and not req.append:
        raise HTTPException(status_code=409, detail="文件已存在且不允许覆盖")
    if req.append and not path.exists():
        # 若 append 但文件不存在，视为创建
        path.parent.mkdir(parents=True, exist_ok=True)

    if req.content_b64 is not None:
        raw = base64.b64decode(req.content_b64.encode("ascii"))
    else:
        raw = (req.content or "").encode(req.encoding)

    if req.append and path.exists():
        # 追加：读现有 + 拼接后原子写
        orig = path.read_bytes()
        raw = orig + raw

    if req.create_dirs:
        path.parent.mkdir(parents=True, exist_ok=True)

    _atomic_write_bytes(path, raw)
    return {"ok": True, "path": str(path.relative_to(BASE_DIR)), "size": len(raw), "sha256": _sha256_bytes(raw)}

@app.post("/api/fs/modify")
def api_fs_modify(req: FSModifyReq):
    path = _resolve(req.path)
    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="文件不存在")

    text = path.read_text(encoding="utf-8")

    if req.op == "append":
        new_text = text + (req.replacement or "")
    elif req.op == "prepend":
        new_text = (req.replacement or "") + text
    elif req.op == "insert_after":
        if not req.find:
            raise HTTPException(status_code=400, detail="insert_after 需要 find")
        occurrence = req.occurrence
        cnt = 0
        def _insert_after_once(s: str) -> str:
            nonlocal cnt
            idx = s.find(req.find)
            if idx == -1:
                return s
            idx_end = idx + len(req.find)
            cnt += 1
            return s[:idx_end] + (req.replacement or "") + s[idx_end:]
        if occurrence <= 0:
            s = text
            prev = None
            while prev != s:
                prev = s
                s2 = _insert_after_once(s)
                if s2 == s:  # 无更多匹配
                    break
                s = s2
            new_text = s
        else:
            s = text
            for _ in range(occurrence):
                s2 = _insert_after_once(s)
                if s2 == s:
                    break
                s = s2
            new_text = s
    elif req.op in ("replace", "regex_replace"):
        if req.find is None:
            raise HTTPException(status_code=400, detail="replace/regex_replace 需要 find")
        repl = req.replacement or ""
        if req.op == "replace":
            if req.occurrence <= 0:
                new_text = text.replace(req.find, repl)
            else:
                new_text = text
                for _ in range(req.occurrence):
                    idx = new_text.find(req.find)
                    if idx == -1:
                        break
                    new_text = new_text[:idx] + repl + new_text[idx + len(req.find):]
        else:
            flags = re.MULTILINE
            pat = re.compile(req.find, flags)
            if req.occurrence <= 0:
                new_text = pat.sub(repl, text)
            else:
                new_text = pat.sub(repl, text, count=req.occurrence)
    else:
        raise HTTPException(status_code=400, detail="不支持的修改操作")

    _atomic_write_bytes(path, new_text.encode("utf-8"))
    return {"ok": True, "path": str(path.relative_to(BASE_DIR)), "bytes": len(new_text.encode('utf-8'))}

# ================================
# ---------- 运行 Python ----------
# ================================

@app.post("/api/run/python")
def api_run_python(req: RunPythonReq):
    if not req.script_path and not req.code:
        raise HTTPException(status_code=400, detail="需要 script_path 或 code 之一")

    workdir = _resolve(req.workdir) if req.workdir else BASE_DIR
    py_exe = os.environ.get("PYTHON_EXECUTABLE") or os.sys.executable

    tmp_file: Optional[Path] = None
    try:
        if req.code and not req.script_path:
            # 将 code 落临时文件，便于带 args 执行
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".py", dir=str(workdir))
            tmp.write(req.code.encode("utf-8"))
            tmp.close()
            tmp_file = Path(tmp.name)
            script = tmp_file
        else:
            script = _resolve(req.script_path)  # type: ignore
            if not script.exists():
                raise HTTPException(status_code=404, detail="脚本不存在")

        cmd = [py_exe, str(script)] + list(req.args)
        env = {**os.environ, **req.env}

        t0 = time.time()
        completed = subprocess.run(
            cmd,
            cwd=str(workdir),
            env=env,
            capture_output=True,
            text=False,
            timeout=req.timeout_sec,
        )
        dur = int((time.time() - t0) * 1000)

        # 输出截断
        maxb = req.max_output_kb * 1024
        stdout = completed.stdout[:maxb]
        stderr = completed.stderr[:maxb]
        truncated = (len(completed.stdout) > len(stdout)) or (len(completed.stderr) > len(stderr))

        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "duration_ms": dur,
            "stdout_b64": base64.b64encode(stdout).decode("ascii"),
            "stderr_b64": base64.b64encode(stderr).decode("ascii"),
            "truncated": truncated,
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail=f"Python 运行超时（>{req.timeout_sec}s）")
    finally:
        if tmp_file and tmp_file.exists():
            try:
                tmp_file.unlink()
            except Exception:
                pass

# ================================
# ---------- 运行命令行 -----------
# ================================

@app.post("/api/run/cmd")
def api_run_cmd(req: RunCmdReq):
    workdir = _resolve(req.workdir) if req.workdir else BASE_DIR
    env = {**os.environ, **req.env}

    try:
        t0 = time.time()
        if req.shell:
            # shell=True 时，cmd 只取第 1 个元素或 join；请注意安全
            if isinstance(req.cmd, list):
                shell_cmd = " ".join(req.cmd)
            else:
                shell_cmd = str(req.cmd)
            completed = subprocess.run(
                shell_cmd,
                shell=True,
                cwd=str(workdir),
                env=env,
                capture_output=True,
                text=False,
                timeout=req.timeout_sec,
            )
        else:
            completed = subprocess.run(
                req.cmd,
                cwd=str(workdir),
                env=env,
                capture_output=True,
                text=False,
                timeout=req.timeout_sec,
            )
        dur = int((time.time() - t0) * 1000)

        maxb = req.max_output_kb * 1024
        stdout = completed.stdout[:maxb]
        stderr = completed.stderr[:maxb]
        truncated = (len(completed.stdout) > len(stdout)) or (len(completed.stderr) > len(stderr))

        return {
            "ok": completed.returncode == 0,
            "returncode": completed.returncode,
            "duration_ms": dur,
            "stdout_b64": base64.b64encode(stdout).decode("ascii"),
            "stderr_b64": base64.b64encode(stderr).decode("ascii"),
            "truncated": truncated,
        }
    except subprocess.TimeoutExpired:
        raise HTTPException(status_code=408, detail=f"命令运行超时（>{req.timeout_sec}s）")

# ================================
# 根路由与健康检查
# ================================
@app.get("/")
def root():
    return {
        "name": "Training Controller API",
        "version": "0.1.0",
        "base_dir": str(BASE_DIR),
        "endpoints": {
            "POST /api/projects/init": "初始化项目配置（如不存在则创建）",
            "GET  /api/projects": "列出已有项目（基于 config.json）",
            "GET  /api/projects/{project_id}/config": "读取项目配置",
            "PUT  /api/projects/{project_id}/config": "保存/覆盖项目配置",
            "POST /api/fs/read": "读取文件（文本/二进制，支持截断）",
            "POST /api/fs/write": "写入/追加文件（原子写）",
            "POST /api/fs/modify": "更改文件（replace/regex/append/prepend/insert_after）",
            "POST /api/run/python": "运行 Python（脚本路径或内联 code）",
            "POST /api/run/cmd": "运行命令行程序（带超时/截断）",
            "GET/POST /ping": "健康检查",
        },
    }

@app.post('/ping')
@app.get('/ping')
def ping():
    return 'Pong'

# 本地启动
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8600)

# MCP Server 创建手册

## 项目结构

```
my-mcp-server/
├── server.py              # MCP 主程序
├── requirements.txt       # Python 依赖
├── pyproject.toml         # 包配置（ModelScope 需要）
├── Dockerfile             # Docker 部署
├── docker-compose.yml     # Docker Compose
└── README.md              # 说明文档
```

## server.py 模板

```python
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("your-mcp-name", host="0.0.0.0", port=8000)

# ---- Tools ----
@mcp.tool()
def your_tool(param: str) -> str:
    """工具描述。Args: param: 参数说明"""
    import json
    return json.dumps({"result": param}, ensure_ascii=False, indent=2)

# ---- Resources (可选) ----
@mcp.resource("your://resource")
def your_resource() -> str:
    import json
    return json.dumps({"data": "value"}, ensure_ascii=False, indent=2)

# ---- 入口 ----
def main():
    import sys
    if "--sse" in sys.argv:
        mcp.run(transport="sse")
    else:
        mcp.run()

if __name__ == "__main__":
    main()
```

## requirements.txt

```
mcp[cli]>=1.0.0
```

## pyproject.toml

```toml
[project]
name = "your-mcp-name"
version = "1.0.0"
description = "项目描述"
requires-python = ">=3.10"
dependencies = ["mcp[cli]>=1.0.0"]

[project.scripts]
your-mcp-name = "server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
```

## Dockerfile

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -i https://mirrors.aliyun.com/pypi/simple/ -r requirements.txt
COPY server.py .
EXPOSE 8000
CMD ["python", "server.py", "--sse"]
```

## docker-compose.yml

```yaml
services:
  mcp-server:
    build: .
    ports:
      - "8000:8000"
    restart: always
```

## 本地开发调试

```bash
# 安装依赖
pip install "mcp[cli]"

# 启动 MCP Inspector 可视化调试
mcp dev server.py

# 运行 MCP 客户端测试
python mcp_client_test.py

# 启动 SSE 服务（本地）
python server.py --sse
```

## 部署流程

### 方式一：Docker 自部署

1. 修改 `server.py` 中 `FastMCP(host="0.0.0.0")` 绑定公网
2. 上传到服务器：`git clone <repo-url>`
3. 启动：`docker compose up -d --build`
4. 开放防火墙端口 8000/TCP
5. 验证：`curl http://<公网IP>:8000/sse`

### 方式二：发布到 ModelScope（魔塔社区）

1. 创建 GitHub 公开仓库并推送代码
2. 到 [modelscope.cn/mcp](https://modelscope.cn/mcp) 点击"自定义创建"
3. 填写：
   - 来源地址：GitHub 仓库 URL
   - 托管类型：选"仅本地可用"（可托管部署经常失败）
   - Stdio 配置：`command: python, args: ["server.py"]`
   - SSE 配置：`command: python, args: ["server.py", "--sse"]`

## MaxKB 接入

```json
{
  "your-mcp-name": {
    "url": "http://<公网IP>:8000/sse",
    "transport": "sse"
  }
}
```

## 常见问题

| 问题 | 解决 |
|------|------|
| `FastMCP.run() got unexpected keyword argument 'host'` | 把 host/port 放到 `FastMCP("name", host="0.0.0.0")` 构造函数里 |
| Docker 容器反复重启 | `docker logs` 查看日志，通常是 Python 报错 |
| 端口不通 | 检查防火墙规则，来源须设 `0.0.0.0/0` |
| pip 下载慢 | Dockerfile 用 `-i https://mirrors.aliyun.com/pypi/simple/` |
| MCP Inspector 连接超时 | server.py 默认用 stdio 模式（`mcp.run()`），不要加 `--sse` |
| GBK 编码报错 | Windows 终端执行前 `set PYTHONIOENCODING=utf-8` |

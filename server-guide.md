# 阿里云轻量服务器使用手册

## 服务器信息

| 项目 | 详情 |
|------|------|
| 公网 IP | 8.160.169.239 |
| 服务端口 | 8000 (MCP SSE), 8080 (校园地图) |
| 镜像 | Docker |
| 项目目录 | /home/admin/scuec-campus-mcp |

## SSH 登录

```bash
ssh admin@8.160.169.239
```

## Docker 常用命令

```bash
# 查看运行中的容器
sudo docker ps

# 查看容器日志（排查错误）
sudo docker logs -f 容器名

# 重启所有服务
cd /home/admin/scuec-campus-mcp
sudo docker compose restart

# 重新构建并启动
git pull
sudo docker compose up -d --build

# 只重建某个服务
sudo docker compose up -d --build 服务名

# 停止所有服务
sudo docker compose down

# 查看容器资源占用
sudo docker stats
```

## 项目更新流程

```bash
cd /home/admin/scuec-campus-mcp
git pull
sudo docker compose up -d --build campus-mcp    # MCP 服务
# sudo docker compose restart campus-web        # 静态文件 nginx 重启即可
```

## 防火墙管理

阿里云控制台 → 轻量应用服务器 → 防火墙，需开放：

| 端口 | 协议 | 来源 | 用途 |
|------|------|------|------|
| 8000 | TCP | 0.0.0.0/0 | MCP SSE 服务 |
| 8080 | TCP | 0.0.0.0/0 | 校园地图网页 |

## 服务验证

```bash
# 验证 MCP 服务
curl http://8.160.169.239:8000/sse

# 验证地图网页
curl -I http://8.160.169.239:8080/

# 本地测试
curl http://localhost:8000/sse
```

## 系统维护

```bash
# 查看磁盘空间
df -h

# 查看内存
free -h

# 清理 Docker 无用镜像和容器
sudo docker system prune -a

# 查看系统日志
sudo journalctl -xe

# 重启服务器
sudo reboot
```

## 服务架构

```
Docker Compose:
├── campus-mcp    → Python server.py --sse  → 0.0.0.0:8000
└── campus-web    → Nginx:alpine            → 0.0.0.0:8080
                     └── 挂载 ./static/     → /usr/share/nginx/html
```

## MaxKB 配置

```json
{
  "campus-map": {
    "url": "http://8.160.169.239:8000/sse",
    "transport": "sse"
  }
}
```

## 故障排查

| 现象 | 检查 |
|------|------|
| 端口不通 | `sudo docker ps` 看容器状态；阿里云防火墙规则 |
| 容器重启循环 | `sudo docker logs 容器名` 看错误日志 |
| git pull 失败 | `git -c http.sslVerify=false pull` |
| Docker 权限拒绝 | 命令前加 `sudo` |

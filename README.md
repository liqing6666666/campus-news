# 中南民族大学校园资讯 MCP 服务

为 MaxKB 校园通智能体提供中南民族大学（SCUEC）最新资讯查询能力。

## 功能

| Tool | 说明 |
|------|------|
| `get_campus_news` | 获取学校主站新闻（民大要闻/南湖快讯/媒体民大） |
| `get_college_news` | 获取各学院最新资讯 |
| `get_department_news` | 获取教务处、学工在线最新资讯 |
| `get_article_detail` | 获取文章全文内容 |
| `list_colleges` | 列出所有可用学院 |
| `list_departments` | 列出所有可用部门 |

## 项目结构

```
├── server.py              # MCP 主程序（FastMCP SSE 模式）
├── scraper.py             # HTML 抓取与解析模块
├── sites.py               # 学院/部门站点代码映射表
├── cache.py               # 简易 TTL 内存缓存
├── requirements.txt       # Python 依赖
├── pyproject.toml         # 包配置
├── Dockerfile             # Docker 部署
├── docker-compose.yml     # Docker Compose
└── test_server.py         # 本地测试脚本
```

## 技术选型

| 层面 | 选择 | 原因 |
|------|------|------|
| MCP 框架 | `mcp[cli]>=1.0.0` (FastMCP) | 支持 SSE 传输 |
| HTTP 客户端 | `httpx` | 异步支持 |
| HTML 解析 | `beautifulsoup4` + `lxml` | 容错性好 |
| 缓存 | 自实现 TTL dict | 零依赖，5min/30min 过期 |

## 数据来源

中南民族大学官网使用**博达站群 CMS V2.0**，无 RSS/API，通过 HTML 抓取获取数据。

### URL 模式

- 主站新闻列表: `https://www.scuec.edu.cn/xww/{column_code}/{page}.htm`
- 文章详情页: `https://www.scuec.edu.cn/{site_code}/info/{category_id}/{article_id}.htm`
- 学院列表页: `https://www.scuec.edu.cn/{site_code}/index.htm`

### 新闻分类

| 分类 | 栏目代码 |
|------|----------|
| 民大要闻 | `mdkx` |
| 南湖快讯 | `stxy` |
| 媒体民大 | `mtmd` |

## 本地开发

```bash
pip install -r requirements.txt
mcp dev server.py          # MCP Inspector 调试
python server.py --sse     # 启动 SSE 服务
```

## 部署

### 步骤 1: 上传文件到服务器

```bash
# 方式 A: 使用 SCP（在本地终端执行）
scp -r f:/desktop/校园资讯/* admin@8.160.169.239:/home/admin/scuec-campus-news/

# 方式 B: 使用 Git（推荐）
cd f:/desktop/校园资讯
git init && git add -A && git commit -m "init campus-news MCP"
git remote add origin <your-git-repo-url>
git push -u origin main
# 然后在服务器上 git clone
```

### 步骤 2: 服务器端构建启动

```bash
ssh admin@8.160.169.239
cd /home/admin/scuec-campus-news
sudo docker compose up -d --build
```

### 步骤 3: 开放防火墙端口

阿里云控制台 → 轻量应用服务器 → 防火墙 → 添加规则：
- 端口: `8001`，协议: TCP，来源: `0.0.0.0/0`

### 步骤 4: 验证服务

```bash
curl http://8.160.169.239:8001/sse
# 应返回: data: {"jsonrpc":"2.0",...}
```

## MaxKB 配置

```json
{
  "campus-news": {
    "url": "http://8.160.169.239:8001/sse",
    "transport": "sse"
  }
}
```

## 端口规划

| 端口 | 服务 |
|------|------|
| 8000 | campus-mcp（校园地图） |
| 8001 | campus-news（校园资讯，本项目） |
| 8080 | campus-web（地图网页） |

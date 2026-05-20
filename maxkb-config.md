# MaxKB 应用配置 — 校园资讯

## 1. MCP 服务名称

```
campus-news
```

## 2. MCP 工具配置

```json
{
  "campus-news": {
    "url": "http://8.160.169.239:8001/sse",
    "transport": "sse"
  }
}
```

**配置步骤：**
1. MaxKB 后台 → 应用管理 → 选择"校园通"智能体 → AI 对话设置
2. 找到 MCP Server 配置区域
3. 添加上述 JSON（与已有的 campus-map 并列）
4. 保存并测试连接

## 3. MCP 工具说明

| 工具名 | 功能 | 输入参数 | 输出 |
|--------|------|----------|------|
| get_campus_news | 获取学校主站新闻 | `category` (可选:"民大要闻"/"南湖快讯"/"媒体民大"), `page`, `limit` | 新闻列表：标题、日期、URL |
| get_college_news | 获取各学院最新资讯 | `college` (必填，支持模糊匹配), `page`, `limit` | 学院新闻列表：标题、日期、URL |
| get_department_news | 获取教务处/学工在线/图书馆资讯 | `department` (可选), `page`, `limit` | 部门资讯列表：标题、日期、URL |
| get_article_detail | 获取文章全文内容 | `url` (必填) | 文章标题、日期、正文、来源 |
| list_colleges | 列出所有可用学院 | 无 | 22 个学院名称及站点代码 |
| list_departments | 列出所有可用部门 | 无 | 3 个部门名称及站点代码 |

## 4. 数据覆盖

| 类别 | 覆盖 | 说明 |
|------|------|------|
| 主站新闻 | 3 个栏目 | 民大要闻、南湖快讯、媒体民大 |
| 学院 | 22 个学院 | 支持全称/简称模糊匹配 |
| 部门 | 3 个部门 | 教务处、学工在线、图书馆 |

## 5. 系统提示词（推荐追加到校园通智能体）

```
## 校园资讯能力

你可以通过以下工具获取中南民族大学最新资讯：
- get_campus_news: 获取学校主站新闻（民大要闻/南湖快讯/媒体民大）
- get_college_news: 获取各学院最新资讯，支持名称模糊匹配（如"计科""法学院"）
- get_department_news: 获取教务处、学工在线、图书馆的最新通知
- get_article_detail: 获取某篇文章的完整内容
- list_colleges: 查看有哪些学院可查
- list_departments: 查看有哪些部门可查

## 回复规则
1. 用户询问"学校有什么新闻"时，调用 get_campus_news
2. 用户询问某学院动态时，先用 list_colleges 确认学院名，再调用 get_college_news
3. 用户询问"教务处通知""图书馆公告"时，调用 get_department_news
4. 用户想看某篇文章详情时，调用 get_article_detail
5. 回复时列出标题、日期，附上文章链接方便用户点击查看
6. 回复使用中文，简洁友好
```

## 6. 测试用例

```
1. "学校最近有什么新闻？"           → 调用 get_campus_news("民大要闻")
2. "计算机科学学院有什么动态？"      → 调用 get_college_news("计科")
3. "教务处最新通知"                 → 调用 get_department_news("教务处")
4. "帮我看看这篇文章" + 链接        → 调用 get_article_detail(url)
5. "有哪些学院可以查？"             → 调用 list_colleges
6. "法学院最近有什么新闻？"          → 调用 get_college_news("法学院")
```

## 7. 服务依赖

| 服务 | 地址 | 状态检查 |
|------|------|----------|
| MCP SSE | http://8.160.169.239:8001/sse | `curl http://8.160.169.239:8001/sse` |

## 8. 端口规划

| 端口 | MCP 服务 | 用途 |
|------|----------|------|
| 8000 | campus-map | 校园地图（POI、导航） |
| 8001 | campus-news | 校园资讯（新闻、通知） |
| 8080 | campus-web | 校园地图网页 |

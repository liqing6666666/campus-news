"""SCUEC Campus News MCP Server — 中南民族大学校园资讯 MCP 服务."""

import json
from mcp.server.fastmcp import FastMCP

from scraper import fetch_list_page, fetch_article_detail, ScraperError
from sites import (
    DEFAULT_BASE, get_site_url,
    COLLEGES, DEPARTMENTS, NEWS_CATEGORIES,
    search_college, search_department,
)

mcp = FastMCP("scuec-campus-news", host="0.0.0.0", port=8001)


def _ok(data) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _err(msg: str) -> str:
    return json.dumps({"error": msg}, ensure_ascii=False)


# ---- Tools ----

@mcp.tool()
def get_campus_news(category: str = "民大要闻", page: int = 1, limit: int = 10) -> str:
    """获取中南民族大学主站新闻。

    Args:
        category: 新闻分类，可选"民大要闻"、"南湖快讯"、"媒体民大"
        page: 页码，从1开始
        limit: 每页条数，最大20
    """
    column_code = NEWS_CATEGORIES.get(category)
    if not column_code:
        return _err(f"未知分类: {category}，可选: {list(NEWS_CATEGORIES.keys())}")

    limit = min(limit, 20)
    # column homepage (no page number) = latest news
    # /{code}/{n}.htm = paginated (1=oldest, max=newest)
    if page <= 1:
        url = f"{DEFAULT_BASE}/xww/{column_code}.htm"
    else:
        url = f"{DEFAULT_BASE}/xww/{column_code}/{page}.htm"
    try:
        items = fetch_list_page(url, limit)
        return _ok({
            "category": category,
            "page": page,
            "count": len(items),
            "items": items,
        })
    except ScraperError as e:
        return _err(str(e))


@mcp.tool()
def get_college_news(college: str, page: int = 1, limit: int = 10) -> str:
    """获取中南民族大学各学院最新资讯。支持学院全称或简称，如"计算机科学学院"、"计科"。

    Args:
        college: 学院名称（支持模糊匹配）
        page: 页码
        limit: 每页条数，最大20
    """
    site_code = search_college(college)
    if not site_code:
        coll_names = "\n".join(f"  {n} ({c})" for n, c in COLLEGES.items())
        return _err(f"未找到学院: {college}\n可用学院:\n{coll_names}")

    limit = min(limit, 20)
    url = get_site_url(site_code, "index.htm")
    try:
        items = fetch_list_page(url, limit)
        college_name = next((n for n, c in COLLEGES.items() if c == site_code), site_code)
        return _ok({
            "college": college_name,
            "site_code": site_code,
            "page": page,
            "count": len(items),
            "items": items,
        })
    except ScraperError as e:
        return _err(str(e))


@mcp.tool()
def get_department_news(department: str = "教务处", page: int = 1, limit: int = 10) -> str:
    """获取中南民族大学教务处、学工在线、图书馆最新资讯。

    Args:
        department: 部门名称：教务处 / 学工在线 / 图书馆
        page: 页码
        limit: 每页条数，最大20
    """
    site_code = search_department(department)
    if not site_code:
        dep_names = ", ".join(DEPARTMENTS.keys())
        return _err(f"未找到部门: {department}，可选: {dep_names}")

    limit = min(limit, 20)
    url = get_site_url(site_code, "index.htm")

    try:
        items = fetch_list_page(url, limit)
        dept_name = next((n for n, c in DEPARTMENTS.items() if c == site_code), site_code)
        return _ok({
            "department": dept_name,
            "site_code": site_code,
            "page": page,
            "count": len(items),
            "items": items,
        })
    except ScraperError as e:
        return _err(str(e))


@mcp.tool()
def get_article_detail(url: str) -> str:
    """获取文章详情页的完整内容。

    Args:
        url: 文章详情页的完整 URL（如 https://www.scuec.edu.cn/xww/info/1002/16114.htm）
    """
    if not url or not url.startswith("http"):
        return _err("请提供完整的文章 URL")
    try:
        detail = fetch_article_detail(url)
        return _ok(detail)
    except ScraperError as e:
        return _err(str(e))


@mcp.tool()
def list_colleges() -> str:
    """列出所有可查询的学院及其站点代码。"""
    return _ok([{"name": n, "site_code": c} for n, c in COLLEGES.items()])


@mcp.tool()
def list_departments() -> str:
    """列出所有可查询的部门及其站点代码。"""
    return _ok([{"name": n, "site_code": c} for n, c in DEPARTMENTS.items()])


# ---- Entry ----

def main():
    import sys
    if "--sse" in sys.argv:
        mcp.run(transport="sse")
    else:
        mcp.run()


if __name__ == "__main__":
    main()

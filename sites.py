"""SCUEC college and department site code mappings."""

COLLEGES: dict[str, str] = {
    "法学院": "fxy",
    "民族学与社会学学院": "mz2025",
    "公共管理学院": "gggl",
    "经济学院": "economics",
    "文学与新闻传播学院": "literature",
    "电子信息工程学院": "dxxy",
    "化学与材料科学学院": "hcxy",
    "计算机科学学院": "jky",
    "生命科学学院": "smkx",
    "外语学院": "wyxy",
    "美术学院": "art",
    "马克思主义学院": "mkszyxy",
    "管理学院": "som",
    "药学院": "yxy",
    "生物医学工程学院": "syxy",
    "数学与统计学学院": "math",
    "体育学院": "tyxy",
    "音乐舞蹈学院": "musicdancing",
    "教育学院": "jyxy",
    "资源与环境学院": "zhxy",
    "中华民族共同体学院": "gttyjy",
    "研究生院": "yjsy",
}

DEPARTMENTS: dict[str, str] = {
    "教务处": "jwc",
    "学工在线": "stu",
    "图书馆": "lib",
}

NEWS_CATEGORIES: dict[str, str] = {
    "民大要闻": "mdkx",
    "南湖快讯": "stxy",
    "媒体民大": "mtmd",
}

# 独立子域名的站点，不使用 www.scuec.edu.cn/{code} 模式
CUSTOM_BASE: dict[str, str] = {
    "dxxy": "https://dxxy.scuec.edu.cn",
    "lib": "https://www.lib.scuec.edu.cn",
}

DEFAULT_BASE = "https://www.scuec.edu.cn"


def get_base_url(site_code: str) -> str:
    return CUSTOM_BASE.get(site_code, DEFAULT_BASE)


def get_site_url(site_code: str, path: str = "") -> str:
    base = get_base_url(site_code)
    is_subdomain = site_code in CUSTOM_BASE
    if is_subdomain:
        # Subdomain already identifies the site, e.g. https://dxxy.scuec.edu.cn/
        if path:
            return f"{base}/{path.lstrip('/')}"
        return f"{base}/"
    else:
        # www.scuec.edu.cn/{site_code}/...
        if path:
            return f"{base}/{site_code}/{path.lstrip('/')}"
        return f"{base}/{site_code}/"


def search_college(name: str) -> str | None:
    """Fuzzy search for a college by name or keyword. Returns site_code or None."""
    name_lower = name.strip().lower()
    for full_name, code in COLLEGES.items():
        if name_lower in full_name.lower() or code.lower() == name_lower:
            return code
    keywords = {
        "计科": "jky", "计算机": "jky",
        "法学": "fxy",
        "民社": "mz2025", "民族": "mz2025",
        "公管": "gggl", "公共": "gggl",
        "经济": "economics",
        "文学": "literature", "新闻": "literature",
        "电信": "dxxy", "电子": "dxxy",
        "化学": "hcxy", "材化": "hcxy",
        "生科": "smkx", "生命": "smkx",
        "外语": "wyxy",
        "美术": "art",
        "马克思": "mkszyxy", "马院": "mkszyxy",
        "管理": "som",
        "药学": "yxy",
        "生医": "syxy",
        "数学": "math", "统计": "math",
        "体育": "tyxy",
        "音乐": "musicdancing", "舞蹈": "musicdancing",
        "教育": "jyxy",
        "资环": "zhxy", "资源": "zhxy",
        "共同体": "gttyjy",
        "研究生": "yjsy",
    }
    for kw, code in keywords.items():
        if kw in name_lower:
            return code
    return None


def search_department(name: str) -> str | None:
    """Fuzzy search for a department by name. Returns site_code or None."""
    name_lower = name.strip().lower()
    for full_name, code in DEPARTMENTS.items():
        if name_lower in full_name.lower() or code.lower() == name_lower:
            return code
    keywords = {
        "教务": "jwc",
        "学工": "stu", "学生工作": "stu", "学工在线": "stu",
        "图书": "lib", "图书馆": "lib",
    }
    for kw, code in keywords.items():
        if kw in name_lower:
            return code
    return None

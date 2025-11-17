import html
import re
from typing import Optional, Tuple

from colorama import Back, Fore, Style
from colorama import init as colorama_init

from .data_fetcher import Page, Pages, populate_pages

MyPages = Pages(pages={})
colorama_init(autoreset=False)
MOSAIC_MAP = {
    1164105659: "🬞",
    251408512: "🬞",
    3287848953: "🬞",
    2335531887: "🬞",
    2862847544: "🬞",
    1739010369: "🬞",
    1219799629: "🬉",
    2190446388: "🬉",
    2693613557: "🬉",
    2327991958: "🬉",
    3987931972: "🬉",
    1227236920: "🬉",
    1250598021: "🬭",
    1326555685: "🬭",
    1254105466: "🬭",
    4249453864: "🬭",
    4244846807: "🬭",
    2790421332: "🬭",
    299620102: "🬭",
    294742777: "🬭",
    1339760422: "🬷",
    3387636925: "🬷",
    3826504151: "🬷",
    1760051201: "🬷",
    3288266310: "🬷",
    2267014944: "🬷",
    1460303617: "🬵",
    1625865678: "🬵",
    3609107780: "🬵",
    2681114375: "🬵",
    1087885570: "🬵",
    999369151: "🬵",
    1460540445: "🬹",
    2537420265: "🬹",
    2413702233: "🬹",
    3771534768: "🬹",
    207576990: "🬹",
    3147580979: "🬹",
    1685294852: "🬻",
    2913233310: "🬻",
    3806973766: "🬻",
    167497510: "🬻",
    750680978: "🬻",
    2296503594: "🬻",
    1994053858: "🬓",
    2754943555: "🬓",
    1091112751: "🬓",
    2140796170: "🬓",
    2594562150: "🬓",
    2156528839: "▐",
    2201328430: "▐",
    2642197907: "▐",
    2934086162: "▐",
    3352595016: "▐",
    4098534857: "▐",
    1270603014: "▐",
    2015754887: "▐",
    2964044975: "▐",
    2287478073: "🬦",
    3138777730: "🬦",
    3150678580: "🬦",
    693852549: "🬦",
    925899746: "🬦",
    1840924899: "🬦",
    3785335171: "🬦",
    3037313580: "🬁",
    3782488817: "🬁",
    4166044020: "🬁",
    1028566380: "🬁",
    880409429: "🬁",
    3896730824: "🬁",
    610948841: "🬁",
    3215696164: "🬱",
    2353048447: "🬱",
    3772511681: "🬱",
    3838981461: "🬱",
    739691859: "🬱",
    3585010416: "🬏",
    15963642: "🬏",
    2030688620: "🬏",
    2509998914: "🬏",
    3965831124: "🬏",
    2762748738: "🬏",
    3713433556: "🬏",
    2218724507: "🬋",
    1559180511: "🬋",
    872158518: "🬋",
    723504262: "🬋",
    2308811616: "🬠",
    282174899: "🬑",
    2881270998: "🬯",
    3188198897: "🬇",
    3547727352: "🬇",
    3298983629: "🬫",
    3618463797: "🬃",
    3931275958: "🬜",
    4082209591: "🬅",
    1118560998: "🬩",
    1056054768: "🬘",
    225196657: "🬘",
    692512409: "*",
}


def mosaic_char_from_id(n: Optional[int]) -> str:
    key = n if n is not None else -1
    return MOSAIC_MAP.get(key, " ") or " "


def normalize_html(content):
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text", "")
                classes = item.get("classes", item.get("class", ""))
                cls = " ".join(classes) if isinstance(classes, list) else str(classes or "")
                parts.append(f'<span class="{cls}">{text}</span>')
        return "".join(parts)
    return str(content or "")


def extract_gif_id_from_src(src: str):
    if not src:
        return None
    m = re.search(r"(\d+)\.gif", src)
    return int(m.group(1)) if m else None


def search_pages(keyword: str, start=100) -> list[int]:
    return [
        page.number
        for page in MyPages.pages.values()
        if page.number > start and keyword.lower() in page.body.lower()
    ]


FG_MAP = {
    "black": Fore.BLACK,
    "red": Fore.RED,
    "green": Fore.GREEN,
    "yellow": Fore.YELLOW,
    "blue": Fore.BLUE,
    "magenta": Fore.MAGENTA,
    "cyan": Fore.CYAN,
    "white": Fore.WHITE,
}
BG_MAP = {
    "black": Back.BLACK,
    "red": Back.RED,
    "green": Back.GREEN,
    "yellow": Back.YELLOW,
    "blue": Back.BLUE,
    "magenta": Back.MAGENTA,
    "cyan": Back.CYAN,
    "white": Back.WHITE,
}


def css_color_to_ansi(color: str) -> Tuple[str, str]:
    if not color:
        return "", ""
    s = color.strip().lower()
    m = re.fullmatch(r"#([0-9a-f]{3}|[0-9a-f]{6})", s)
    if m:
        hexv = m.group(1)
        if len(hexv) == 3:
            r, g, b = [int(c * 2, 16) for c in hexv]
        else:
            r, g, b = int(hexv[0:2], 16), int(hexv[2:4], 16), int(hexv[4:6], 16)
        return (f"\033[38;2;{r};{g};{b}m", f"\033[48;2;{r};{g};{b}m")
    return FG_MAP.get(s, ""), BG_MAP.get(s, "")


def style_from_class_and_css(classes, style_attr: Optional[str]) -> str:
    if isinstance(classes, str):
        classes = classes.split()
    classes = set(classes or [])
    seq = ""

    # Backgrounds (critical for teletext layout)
    bg_map = {
        "bgB": Back.BLUE,
        "bgBl": Back.BLACK,
        "bgW": Back.WHITE,
        "bgY": Back.YELLOW,
        "bgR": Back.RED,
        "bgG": Back.GREEN,
        "bgC": Back.CYAN,
        "bgM": Back.MAGENTA,
    }
    for k, v in bg_map.items():
        if k in classes:
            seq += v
            break

    # Foreground
    fg_map = {
        "W": Fore.WHITE,
        "Y": Fore.YELLOW,
        "R": Fore.RED,
        "G": Fore.GREEN,
        "C": Fore.CYAN,
        "M": Fore.MAGENTA,
        "bl": Fore.BLACK,  # blue text is 'bl'
        "B": Fore.BLUE,
    }
    # # Bold (Teletext: 'B' is bold; not blue)
    # if "B" in classes or "bold" in classes:
    #     seq += Style.BRIGHT
    for k, v in fg_map.items():
        if k in classes:
            seq += v
            break

    # (Optional) inline CSS fallback for background-color
    if style_attr:
        m = re.search(r"background(?:-color)?\s*:\s*([^;]+)", style_attr, re.I)
        if m:
            # crude named-color support
            named = m.group(1).strip().lower()
            named_bg = {
                "black": Back.BLACK,
                "blue": Back.BLUE,
                "white": Back.WHITE,
                "yellow": Back.YELLOW,
                "red": Back.RED,
                "green": Back.GREEN,
                "cyan": Back.CYAN,
                "magenta": Back.MAGENTA,
            }.get(named)
            if named_bg:
                seq += named_bg
    return seq


SPACE_ODDITIES = {
    "\u00a0",  # NBSP
    "\u2007",  # figure space
    "\u2008",  # punctuation space
    "\u2009",  # thin space
    "\u200a",  # hair space
}
ZERO_WIDTH = {
    "\u200b",
    "\u200c",
    "\u200d",
    "\u2060",  # zwsp, zwnj, zwj, word joiner
}


SPAN_RE = re.compile(
    r'<span\s+class="([^"]*)"(?:[^>]*?style="([^"]*)")?[^>]*>(.*?)</span>', re.DOTALL
)
A_OPEN_RE = re.compile(r"<a [^>]+>", re.I)
A_CLOSE_RE = re.compile(r"</a>", re.I)
BR_RE = re.compile(r"<br\s*/?>", re.I)

LINE_OPEN_RE = re.compile(r'<span\b(?=[^>]*\bclass="[^"]*\bline\b)[^>]*>', re.I)
SPAN_OPEN_RE = re.compile(r"<span\b[^>]*>", re.I)
SPAN_CLOSE_RE = re.compile(r"</span>", re.I)
LINE_TAG_RE = re.compile(r'(<span\b[^>]*\bclass="([^"]*)"[^>]*>)', re.I)


def extract_line_blocks(raw_html: str):
    pos = 0
    while True:
        m = LINE_TAG_RE.search(raw_html, pos)
        if not m:
            break
        classes = m.group(2) or ""

        class_list = classes.lower().split()
        if "line" not in class_list:
            pos = m.end()
            continue

        start = m.end()
        depth = 1
        i = start
        mc: Optional[re.Match[str]] = None  # <- explicitly tracked

        while depth and i < len(raw_html):
            mo = SPAN_OPEN_RE.search(raw_html, i)
            mc = SPAN_CLOSE_RE.search(raw_html, i)
            if not mc:
                break
            if mo and mo.start() < mc.start():
                depth += 1
                i = mo.end()
            else:
                depth -= 1
                i = mc.end()
        if depth == 0 and mc is not None:
            inner = raw_html[start : mc.start()]
        else:
            inner = ""
        yield inner
        pos = i


def _fill_missing_pages(pages: Pages, start: int = 1, end: int = 1000):
    for i in range(start, end + 1):
        if i not in pages.pages:
            pages.pages[i] = Page(number=i, body="")


_ANSI_RE = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")
_ZERO_WIDTH = {"\u200b", "\u200c", "\u200d", "\u2060"}


def update_my_pages(page_start, page_end, batch_size):
    global MyPages
    MyPages = populate_pages(page_start, page_end, batch_size)
    _fill_missing_pages(MyPages)


def _strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s or "")


def _normalize_text(s: str) -> str:
    if not s:
        return ""
    s = _strip_ansi(s)
    s = "".join(ch for ch in s if ch not in _ZERO_WIDTH)
    return "\n".join(line.rstrip() for line in s.splitlines()).strip()


def _is_blank_or_offair(body: str) -> bool:
    t = _normalize_text(body).casefold()
    if not t:
        return True
    if "sidan ej i sändning" in t:
        return True
    non_header = t.replace("svt text", "")
    return non_header.strip() == ""


def _has_content(page_num: int) -> bool:
    p = MyPages.pages.get(int(page_num))
    if not p:
        return False
    return not _is_blank_or_offair(getattr(p, "body", ""))


def next_actual_page(current_page):
    global MyPages
    page_iter = current_page + 1
    while not _has_content(page_iter):
        if (page_iter == 999) or (page_iter < 100):
            return 100
        page_iter = page_iter + 1
    return page_iter


def actual_previous_page(current_page):
    global MyPages
    page_iter = current_page - 1
    while not _has_content(page_iter):
        if page_iter < 100:
            return 100
        page_iter -= 1
    return page_iter


def render_page_no_bs(page=100) -> str:
    try:
        raw = MyPages.pages[page].body
    except KeyError:
        page = 100
        raw = MyPages.pages[page].body
    out_lines = []
    for line_html in extract_line_blocks(raw):
        line_html = A_OPEN_RE.sub("", line_html)
        line_html = A_CLOSE_RE.sub("", line_html)
        line_html = BR_RE.sub("\n", line_html)

        runs = []
        for m in SPAN_RE.finditer(line_html):
            classes = m.group(1) or ""
            style_attr = m.group(2) or ""
            inner = m.group(3) or ""

            gif_id = extract_gif_id_from_src(style_attr)
            if gif_id is not None and "bgImg" in classes.split():
                inner_text = mosaic_char_from_id(gif_id)
            else:
                inner_text = html.unescape(inner)

            style_seq = style_from_class_and_css(classes, style_attr)

            if runs and runs[-1][1] == style_seq:
                runs[-1] = (runs[-1][0] + inner_text, style_seq)
            else:
                runs.append((inner_text, style_seq))
        buf, active = [], None
        for text, style_seq in runs:
            if style_seq != active:
                if active:
                    buf.append(Style.RESET_ALL)
                active = style_seq
                if active:
                    buf.append(active)
            buf.append(text)
        if active:
            buf.append(Style.RESET_ALL)
        line_out = "".join(buf)
        out_lines.append(line_out)
    return "\n".join(out_lines)

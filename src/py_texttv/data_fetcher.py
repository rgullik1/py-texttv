import requests
from pydantic import BaseModel, field_validator


class Page(BaseModel):
    number: int
    body: str

class Pages(BaseModel):
    pages: dict[int, Page]

    @field_validator("pages", mode="after")
    def ensure_dict(cls, v):
        if isinstance(v, dict):
            return v
        if isinstance(v, list):
            return {p.number: p for p in v}
        raise TypeError("pages must be a dict or list of Page")



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

def _normalize_html(data) -> str:
    page_info = data

    content = page_info.get("content", [])

    if "Sidan ej i sändning" in content:
        return ""

    html_content = normalize_html(content)

    return html_content

def populate_pages(page_start=100, page_end=400, batch_size=50, app_id="py-texttv"):
    my_pages = Pages(pages={})
    for start in range(page_start, page_end, batch_size):
        end = start + 99
        span = f"{start}-{end}"
        url = f"https://texttv.nu/api/get/{span}?app={app_id}"
        r = requests.get(url)
        try:
            data = r.json()
        except Exception:
            continue
        for item in data:
            num_raw = item.get("num")
            try:
                num = int(num_raw)
            except (TypeError, ValueError):
                continue
            content = item.get("content", [])
            if isinstance(content, list) and any("Sidan ej i sändning" in str(x) for x in content):
                my_pages.pages[num] = Page(number=num, body="")
            if isinstance(content, str) and "Sidan ej i sändning" in content:
                my_pages.pages[num] = Page(number=num, body="")
            else:
                my_pages.pages[num] = Page(number=num, body=_normalize_html(item))
    return my_pages
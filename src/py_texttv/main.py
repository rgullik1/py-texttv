from __future__ import annotations

from datetime import datetime

from blessed import Terminal

from .page import (
    actual_previous_page,
    next_actual_page,
    render_page_no_bs,
    search_pages,
    update_my_pages,
)

term = Terminal()
global latest_search
global total_offset
HELP  = "[<- ->] page -/+1   [g] goto   [q] quit   [s] search   [1-9] quick navigate"

def _draw_scrollbar(*, scroll: int, total: int, viewport: int, top_y: int, bottom_y: int, x: int) -> None:
    track_len = max(0, bottom_y - top_y + 1)
    if track_len <= 0:
        return

    # track
    for y in range(top_y, bottom_y + 1):
        print(term.move_yx(y, x) + "▯")   # track glyph

    if total <= 0 or viewport <= 0 or total <= viewport:
        # full content fits; show a filled bar
        for y in range(top_y, bottom_y + 1):
            print(term.move_yx(y, x) + "▮")
        return

    # proportional thumb height
    thumb_height = max(1, round(track_len * (viewport / total)))

    max_scroll = total - viewport
    if max_scroll <= 0:
        thumb_top = top_y
    else:
        thumb_top = top_y + round((track_len - thumb_height) * (scroll / max_scroll))

    thumb_bottom = min(bottom_y, thumb_top + thumb_height - 1)

    # draw thumb (▮)
    for y in range(thumb_top, thumb_bottom + 1):
        print(term.move_yx(y, x) + "▮")

def draw(body: str, page_number: int, offset_inc: int = 0) -> None:
    # Clear
    global total_offset
    print(term.home + term.clear)
    h, w = term.height, term.width

    # header
    header = f"SVT Text  —  {actual_previous_page(page_number)} ◀ {page_number} ▶ {next_actual_page(page_number)}"
    print(term.move_yx(1, 0)
          + term.bold_white_on_blue
          + header.center(max(1, w)).rstrip().ljust(max(1, w))
          + term.normal,
          end="", flush=True)

    # body
    total_offset = total_offset + offset_inc
    usable = max(0, h - 3)
    lines = body.splitlines()
    max_offset = max(0, len(lines) - usable)
    offset = max(0, min(total_offset, max_offset))
    total_offset = offset
    for i in range(min(usable, len(lines))):
        idx = i + offset
        print(term.move_yx(2 + i, 0) + lines[idx])

    #fooder/pad
    print(term.move_yx(h - 1, 0) + term.reverse + " " * max(0, w - 1) + term.normal)
    print(term.move_yx(h - 1, 0) + term.reverse + HELP[: max(0, w - 1)] + term.normal, end="", flush=True)
    _draw_scrollbar(scroll=offset, total=len(lines), viewport=usable, top_y=2, bottom_y=h-2, x=w-2)

def prompt_number(prompt="Go to page: ") -> int:
    h, w = term.height, term.width
    buf = []
    print(term.move_yx(h - 1, 0) + term.normal + " " * max(0, w - 1))
    print(term.move_yx(h - 1, 0) + prompt, end="", flush=True)

    with term.cbreak():
        while True:
            k = term.inkey()
            if not k:
                continue
            if k.name in ("KEY_ENTER",) or k == "\n" or k == "\r":
                return int("".join(buf).strip())
            if k.name in ("KEY_BACKSPACE", "KEY_DELETE") or k == "\x7f":
                if buf:
                    buf.pop()
                    cur = prompt + "".join(buf)
                    print(term.move_yx(h - 1, 0) + " " * max(0, w - 1))
                    print(term.move_yx(h - 1, 0) + cur, end="", flush=True)
                continue
            if k.is_sequence:
                continue
            if len(buf) < 8:
                buf.append(str(k))
                cur = prompt + "".join(buf)
                print(term.move_yx(h - 1, 0) + cur, end="", flush=True)

import traceback


def log_keypress(k):
    try:
        with open(r"C:\Users\RGULLIK1\hobby_projects\py-texttv\keylog.txt", "a", encoding="utf-8") as f:
            f.write(
                f"{datetime.now():%H:%M:%S}  "
                f"name={repr(k.name)}  "
                f"char={repr(str(k))}  "
                f"lower={k.lower()}  "
                f"seq={k.is_sequence}\n"
            )
    except Exception as e:
        with open(r"C:\Users\RGULLIK1\hobby_projects\py-texttv\errorlog.txt", "a", encoding="utf-8") as ef:
            ef.write(f"Logging failed: {e}\n{traceback.format_exc()}\n")



def _search_keyword(query: str, start: int) -> int:
    global latest_search
    latest_search = query
    hits = search_pages(query, start) or []
    return hits[0]

def search_keyword(current_page: int, prompt="Search Keyword: ") -> int | None:
    h, w = term.height, term.width
    buf: list[str] = []

    # clear footer row and show prompt
    print(term.move_yx(h - 1, 0) + term.normal + " " * max(0, w - 1), end="")
    print(term.move_yx(h - 1, 0) + prompt, end="", flush=True)

    with term.cbreak():
        while True:
            k = term.inkey()
            if not k:
                continue

            # submit
            if k.name in ("KEY_ENTER",) or k == "\n" or k == "\r":
                query = "".join(buf).strip()
                if not query:
                    return None
                try:
                    page = _search_keyword(query=query, start=current_page+1)
                except Exception:
                    return None
                return page or None

            # edit
            if k.name in ("KEY_BACKSPACE", "KEY_DELETE") or k == "\x7f":
                if buf:
                    buf.pop()
            elif not k.is_sequence and k.isprintable():
                buf.append(str(k))

            # repaint the input line
            cur = prompt + "".join(buf)
            print(term.move_yx(h - 1, 0) + " " * max(0, w - 1), end="")
            print(term.move_yx(h - 1, 0) + cur[:max(0, w - 1)], end="", flush=True)

def main():
    current_page = 100
    global total_offset
    total_offset = 0
    update_my_pages(100, 101, 1)
    batch_is_fetched = False
    body = render_page_no_bs(current_page)
    with term.fullscreen(), term.hidden_cursor(), term.cbreak():
        draw(body, current_page)
        print(
            term.move_yx(term.height // 2, (term.width // 2) - 5)
            + term.bold
            + "Loading..."
            + term.normal,
            end="",
            flush=True,
        )

        update_my_pages(100, 1000, 50)
        draw(body, current_page)
        while True:
            k = term.inkey()
            if not k:
                continue
            log_keypress(k)

            #quit
            if k.lower() == "q" or k.name == "KEY_ESCAPE":
                break

            # navigation
            if k.name == "KEY_RIGHT":
                total_offset = 0
                current_page = next_actual_page(current_page)
                body = render_page_no_bs(current_page)
                draw(body, current_page)
                continue

            if k.name == "KEY_LEFT":
                total_offset = 0
                current_page = actual_previous_page(current_page)
                body = render_page_no_bs(current_page)
                draw(body, current_page)
                continue

            # goto
            if k.lower() == "g":
                target = prompt_number()
                # restore footer after prompt
                total_offset = 0
                draw(body, current_page)
                if target:
                    current_page = target
                    body = render_page_no_bs(current_page)
                    draw(body, current_page)
                continue

            # goto
            if k.lower() == "s":
                target = search_keyword(current_page = current_page)
                total_offset = 0
                draw(body, current_page)
                if target:
                    current_page = int(target)
                    body = render_page_no_bs(current_page)
                    draw(body, current_page)
                continue

            # quick-nav
            if str(k).isdigit() and 1 <= int(str(k)) <= 9:
                total_offset = 0
                current_page = int(str(k)) * 100
                body = render_page_no_bs(current_page)
                draw(body, current_page)
                continue

            # scroll
            if k.name in ("KEY_DOWN",):
                offset = +1
                draw(body, current_page, offset)
                continue

            if k.name in ("KEY_UP",):
                offset = -1
                draw(body, current_page, offset)
                continue

            # resize handling: blessed emits KEY_RESIZE
            if k.name == "KEY_RESIZE":
                draw(body, current_page)
                continue

if __name__ == "__main__":
    main()

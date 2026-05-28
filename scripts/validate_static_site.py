from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PAGES = [
    ROOT / "index.html",
    ROOT / "pages/project-multicamera.html",
    ROOT / "pages/project-singleview.html",
    ROOT / "pages/tech-stack.html",
]


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[tuple[str, str]] = []
        self.images = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if tag == "img":
            self.images += 1
        for key in ("href", "src"):
            value = values.get(key)
            if value and not value.startswith(("#", "http://", "https://", "mailto:")):
                self.refs.append((key, value))


def main() -> int:
    missing: list[str] = []
    total_images = 0
    suspicious = ("쨌", "\ufffd", "怨")

    for page in PAGES:
        parser = LinkParser()
        text = page.read_text(encoding="utf-8")
        parser.feed(text)
        total_images += parser.images

        for marker in suspicious:
            if marker in text:
                missing.append(f"{page.relative_to(ROOT)} contains suspicious text marker {marker!r}")

        for kind, ref in parser.refs:
            target = (page.parent / ref).resolve()
            if not target.exists():
                missing.append(f"{page.relative_to(ROOT)} {kind} missing: {ref}")

    if total_images < 10:
        missing.append(f"Expected at least 10 images, found {total_images}.")

    if missing:
        print("validation failed")
        for item in missing:
            print(f"- {item}")
        return 1

    print(f"validation passed: {len(PAGES)} pages, {total_images} images")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

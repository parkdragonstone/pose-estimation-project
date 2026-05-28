from __future__ import annotations

import html
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def read_source() -> tuple[Path, str]:
    candidates = sorted(
        p for p in ROOT.glob("*.html") if p.name.lower() not in {"index.html"}
    )
    if not candidates:
        raise FileNotFoundError("No source HTML file found in project root.")
    source = max(candidates, key=lambda p: p.stat().st_size)
    return source, source.read_text(encoding="utf-8")


def extract_between(text: str, start: str, end: str) -> str:
    pattern = re.escape(start) + r"(.*?)" + re.escape(end)
    match = re.search(pattern, text, flags=re.DOTALL | re.IGNORECASE)
    if not match:
        raise ValueError(f"Could not find block between {start!r} and {end!r}.")
    return match.group(1).strip()


def extract_script_blocks(head_prefix: str) -> list[str]:
    return [
        match.group(1).strip()
        for match in re.finditer(r"<script>(.*?)</script>", head_prefix, re.DOTALL)
    ]


def extract_panel(body: str, panel_id: str) -> str:
    marker = f'<div id="{panel_id}" class="tab-content">'
    start = body.find(marker)
    if start < 0:
        raise ValueError(f"Panel {panel_id} was not found.")

    pos = start
    depth = 0
    token_re = re.compile(r"</?div\b[^>]*>", re.IGNORECASE)
    for token in token_re.finditer(body, start):
        tag = token.group(0)
        if tag.startswith("</"):
            depth -= 1
            if depth == 0:
                return body[start : token.end()].strip()
        else:
            depth += 1
        pos = token.end()

    raise ValueError(f"Panel {panel_id} did not close. Last position: {pos}")


def write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def make_nav(active: str, prefix: str = "") -> str:
    items = [
        ("overview", f"{prefix}index.html", "Overview"),
        ("project1", f"{prefix}pages/project-multicamera.html", "Project 1 - Multi-Camera"),
        ("project2", f"{prefix}pages/project-singleview.html", "Project 2 - Single-View"),
        ("tech", f"{prefix}pages/tech-stack.html", "Tech Stack"),
    ]
    links = []
    for key, href, label in items:
        aria = ' aria-current="page"' if key == active else ""
        links.append(f'  <a class="tab-label" href="{href}"{aria}>{html.escape(label)}</a>')
    return '<nav class="tabs" aria-label="Portfolio sections">\n' + "\n".join(links) + "\n</nav>"


def make_page(title: str, active: str, content: str, *, prefix: str = "") -> str:
    css_href = f"{prefix}assets/css/portfolio.css"
    app_src = f"{prefix}assets/js/portfolio.js"
    chart_src = f"{prefix}assets/vendor/chart.umd.js"
    adapter_src = f"{prefix}assets/vendor/chartjs-adapter-date-fns.bundle.min.js"

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'none'; base-uri 'none'; form-action 'none'">
<link rel="stylesheet" href="{css_href}">
<script src="{chart_src}" defer></script>
<script src="{adapter_src}" defer></script>
<script src="{app_src}" defer></script>
</head>
<body>
<header class="header">
  <h1>Portfolio</h1>
  <div class="sub">Computer Vision &amp; Biomechanics Researcher</div>
  <span class="role">3D Human Pose Estimation · Markerless Motion Capture · Inverse Kinematics</span>
</header>

{make_nav(active, prefix)}

<main class="panels">
{content}
</main>
</body>
</html>"""


def main() -> None:
    source_path, text = read_source()

    head_before_meta = text.split("<meta charset", 1)[0]
    scripts = extract_script_blocks(head_before_meta)
    if len(scripts) < 2:
        raise ValueError("Expected two vendor script blocks in the source HTML.")

    css = extract_between(text, "<style>", "</style>")
    body = extract_between(text, "<body>", "</body>")
    app_script = extract_between(body, "<script>", "</script>")

    panels = {
        "overview": extract_panel(body, "p1").replace(
            ' id="p1" class="tab-content"', ' id="overview" class="tab-content active"'
        ),
        "project1": extract_panel(body, "p2").replace(
            ' id="p2" class="tab-content"', ' id="project-multicamera" class="tab-content active"'
        ),
        "project2": extract_panel(body, "p3").replace(
            ' id="p3" class="tab-content"', ' id="project-singleview" class="tab-content active"'
        ),
        "tech": extract_panel(body, "p4").replace(
            ' id="p4" class="tab-content"', ' id="tech-stack" class="tab-content active"'
        ),
    }

    css = re.sub(
        r"\.tab-input \{ display: none; \}\n"
        r"\.tab-input:checked \+ \.tab-label \{\n"
        r"  color: var\(--wrks-viz-primary\);\n"
        r"  border-bottom-color: var\(--wrks-viz-primary\);\n"
        r"\}\n"
        r"\.tab-content \{ display: none; \}\n"
        r"#t1:checked ~ \.panels #p1,\n"
        r"#t2:checked ~ \.panels #p2,\n"
        r"#t3:checked ~ \.panels #p3,\n"
        r"#t4:checked ~ \.panels #p4 \{ display: block; \}",
        ".tab-label { text-decoration: none; }\n"
        ".tab-label[aria-current=\"page\"] {\n"
        "  color: var(--wrks-viz-primary);\n"
        "  border-bottom-color: var(--wrks-viz-primary);\n"
        "}\n"
        ".tab-content { display: block; }",
        css,
    )

    app_script = app_script.replace(
        "document.querySelectorAll('.tab-input').forEach(function(el) {\n"
        "  el.addEventListener('change', function() {\n"
        "    setTimeout(postHeight, 50);\n"
        "  });\n"
        "});",
        "document.querySelectorAll('.tab-label').forEach(function(el) {\n"
        "  el.addEventListener('click', function() {\n"
        "    setTimeout(postHeight, 50);\n"
        "  });\n"
        "});",
    )

    write(ROOT / "assets/vendor/chart.umd.js", scripts[0])
    write(ROOT / "assets/vendor/chartjs-adapter-date-fns.bundle.min.js", scripts[1])
    write(ROOT / "assets/css/portfolio.css", css)
    write(ROOT / "assets/js/portfolio.js", app_script)

    write(ROOT / "index.html", make_page("Portfolio - CV & Biomechanics Researcher", "overview", panels["overview"]))
    write(
        ROOT / "pages/project-multicamera.html",
        make_page("Project 1 - Multi-Camera", "project1", panels["project1"], prefix="../"),
    )
    write(
        ROOT / "pages/project-singleview.html",
        make_page("Project 2 - Single-View", "project2", panels["project2"], prefix="../"),
    )
    write(
        ROOT / "pages/tech-stack.html",
        make_page("Tech Stack", "tech", panels["tech"], prefix="../"),
    )

    print("Refactored source HTML into assets/ and pages/.")


if __name__ == "__main__":
    main()

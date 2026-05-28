from __future__ import annotations

import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}


def text_of(shape: ET.Element) -> str:
    parts = [node.text or "" for node in shape.findall(".//a:t", NS)]
    return " ".join(part.strip() for part in parts if part.strip())


def rels_for(zf: zipfile.ZipFile, rel_path: str) -> dict[str, str]:
    rels: dict[str, str] = {}
    try:
        root = ET.fromstring(zf.read(rel_path))
    except KeyError:
        return rels
    for rel in root.findall("rel:Relationship", NS):
        rid = rel.attrib.get("Id")
        target = rel.attrib.get("Target")
        if rid and target:
            rels[rid] = target
    return rels


def emu_to_in(value: str | None) -> float:
    return int(value or 0) / 914400


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    pptx = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(r"C:\Users\USER\Downloads\portfolio.pptx")
    with zipfile.ZipFile(pptx) as zf:
        media = sorted(name for name in zf.namelist() if name.startswith("ppt/media/"))
        print(f"pptx={pptx}")
        print(f"media={len(media)}")
        for item in media:
            print(f"  {item} size={len(zf.read(item))}")

        presentation = ET.fromstring(zf.read("ppt/presentation.xml"))
        pres_rels = rels_for(zf, "ppt/_rels/presentation.xml.rels")
        slides = []
        for slide_id in presentation.findall(".//p:sldId", NS):
            rid = slide_id.attrib.get(f"{{{NS['r']}}}id")
            target = pres_rels.get(rid or "")
            if target:
                slides.append("ppt/" + target.lstrip("/"))

        print(f"slides={len(slides)}")
        for slide_index, slide_path in enumerate(slides, 1):
            root = ET.fromstring(zf.read(slide_path))
            rel_path = slide_path.replace("ppt/slides/", "ppt/slides/_rels/") + ".rels"
            rels = rels_for(zf, rel_path)
            print(f"\nslide {slide_index}: {slide_path}")
            texts = []
            for sp in root.findall(".//p:sp", NS):
                candidate = text_of(sp)
                if candidate:
                    texts.append(candidate)
            for item in texts[:6]:
                print(f"  text: {item[:180]}")

            for pic in root.findall(".//p:pic", NS):
                name_node = pic.find(".//p:cNvPr", NS)
                blip = pic.find(".//a:blip", NS)
                off = pic.find(".//a:xfrm/a:off", NS)
                ext = pic.find(".//a:xfrm/a:ext", NS)
                rid = blip.attrib.get(f"{{{NS['r']}}}embed") if blip is not None else ""
                target = rels.get(rid, "")
                print(
                    "  pic:"
                    f" name={name_node.attrib.get('name', '') if name_node is not None else ''}"
                    f" target={target}"
                    f" x={emu_to_in(off.attrib.get('x') if off is not None else None):.2f}in"
                    f" y={emu_to_in(off.attrib.get('y') if off is not None else None):.2f}in"
                    f" w={emu_to_in(ext.attrib.get('cx') if ext is not None else None):.2f}in"
                    f" h={emu_to_in(ext.attrib.get('cy') if ext is not None else None):.2f}in"
                )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

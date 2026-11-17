#!/usr/bin/env python3
"""Build image-only and object-editable PPTX files from an agent-authored manifest."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
from io import BytesIO
import json
import math
from pathlib import Path
from lxml import etree as ET
import zipfile

from PIL import Image
from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION
from pptx.enum.shapes import MSO_CONNECTOR, MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.util import Inches, Pt

__author__ = "用户"
SHAPES = {"rect": MSO_SHAPE.RECTANGLE, "roundRect": MSO_SHAPE.ROUNDED_RECTANGLE,
          "ellipse": MSO_SHAPE.OVAL, "triangle": MSO_SHAPE.ISOSCELES_TRIANGLE,
          "rightArrow": MSO_SHAPE.RIGHT_ARROW, "downArrow": MSO_SHAPE.DOWN_ARROW,
          "chevron": MSO_SHAPE.CHEVRON}
CHARTS = {"column": XL_CHART_TYPE.COLUMN_CLUSTERED, "bar": XL_CHART_TYPE.BAR_CLUSTERED,
          "line": XL_CHART_TYPE.LINE, "pie": XL_CHART_TYPE.PIE,
          "doughnut": XL_CHART_TYPE.DOUGHNUT}


def color(value):
    value = str(value).lstrip("#")
    if len(value) != 6:
        raise ValueError(f"Expected a six-digit RGB color: {value}")
    return RGBColor.from_string(value.upper())


def resolve(base, value):
    path = (base / value).resolve()
    if not path.is_file():
        raise FileNotFoundError(path)
    return path


def box(element, canvas):
    result = element.get("box")
    if not isinstance(result, list) or len(result) != 4:
        raise ValueError(f"{element.get('id')}: box must be [x,y,width,height]")
    x, y, w, h = [float(v) for v in result]
    if not all(math.isfinite(v) for v in (x, y, w, h)) or w <= 0 or h <= 0:
        raise ValueError(f"Invalid object box: {result}")
    if x < -.01 or y < -.01 or x + w > canvas[0] + .1 or y + h > canvas[1] + .1:
        raise ValueError(f"{element.get('id')}: object extends outside the canvas")
    return x, y, w, h


def set_fill(fill, value):
    if value is None:
        fill.background()
    else:
        fill.solid()
        fill.fore_color.rgb = color(value)


def style_font(font, specification, points_per_px):
    font.name = specification.get("font", "Microsoft YaHei")
    font.size = Pt(float(specification.get("font_size", 32)) * points_per_px)
    font.bold = bool(specification.get("bold", False))
    font.italic = bool(specification.get("italic", False))
    font.underline = bool(specification.get("underline", False))
    font.color.rgb = color(specification.get("color", "222222"))


def text_frame(frame, element, points_per_px):
    frame.clear()
    frame.word_wrap = bool(element.get("wrap", False))
    frame.auto_size = None
    frame.margin_left = frame.margin_right = frame.margin_top = frame.margin_bottom = 0
    frame.vertical_anchor = {"top": MSO_ANCHOR.TOP, "middle": MSO_ANCHOR.MIDDLE,
                             "bottom": MSO_ANCHOR.BOTTOM}[element.get("vertical_align", "middle")]
    paragraphs = element.get("paragraphs")
    if paragraphs is None:
        paragraphs = [{"text": line} for line in str(element.get("text", "")).split("\n")]
        if element.get("runs"):
            paragraphs = [{"runs": element["runs"]}]
    for index, paragraph in enumerate(paragraphs):
        paragraph = {"text": paragraph} if isinstance(paragraph, str) else paragraph
        p = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        spec = {**element, **paragraph}
        p.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER,
                       "right": PP_ALIGN.RIGHT}[spec.get("align", "left")]
        p.space_before = p.space_after = Pt(0)
        p.line_spacing = float(spec.get("line_spacing", 1.0))
        for run_spec in paragraph.get("runs", [{"text": paragraph.get("text", "")} ]):
            r = p.add_run()
            r.text = str(run_spec["text"])
            style_font(r.font, {**spec, **run_spec}, points_per_px)


def normalize_package_metadata(data):
    source, result = BytesIO(data), BytesIO()
    with zipfile.ZipFile(source) as package, zipfile.ZipFile(result, "w", zipfile.ZIP_DEFLATED) as output:
        for info in package.infolist():
            payload = package.read(info.filename)
            if info.filename == "docProps/core.xml":
                xml = ET.fromstring(payload)
                for name in ["{http://purl.org/dc/elements/1.1/}creator",
                             "{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}lastModifiedBy"]:
                    element = xml.find(name)
                    if element is None:
                        element = ET.SubElement(xml, name)
                    element.text = "用户"
                payload = ET.tostring(xml, encoding="utf-8", xml_declaration=True)
            elif info.filename.startswith("ppt/embeddings/") and info.filename.endswith(".xlsx"):
                payload = normalize_package_metadata(payload)
            output.writestr(info, payload)
    return result.getvalue()


def save(presentation, destination):
    presentation.core_properties.author = "用户"
    presentation.core_properties.last_modified_by = "用户"
    presentation.core_properties.comments = ""
    presentation.core_properties.modified = datetime.now(timezone.utc).replace(tzinfo=None)
    stream = BytesIO()
    presentation.save(stream)
    with destination.open("xb") as output:
        output.write(normalize_package_metadata(stream.getvalue()))


def new_presentation(manifest):
    result = Presentation()
    width, height = manifest["canvas"]
    result.slide_width = Inches(float(manifest.get("width_inches", 13.333333)))
    result.slide_height = int(result.slide_width * height / width)
    result.core_properties.title = manifest.get("title", "Presentation")
    result.core_properties.language = manifest.get("language", "zh-CN")
    return result


def add_picture(slide, path, bounds, convert, fit="contain"):
    x, y, w, h = bounds
    with Image.open(path) as image:
        iw, ih = image.size
    if fit == "contain":
        scale = min(w / iw, h / ih)
        dw, dh = iw * scale, ih * scale
        picture = slide.shapes.add_picture(str(path), convert(x + (w-dw)/2), convert(y + (h-dh)/2), convert(dw), convert(dh))
    elif fit == "cover":
        picture = slide.shapes.add_picture(str(path), convert(x), convert(y), convert(w), convert(h))
        source_ratio, target_ratio = iw / ih, w / h
        if source_ratio > target_ratio:
            picture.crop_left = picture.crop_right = (1 - target_ratio/source_ratio)/2
        else:
            picture.crop_top = picture.crop_bottom = (1 - source_ratio/target_ratio)/2
    else:
        raise ValueError("Image fit must be contain or cover")
    return picture


def add_element(slide, element, manifest, base, convert, points_per_px):
    kind = element["kind"]
    if kind == "line":
        points = element["points"]
        if len(points) < 2 or any(len(p) != 2 for p in points):
            raise ValueError("Line points must be a list of coordinate pairs")
        for index, (start, end) in enumerate(zip(points, points[1:])):
            if any(not (0 <= p[0] <= manifest['canvas'][0] and 0 <= p[1] <= manifest['canvas'][1]) for p in (start, end)):
                raise ValueError("Line points extend outside the canvas")
            shape = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT, convert(start[0]), convert(start[1]), convert(end[0]), convert(end[1]))
            shape.line.color.rgb = color(element.get("color", "222222"))
            shape.line.width = Pt(element.get("line_width", 2) * points_per_px)
            shape.name = f"{element['id']}_{index}"
            if index == len(points)-2 and element.get("end_arrow"):
                arrow = OxmlElement("a:tailEnd")
                arrow.set("type", "triangle")
                shape.line._get_or_add_ln().append(arrow)
        return
    bounds = box(element, manifest["canvas"])
    x, y, w, h = [convert(value) for value in bounds]
    if kind == "text":
        shape = slide.shapes.add_textbox(x, y, w, h)
        text_frame(shape.text_frame, element, points_per_px)
    elif kind == "shape":
        shape = slide.shapes.add_shape(SHAPES[element.get("shape", "rect")], x, y, w, h)
        set_fill(shape.fill, element.get("fill"))
        if element.get("stroke"):
            shape.line.color.rgb = color(element["stroke"])
            shape.line.width = Pt(float(element.get("line_width", 2)) * points_per_px)
        else:
            shape.line.fill.background()
    elif kind == "image":
        shape = add_picture(slide, resolve(base, element["path"]), bounds, convert, element.get("fit", "contain"))
    elif kind == "table":
        rows = element["rows"]
        if not rows or not rows[0] or any(len(row) != len(rows[0]) for row in rows):
            raise ValueError("Table rows must form a non-empty rectangular array")
        shape = slide.shapes.add_table(len(rows), len(rows[0]), x, y, w, h)
        table = shape.table
        for index, width in enumerate(element.get("column_widths", [])):
            table.columns[index].width = convert(width)
        for index, height in enumerate(element.get("row_heights", [])):
            table.rows[index].height = convert(height)
        for merge in element.get("merges", []):
            r, c, rowspan, colspan = merge
            table.cell(r, c).merge(table.cell(r+rowspan-1, c+colspan-1))
        for row_index, row in enumerate(rows):
            for col_index, value in enumerate(row):
                cell = table.cell(row_index, col_index)
                if cell.is_spanned:
                    if value not in ("", None):
                        raise ValueError("Covered merge cells must be empty")
                    continue
                spec = {**element, "text": str(value), "align": element.get("align", "center")}
                if row_index == 0 and element.get("header", True):
                    spec.update({"bold": True, "color": element.get("header_color", "FFFFFF")})
                    set_fill(cell.fill, element.get("header_fill", "17374A"))
                else:
                    set_fill(cell.fill, element.get("fill", "FFFFFF"))
                text_frame(cell.text_frame, spec, points_per_px)
    elif kind == "chart":
        data = CategoryChartData()
        data.categories = element["categories"]
        for series in element["series"]:
            if len(series["values"]) != len(element["categories"]):
                raise ValueError("Each chart series needs one value per category")
            data.add_series(series["name"], series["values"])
        shape = slide.shapes.add_chart(CHARTS[element.get("chart_type", "column")], x, y, w, h, data)
        chart = shape.chart
        chart.has_legend = bool(element.get("legend", len(element["series"]) > 1))
        if chart.has_legend:
            chart.legend.position = XL_LEGEND_POSITION.BOTTOM
        chart.has_title = False
    else:
        raise ValueError(f"Unsupported element kind: {kind}")
    shape.name = element["id"]
    shape.rotation = float(element.get("rotation", 0))


def build(manifest_path, out_dir, mode="both"):
    base = manifest_path.resolve().parent
    manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    manifest.setdefault("canvas", [1920, 1080])
    if len(manifest["canvas"]) != 2 or any(not isinstance(v, (int, float)) or v <= 0 or not math.isfinite(v) for v in manifest["canvas"]):
        raise ValueError("Canvas must contain two positive finite dimensions")
    if not manifest.get("slides"):
        raise ValueError("Manifest needs at least one slide")
    stem = manifest.get("file_stem", "presentation")
    if any(c in stem for c in '/\\:') or stem in ("", ".", ".."):
        raise ValueError("file_stem must be a filename without path separators")
    outputs = {}
    if mode in ("both", "image"):
        outputs["image"] = out_dir / f"{stem}_image.pptx"
    if mode in ("both", "editable"):
        outputs["editable"] = out_dir / f"{stem}_editable.pptx"
    audit_path = out_dir / f"{stem}_audit.json"
    for path in [*outputs.values(), audit_path]:
        if path.exists():
            raise FileExistsError(f"Choose a new output directory or stem: {path}")
    presentations = {name: new_presentation(manifest) for name in outputs}
    audit = {"author": "用户", "canvas": manifest["canvas"], "slides": [], "files": {}}
    for index, source in enumerate(manifest["slides"], 1):
        image = resolve(base, source["image"])
        with Image.open(image) as raster:
            source_size = raster.size
        if abs(source_size[0]/source_size[1] / (manifest['canvas'][0]/manifest['canvas'][1])-1) > .01:
            raise ValueError(f"Slide {index}: final image and canvas aspect ratios differ")
        objects = source.get("elements", [])
        if "editable" in presentations and not objects:
            raise ValueError(f"Slide {index}: editable output requires explicit native/image objects")
        identifiers = [element["id"] for element in objects]
        if len(set(identifiers)) != len(identifiers):
            raise ValueError(f"Slide {index}: object IDs must be unique")
        for name, presentation in presentations.items():
            slide = presentation.slides.add_slide(presentation.slide_layouts[6])
            scale = presentation.slide_width / manifest["canvas"][0]
            convert = lambda value: round(float(value) * scale)
            points_per_px = scale / 12700
            if name == "image":
                add_picture(slide, image, [0, 0, *manifest["canvas"]], convert, "contain").name = f"slide_{index:03d}"
            else:
                background = source.get("background", {"color": "FFFFFF"})
                if background.get("image"):
                    bg = resolve(base, background["image"])
                    if bg == image or background.get("text_free") is not True:
                        raise ValueError("Editable backgrounds need a separate text-free image and text_free=true")
                    add_picture(slide, bg, [0, 0, *manifest["canvas"]], convert, "cover").name = "background"
                else:
                    set_fill(slide.background.fill, background.get("color", "FFFFFF"))
                for _, element in sorted(enumerate(objects), key=lambda pair: (pair[1].get("z", 0), pair[0])):
                    add_element(slide, element, manifest, base, convert, points_per_px)
            slide.notes_slide.notes_text_frame.text = source.get("notes", "")
        audit['slides'].append({"slide": index, "title": source.get("title", ""), "source_px": list(source_size),
                                "elements": dict(Counter(e['kind'] for e in objects)), "notes": source.get('notes', '')})
    out_dir.mkdir(parents=True, exist_ok=True)
    for name, presentation in presentations.items():
        save(presentation, outputs[name])
        audit['files'][name] = {"path": str(outputs[name].resolve()), "sha256": hashlib.sha256(outputs[name].read_bytes()).hexdigest()}
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    return audit


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--mode", choices=["both", "image", "editable"], default="both")
    args = parser.parse_args()
    result = build(args.manifest, args.out_dir, args.mode)
    print(json.dumps({"author": "用户", "slides": len(result['slides']), "files": result['files']}, ensure_ascii=False))


if __name__ == "__main__":
    main()

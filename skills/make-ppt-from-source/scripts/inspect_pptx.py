#!/usr/bin/env python3
"""Inspect object types, embedded media and identity metadata in a PPTX file."""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
from io import BytesIO
import json
from pathlib import Path
from xml.etree import ElementTree as ET
import zipfile
from PIL import Image
from pptx import Presentation

__author__ = "用户"


def inspect(path):
    presentation = Presentation(path)
    result = {"author": "用户", "path": str(path.resolve()), "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
              "metadata": {"author": presentation.core_properties.author,
                           "last_modified_by": presentation.core_properties.last_modified_by},
              "slides": [], "media": [], "embedded_workbooks": []}
    for index, slide in enumerate(presentation.slides, 1):
        counts = Counter()
        for shape in slide.shapes:
            kind = "table" if shape.has_table else "chart" if shape.has_chart else "image" if int(shape.shape_type) == 13 else "text" if shape.has_text_frame and shape.text else "shape"
            counts[kind] += 1
        result['slides'].append({"slide": index, "objects": dict(counts),
                                 "text": [shape.text for shape in slide.shapes if shape.has_text_frame and shape.text],
                                 "notes": slide.notes_slide.notes_text_frame.text})
    with zipfile.ZipFile(path) as package:
        for name in package.namelist():
            if name.startswith('ppt/media/'):
                payload = package.read(name)
                try:
                    with Image.open(BytesIO(payload)) as image:
                        pixels = list(image.size)
                except Exception:
                    pixels = None
                result['media'].append({"file": name, "native_px": pixels, "sha256": hashlib.sha256(payload).hexdigest()})
            elif name.startswith('ppt/embeddings/') and name.endswith('.xlsx'):
                with zipfile.ZipFile(BytesIO(package.read(name))) as workbook:
                    core = ET.fromstring(workbook.read('docProps/core.xml'))
                    creator = core.find('{http://purl.org/dc/elements/1.1/}creator')
                    modifier = core.find('{http://schemas.openxmlformats.org/package/2006/metadata/core-properties}lastModifiedBy')
                    result['embedded_workbooks'].append({"file": name, "author": creator.text, "last_modified_by": modifier.text})
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pptx', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = inspect(args.pptx)
    data = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        with args.out.open('x', encoding='utf-8') as output:
            output.write(data)
    print(data)


if __name__ == '__main__':
    main()

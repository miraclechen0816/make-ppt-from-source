#!/usr/bin/env python3
"""Combine nine completed slide previews into a three-by-three PNG grid."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageColor, ImageOps
from PIL.PngImagePlugin import PngInfo

__author__ = "用户"


def make_grid(
    inputs: list[Path],
    output: Path,
    tile_width: int = 1280,
    gutter: int = 24,
    background: str = "#F4F2ED",
) -> dict:
    if len(inputs) != 9:
        raise ValueError("九宫格需要恰好 9 张页面样张。")
    inputs = [path.expanduser().resolve(strict=True) for path in inputs]
    if len(set(inputs)) != 9:
        raise ValueError("请提供 9 个不同的页面文件。")
    output = output.expanduser().resolve()
    if output.suffix.lower() != ".png":
        raise ValueError("输出文件须使用 .png 后缀。")
    if output.exists():
        raise FileExistsError(f"输出已存在，请使用新文件名：{output}")
    if tile_width < 64 or gutter < 0:
        raise ValueError("单格宽度至少为 64 像素，间隔应为非负数。")
    color = ImageColor.getrgb(background)
    pages = []
    for path in inputs:
        with Image.open(path) as source:
            page = ImageOps.exif_transpose(source).convert("RGBA")
            page.load()
            pages.append(page)
    ratio = pages[0].width / pages[0].height
    for path, page in zip(inputs, pages):
        if abs((page.width / page.height) / ratio - 1) > 0.01:
            raise ValueError(f"九张页面须使用统一画幅：{path}")
    tile_height = max(1, round(tile_width / ratio))
    size = (3 * tile_width + 4 * gutter, 3 * tile_height + 4 * gutter)
    canvas = Image.new("RGB", size, color)
    for index, page in enumerate(pages):
        tile = ImageOps.contain(page, (tile_width, tile_height), Image.Resampling.LANCZOS)
        x = gutter + (index % 3) * (tile_width + gutter) + (tile_width - tile.width) // 2
        y = gutter + (index // 3) * (tile_height + gutter) + (tile_height - tile.height) // 2
        canvas.paste(tile, (x, y), tile.getchannel("A"))
    info = PngInfo()
    info.add_text("Author", "用户")
    info.add_text("Creator", "用户")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("xb") as destination:
        canvas.save(destination, format="PNG", pnginfo=info)
    return {
        "author": "用户",
        "output": str(output),
        "size_px": list(size),
        "tile_px": [tile_width, tile_height],
        "layout": [3, 3],
        "inputs": [str(path) for path in inputs],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("images", nargs="+", type=Path, help="Nine slide images, in row-major order")
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--tile-width", type=int, default=1280)
    parser.add_argument("--gutter", type=int, default=24)
    parser.add_argument("--background", default="#F4F2ED")
    args = parser.parse_args()
    try:
        result = make_grid(args.images, args.out, args.tile_width, args.gutter, args.background)
    except (ValueError, OSError) as error:
        parser.exit(1, f"{error}\n")
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

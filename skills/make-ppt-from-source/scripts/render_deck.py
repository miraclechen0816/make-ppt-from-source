#!/usr/bin/env python3
"""Render a PPTX using installed PowerPoint or LibreOffice, preserving work files."""
import argparse
from pathlib import Path
import json
import os
import shutil
import subprocess
from PIL import Image
from PIL.PngImagePlugin import PngInfo

__author__ = "用户"


def render(source, destination, width=1920):
    from pptx import Presentation
    source, destination = source.resolve(), destination.resolve()
    if destination.exists():
        raise FileExistsError('Choose a new render directory')
    presentation = Presentation(source)
    height = round(width * presentation.slide_height / presentation.slide_width)
    if os.name == 'nt':
        powershell = shutil.which('powershell.exe') or shutil.which('pwsh.exe')
        if not powershell:
            raise RuntimeError('PowerShell is unavailable')
        subprocess.run([powershell, '-NoProfile', '-NonInteractive', '-ExecutionPolicy', 'Bypass', '-File',
                        str(Path(__file__).with_name('render_powerpoint.ps1')), str(source), str(destination), str(width), str(height)], check=True)
        backend = 'PowerPoint'
    else:
        office = shutil.which('soffice') or shutil.which('libreoffice')
        if not office:
            raise RuntimeError('Install LibreOffice to render PPTX on this platform')
        import fitz
        destination.mkdir(parents=True)
        work = destination / 'office-work'
        work.mkdir()
        profile = work / 'profile'
        subprocess.run([office, f'-env:UserInstallation={profile.as_uri()}', '--headless', '--convert-to', 'pdf',
                        '--outdir', str(work), str(source)], check=True)
        with fitz.open(work / (source.stem + '.pdf')) as document:
            for index, page in enumerate(document, 1):
                page.get_pixmap(matrix=fitz.Matrix(width/page.rect.width, height/page.rect.height), alpha=False).save(destination / f'slide_{index:03d}.png')
        backend = 'LibreOffice'
    files = sorted(destination.glob('slide_*.png'))
    if len(files) != len(presentation.slides):
        raise RuntimeError('Rendered page count differs from the PPTX')
    for path in files:
        with Image.open(path) as source_image:
            image = source_image.copy()
        metadata = PngInfo()
        metadata.add_text('Author', '用户')
        metadata.add_text('Creator', '用户')
        image.save(path, pnginfo=metadata)
    result = {'author': '用户', 'renderer': backend, 'source': str(source), 'pages': len(files), 'size_px': [width, height], 'output': str(destination)}
    (destination / 'render_report.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('pptx', type=Path)
    parser.add_argument('--out', required=True, type=Path)
    parser.add_argument('--width', type=int, default=1920)
    arguments = parser.parse_args()
    print(json.dumps(render(arguments.pptx, arguments.out, arguments.width), ensure_ascii=False))

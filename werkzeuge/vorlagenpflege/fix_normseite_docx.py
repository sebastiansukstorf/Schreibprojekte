#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
ET.register_namespace('w', NS['w'])

TEMPLATE_STYLE_IDS = ['Standard', 'Textkrper']


def ensure_space(elem, tag, attrs):
    child = elem.find(f'w:{tag}', NS)
    if child is None:
        child = ET.SubElement(elem, f'{{{NS["w"]}}}{tag}')
    for key, value in attrs.items():
        child.attrib[f'{{{NS["w"]}}}{key}'] = value
    return child


def normalize_style(style):
    pPr = style.find('w:pPr', NS)
    if pPr is None:
        pPr = ET.SubElement(style, '{%s}pPr' % NS['w'])
    ensure_space(pPr, 'spacing', {
        'after': '0',
        'line': '485',
        'lineRule': 'exact',
    })
    rPr = style.find('w:rPr', NS)
    if rPr is None:
        rPr = ET.SubElement(style, '{%s}rPr' % NS['w'])
    fonts = ensure_space(rPr, 'rFonts', {
        'ascii': 'Courier New',
        'hAnsi': 'Courier New',
    })
    ensure_space(rPr, 'sz', {'val': '24'})
    ensure_space(rPr, 'szCs', {'val': '24'})


def rewrite_styles_xml(styles_xml: bytes) -> bytes:
    root = ET.fromstring(styles_xml)
    for style_id in TEMPLATE_STYLE_IDS:
        xpath = f".//w:style[@w:styleId='{style_id}']"
        style = root.find(xpath, NS)
        if style is not None:
            normalize_style(style)
    return ET.tostring(root, encoding='utf-8', xml_declaration=True)


def rewrite_docx(path: Path) -> None:
    with ZipFile(path, 'r') as zin:
        entries = {name: zin.read(name) for name in zin.namelist() if name != 'word/styles.xml'}
        styles_xml = zin.read('word/styles.xml')

    fixed_styles = rewrite_styles_xml(styles_xml)

    tmp_path = path.with_suffix('.tmp.docx')
    with ZipFile(tmp_path, 'w', ZIP_DEFLATED) as zout:
        for name, data in entries.items():
            zout.writestr(name, data)
        zout.writestr('word/styles.xml', fixed_styles)

    tmp_path.replace(path)


if __name__ == '__main__':
    import sys

    if len(sys.argv) != 2:
        print('Usage: fix_normseite_docx.py <path/to/docx>')
        raise SystemExit(1)

    target = Path(sys.argv[1])
    if not target.exists():
        print('File not found:', target)
        raise SystemExit(1)

    rewrite_docx(target)

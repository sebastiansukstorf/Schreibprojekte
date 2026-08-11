#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
ET.register_namespace('w', NS['w'])

TEMPLATE = Path('ressourcen/Normseite.docx')
SPACING_AFTER = '720'  # Twips

if not TEMPLATE.exists():
    raise SystemExit('Template not found: ' + str(TEMPLATE))

with ZipFile(TEMPLATE, 'r') as zin:
    entries = {name: zin.read(name) for name in zin.namelist() if name != 'word/styles.xml'}
    styles_xml = zin.read('word/styles.xml')

root = ET.fromstring(styles_xml)
changed = False
for style in root.findall('.//w:style', NS):
    sid = style.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId')
    if sid == 'berschrift1':
        pPr = style.find('w:pPr', NS)
        if pPr is None:
            pPr = ET.SubElement(style, '{%s}pPr' % NS['w'])
        spacing = pPr.find('w:spacing', NS)
        if spacing is None:
            spacing = ET.SubElement(pPr, '{%s}spacing' % NS['w'])
        spacing.attrib['{%s}after' % NS['w']] = SPACING_AFTER
        changed = True
        break

if not changed:
    print('Style "berschrift1" not found; no change made.')
else:
    new_styles = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    tmp = TEMPLATE.with_suffix('.tmp.docx')
    with ZipFile(tmp, 'w', ZIP_DEFLATED) as zout:
        for name, data in entries.items():
            zout.writestr(name, data)
        zout.writestr('word/styles.xml', new_styles)
    tmp.replace(TEMPLATE)
    print('Updated "berschrift1" spacing to', SPACING_AFTER, 'Twips in', TEMPLATE)

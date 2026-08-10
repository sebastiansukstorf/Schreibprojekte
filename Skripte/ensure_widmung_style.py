#!/usr/bin/env python3
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import xml.etree.ElementTree as ET

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
ET.register_namespace('w', NS['w'])

TEMPLATE = Path('Vorlage/Normseite.docx')
STYLE_ID = 'Widmung'
STYLE_NAME = 'Widmung'

if not TEMPLATE.exists():
    raise SystemExit('Template not found: ' + str(TEMPLATE))

with ZipFile(TEMPLATE, 'r') as zin:
    entries = {name: zin.read(name) for name in zin.namelist() if name != 'word/styles.xml'}
    styles_xml = zin.read('word/styles.xml')

root = ET.fromstring(styles_xml)
found = None
for style in root.findall('.//w:style', NS):
    sid = style.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}styleId')
    name_el = style.find('w:name', NS)
    name = name_el.attrib.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val') if name_el is not None else ''
    if sid == STYLE_ID or name == STYLE_NAME:
        found = style
        break

if found is None:
    # create a new paragraph style
    style = ET.Element('{%s}style' % NS['w'], {
        '{%s}type' % NS['w']: 'paragraph',
        '{%s}styleId' % NS['w']: STYLE_ID
    })
    name_el = ET.SubElement(style, '{%s}name' % NS['w'])
    name_el.attrib['{%s}val' % NS['w']] = STYLE_NAME
    # make it qFormat so it appears in the UI
    ET.SubElement(style, '{%s}qFormat' % NS['w'])
    # pPr with pageBreakBefore
    pPr = ET.SubElement(style, '{%s}pPr' % NS['w'])
    ET.SubElement(pPr, '{%s}pageBreakBefore' % NS['w'])
    # left alignment (linksbündig)
    jc = ET.SubElement(pPr, '{%s}jc' % NS['w'])
    jc.attrib['{%s}val' % NS['w']] = 'left'
    # spacing: some after
    spacing = ET.SubElement(pPr, '{%s}spacing' % NS['w'])
    spacing.attrib['{%s}after' % NS['w']] = '240'
    spacing.attrib['{%s}before' % NS['w']] = '1440'
    # rPr: set font to match Standard (Courier New 12pt)
    rPr = ET.SubElement(style, '{%s}rPr' % NS['w'])
    rFonts = ET.SubElement(rPr, '{%s}rFonts' % NS['w'])
    rFonts.attrib['{%s}ascii' % NS['w']] = 'Courier New'
    rFonts.attrib['{%s}hAnsi' % NS['w']] = 'Courier New'
    sz = ET.SubElement(rPr, '{%s}sz' % NS['w'])
    sz.attrib['{%s}val' % NS['w']] = '24'
    root.append(style)
    changed = True
else:
    # ensure pageBreakBefore exists
    pPr = found.find('w:pPr', NS)
    if pPr is None:
        pPr = ET.SubElement(found, '{%s}pPr' % NS['w'])
    # ensure pageBreakBefore
    if pPr.find('w:pageBreakBefore', NS) is None:
        ET.SubElement(pPr, '{%s}pageBreakBefore' % NS['w'])
        changed = True
    else:
        changed = False
    # ensure left alignment
    jc = pPr.find('w:jc', NS)
    if jc is None:
        jc = ET.SubElement(pPr, '{%s}jc' % NS['w'])
        jc.attrib['{%s}val' % NS['w']] = 'left'
        changed = True
    else:
        if jc.attrib.get('{%s}val' % NS['w']) != 'left':
            jc.attrib['{%s}val' % NS['w']] = 'left'
            changed = True
    # ensure spacing after
    spacing = pPr.find('w:spacing', NS)
    if spacing is None:
        spacing = ET.SubElement(pPr, '{%s}spacing' % NS['w'])
        spacing.attrib['{%s}after' % NS['w']] = '240'
        spacing.attrib['{%s}before' % NS['w']] = '1440'
        changed = True
    else:
        if spacing.attrib.get('{%s}after' % NS['w']) != '240':
            spacing.attrib['{%s}after' % NS['w']] = '240'
            changed = True
        if spacing.attrib.get('{%s}before' % NS['w']) != '1440':
            spacing.attrib['{%s}before' % NS['w']] = '1440'
            changed = True
    # ensure rPr has font and size matching Standard
    rPr = found.find('w:rPr', NS)
    if rPr is None:
        rPr = ET.SubElement(found, '{%s}rPr' % NS['w'])
        changed = True
    rf = rPr.find('w:rFonts', NS)
    if rf is None:
        rf = ET.SubElement(rPr, '{%s}rFonts' % NS['w'])
        rf.attrib['{%s}ascii' % NS['w']] = 'Courier New'
        rf.attrib['{%s}hAnsi' % NS['w']] = 'Courier New'
        changed = True
    else:
        updated = False
        if rf.attrib.get('{%s}ascii' % NS['w']) != 'Courier New':
            rf.attrib['{%s}ascii' % NS['w']] = 'Courier New'
            updated = True
        if rf.attrib.get('{%s}hAnsi' % NS['w']) != 'Courier New':
            rf.attrib['{%s}hAnsi' % NS['w']] = 'Courier New'
            updated = True
        if updated:
            changed = True
    sz = rPr.find('w:sz', NS)
    if sz is None:
        sz = ET.SubElement(rPr, '{%s}sz' % NS['w'])
        sz.attrib['{%s}val' % NS['w']] = '24'
        changed = True
    else:
        if sz.attrib.get('{%s}val' % NS['w']) != '24':
            sz.attrib['{%s}val' % NS['w']] = '24'
            changed = True

if changed:
    new_styles = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    tmp = TEMPLATE.with_suffix('.tmp.docx')
    with ZipFile(tmp, 'w', ZIP_DEFLATED) as zout:
        for name, data in entries.items():
            zout.writestr(name, data)
        zout.writestr('word/styles.xml', new_styles)
    tmp.replace(TEMPLATE)
    print('Added/updated style', STYLE_ID, 'in', TEMPLATE)
else:
    print('No changes needed; style exists with pageBreakBefore')

#!/usr/bin/env python3
from pandocfilters import toJSONFilter, RawBlock, Header

def add_pagebreaks(key, value, format, meta):
    if key == "Header":
        level, _, _ = value
        if level == 1 and format == "docx":
            return [RawBlock("openxml", "<w:p><w:r><w:br w:type=\"page\"/></w:r></w:p>"), Header(*value)]

if __name__ == "__main__":
    toJSONFilter(add_pagebreaks)

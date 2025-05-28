#!/usr/bin/env lua
function RawBlock(el)
  if el.format == "markdown" then
    local lines = {}
    for line in el.text:gmatch("[^\r\n]+") do
      if line:match("%S") then
        table.insert(lines, pandoc.Para({pandoc.Str(line)}))
      else
        table.insert(lines, pandoc.Para({}))  -- Leerer Absatz für Leerzeile
      end
    end
    return lines
  end
end


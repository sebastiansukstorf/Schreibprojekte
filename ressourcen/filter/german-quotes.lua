-- Normalisiere Anführungszeichen ausschließlich im Pandoc-Ausgabebaum.
-- Die Markdown-Quelldateien werden nicht verändert.

local function wrapped(opening, content, closing)
  local result = { pandoc.Str(opening) }
  for _, inline in ipairs(content) do
    table.insert(result, inline)
  end
  table.insert(result, pandoc.Str(closing))
  return result
end

function Quoted(element)
  if element.quotetype == "DoubleQuote" then
    return wrapped("„", element.content, "“")
  end
  return wrapped("‚", element.content, "‘")
end

function Str(element)
  local text = element.text:gsub("”", "“")
  if text:sub(1, #"“") == "“" then
    text = "„" .. text:sub(#"“" + 1)
  end
  element.text = text
  return element
end

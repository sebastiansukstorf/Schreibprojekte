-- Fügt sichtbare Leerzeilen ein (DOCX-kompatibel),
-- wenn im Markdown zwei Zeilenumbrüche oder [[BLANKLINE]] / <br><br> stehen.

local function visible_blank_para()
  return pandoc.Para({ pandoc.Str("\u{00A0}") }) -- NBSP für sichtbaren Absatz
end

local function para_is_blank_marker(inlines)
  if #inlines == 1 then
    local el = inlines[1]
    if el.t == "RawInline" and el.format == "html" and el.text:match("<br>") then
      return true
    end
    if el.t == "Str" and el.text == "[[BLANKLINE]]" then
      return true
    end
  end
  return false
end

function Para(p)
  if para_is_blank_marker(p.content) then
    return visible_blank_para()
  end

  -- Zwei harte Zeilenumbrüche innerhalb eines Absatzes -> sichtbare Leerzeile
  local out_blocks, cur, lb_count, used = {}, pandoc.List(), 0, false
  for _, inline in ipairs(p.content) do
    if inline.t == "LineBreak" then
      lb_count = lb_count + 1
      if lb_count == 2 then
        table.insert(out_blocks, pandoc.Para(cur))
        table.insert(out_blocks, visible_blank_para())
        cur, lb_count, used = pandoc.List(), 0, true
      else
        table.insert(cur, inline)
      end
    else
      lb_count = 0
      table.insert(cur, inline)
    end
  end
  if used then
    if #cur > 0 then table.insert(out_blocks, pandoc.Para(cur)) end
    return out_blocks
  end
  return nil
end

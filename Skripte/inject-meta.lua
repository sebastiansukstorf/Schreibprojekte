function replace_placeholders(el)
  if el.t == "Str" and el.text:match("{{(.-)}}") then
    local key = el.text:match("{{(.-)}}")
    local value = PANDOC_META[key]
    if value then
      return pandoc.Str(pandoc.utils.stringify(value))
    else
      return el  -- wenn kein Wert vorhanden, nicht ersetzen
    end
  end
end

return {
  {
    Str = replace_placeholders
  }
}

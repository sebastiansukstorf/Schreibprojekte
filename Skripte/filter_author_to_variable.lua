function Meta(meta)
  if meta.author then
    meta.author_in_text = meta.author  -- neue Variable, die Pandoc ersetzt
    meta.author = nil                  -- entfernt die Standarddarstellung im Text
  end
  return meta
end

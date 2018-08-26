if exists("b:current_syntax")
    finish
endif

syntax keyword cardType Artifact Creature Enchantment Instant Land Planeswalker Sorcery Tribal
highlight link cardType Keyword

syntax match cardSymbol "{.*}"
highlight link cardSymbol Comment

let b:current_syntax = "vimscry"

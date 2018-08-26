if exists("b:current_syntax")
    finish
endif

syntax keyword cardType Artifact Creature Enchantment Instant Land Planeswalker Sorcery Tribal
highlight link cardType Keyword

syntax match cardSymbol "{[A-Z0-9/]\+}"
highlight link cardSymbol Comment

" RDoc inline links:           protocol   optional  user:pass@       sub/domain                 .com, .co.uk, etc      optional port   path/querystring/hash fragment
"                            ------------ _____________________ --------------------------- ________________________ ----------------- __
syntax match rdocInlineURL /https\?:\/\/\(\w\+\(:\w\+\)\?@\)\?\([A-Za-z][-_0-9A-Za-z]*\.\)\{1,}\(\w\{2,}\.\?\)\{1,}\(:[0-9]\{1,5}\)\?\S*/
highlight link rdocInlineURL String

let b:current_syntax = "vimscry"

setlocal foldmethod=expr
setlocal foldexpr=GetVimScryFold(v:lnum)
hi Folded ctermbg=226

function! GetVimScryFold(lnum)
    if getline(a:lnum) =~? '\v^ \| '
        return '1'
    endif

    if getline(a:lnum + 1) =~? '\v^ \| '
        return '>1'
    endif

    return '0'
endfunction

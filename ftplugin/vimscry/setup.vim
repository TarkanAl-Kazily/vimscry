setlocal buftype=nofile
setlocal bufhidden=hide
setlocal noswapfile

nnoremap <buffer> <cr> :call OpenCardUrl()<cr>
vnoremap <buffer> y :call CopyCardName()<cr>
noremap <buffer> Y :call CopyCardName()<cr>
noremap <buffer> <tab> :call AddCard()<cr>

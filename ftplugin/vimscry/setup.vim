setlocal buftype=nofile
setlocal bufhidden=hide
setlocal noswapfile

nnoremap <buffer> <cr> :call OpenCardUrl()<cr>
nnoremap <buffer> Y :call CopyCardName()<cr>

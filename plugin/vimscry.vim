if !has("python3")
    echo "vim has to be compiled with +python3 to run this"
    finish
endif

if exists('g:vimscry')
    finish
endif

let s:plugin_root_dir = fnamemodify(resolve(expand('<sfile>:p')), ':h')

python3 << EOF
import sys
from os.path import normpath, join
import vim
plugin_root_dir = vim.eval('s:plugin_root_dir')
python_root_dir = normpath(join(plugin_root_dir, '..', 'python'))
sys.path.insert(0, python_root_dir)
import vimscry
EOF

function! RandomCard()
    python3 vimscry.scry.random_card()
endfunction

function! Scry(query)
    python3 vimscry.scry.scry()
endfunction

function! OpenCardUrl()
    python3 vimscry.scry.open_card_url()
endfunction

function! CopyCardName() range
    python3 vimscry.scry.copy_card_names()
endfunction

function! AddCard() range
    python3 vimscry.scry.copy_card_names()
    wincmd w
    normal! G
    normal! p
    wincmd w
endfunction

command! -nargs=0 RandomCard call RandomCard()
command! -nargs=0 InsertRandomCard call InsertRandomCard()
command! -nargs=1 Scry call Scry(<q-args>)
let g:vimscry = 1

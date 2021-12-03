nnoremap <silent> <leader>\ :vs term://zsh<CR>
nnoremap <silent> <leader>- :sp term://zsh<CR>
nnoremap <silent> <leader>_ :sp term://zsh<CR>
if has('nvim')
  tnoremap <Esc> <C-\><C-n>
  tnoremap <M-[> <Esc>
  tnoremap <C-v><Esc> <Esc>
endif


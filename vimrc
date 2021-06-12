" ######  BAIC CONFIG 
set number 		" show line number
set wildmenu		" better command line completion 
set ruler		" display cursor position
set nocompatible	" must have
set showcmd		" show partial commands in the last line
set hlsearch 		" highlight search
set ignorecase 		" search ignore case
set smartcase
syntax on		" syntax highlight
set autoindent 		" Auto indent
set smartindent		
set sw=4		" indent size = 4 
set tabstop=4
set expandtab
set backspace=indent,eol,start
set splitbelow
set splitright
" ##### Plugin Manager
if &compatible
      set nocompatible               " Be iMproved
endif
if (empty($TMUX))
  if (has("nvim"))
    let $NVIM_TUI_ENABLE_TRUE_COLOR=1
  endif
  if (has("termguicolors"))
    set termguicolors
  endif
endif

let s:dein_path = join([$HOME, has('nvim') ? '.nvim': '.vim'], '/')
" Required:
"set runtimepath+=/Users/alexzhang/.vim/bundles/repos/github.com/Shougo/dein.vim
let &runtimepath .= ','.expand(join([s:dein_path,'/bundles/repos/github.com/Shougo/dein.vim'], ''))
" Required:
call dein#begin(join([s:dein_path, '/bundles'], ''))
" Let dein manage dein
" Required:
    call dein#add('Shug/dein.vim')
    call dein#add('preservim/nerdtree')
    call dein#add('Shougo/denite.nvim')
    call dein#add('vim-airline/vim-airline')
    call dein#add('liuchengxu/vim-which-key', {'on_cmd': ['WhichKey', 'WhichKey!']}) 
    call dein#add('neoclide/coc.nvim', {'on_if': 'has("nvim")', 'rev': 'release'})
    call dein#add('joshdick/onedark.vim')
    if !has('nvim')
          call dein#add('roxma/nvim-yarp')
          call dein#add('roxma/vim-hug-neovim-rpc')
    endif
" Required:
    call dein#config('preservim/nerdtree',  { 
    \    'on_cmd': ['NERDTreeToggle',
    \       'NERDTreeCWD'
    \    ]
    \}) 
call dein#end()

" Required:
filetype plugin indent on
syntax enable
colorscheme onedark

"##### Plugin settings 

" <<<<< AIR-LINE 
let g:airline#extensions#tabline#enabled = 1
let g:airline#extensions#tabline#buffer_nr_show = 1
let g:airline_powerline_fonts = 1

" <<<<< NERDTREE
let g:NERDTreeWinPos = "right"

" <<<<< WHICH-KEY
let g:which_key_map={}
let g:which_key_map.f = {
    \ 'name': '+File',
    \ 't': [':NERDTreeToggle<CR>', 'Toggle File Manager'] ,
    \ }

"###### Key Mapping
" NERD TREE
nnoremap <Space>ft :NERDTreeToggle<CR>
" <<<<< Which Key
nnoremap <silent><Space> :WhichKey '<Space>'<CR>
" <<<<< Denite
autocmd FileType denite call s:denite_my_settings()
function! s:denite_my_settings() abort
    nnoremap <silent><buffer><expr> <CR>
    \ denite#do_map('do_action')
    nnoremap <silent><buffer><expr> d
    \ denite#do_map('do_action', 'delete')
    nnoremap <silent><buffer><expr> p
    \ denite#do_map('do_action', 'preview')
    nnoremap <silent><buffer><expr> q
    \ denite#do_map('quit')
    nnoremap <silent><buffer><expr> i
    \ denite#do_map('open_filter_buffer')
    nnoremap <silent><buffer><expr> <Space>
    \ denite#do_map('toggle_select').'j'
endfunction
" <<<<< MISC
nnoremap <silent><leader>1 :buffer 1 <CR>
nnoremap <silent><leader>2 :buffer 2 <CR>
nnoremap <silent><leader>3 :buffer 3 <CR>
nnoremap <silent><leader>4 :buffer 4 <CR>
nnoremap <silent><leader>5 :buffer 5 <CR>
nnoremap <silent><leader>6 :buffer 6 <CR>
nnoremap <silent><leader>7 :buffer 7 <CR>
nnoremap <silent><leader>8 :buffer 8 <CR>
nnoremap <silent><leader>9 :buffer 9 <CR>

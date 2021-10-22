" ############################
" #                          # 
" #      COMMOM SETTINGS     #
" #                          #
" ############################ 
set number 		    " show line number
set wildmenu		" better command line completion 
set ruler		    " display cursor position
set nocompatible	" must have
set showcmd		    " show partial commands in the last line
set hlsearch 		" highlight search
set ignorecase 		" search ignore case
set smartcase
syntax on		    " syntax highlight
set autoindent 		" Auto indent
set smartindent		
set sw=4		    " indent size = 4 
set tabstop=4
set expandtab
set backspace=indent,eol,start
set splitbelow
set splitright
set hidden
set nobackup
set nowritebackup
set updatetime=300
set stal=2          " Always show tabline
set laststatus=2
set termguicolors
if has('nvim')
  set noshowmode
endif 
" Always show signcolumn
if has("nvim-0.5.0") || has("patch-8.1.1564")
  set signcolumn=number
else
  set signcolumn=yes
endif


" ###################
" #                 #
" #     PLUGINS     #
" #                 # 
" ################### 
call plug#begin(has('nvim') ? stdpath('data') . '/plugged' : '~/.vim/plugged')
    Plug 'sheerun/vim-polyglot'                                 " Syntax Highlight
    Plug 'itchyny/lightline.vim'                                " Status Line
    Plug 'neoclide/coc.nvim', { 'branch': 'release',
      \ 'do': ':CocInstall coc-json  coc-tsserver coc-pyright'
      \ }           " Auto Complete
    " file tree
    if has('nvim')
      Plug 'Shougo/defx.nvim', { 'do': ':UpdateRemotePlugins' }
      Plug 'akinsho/bufferline.nvim' 
    else
      Plug 'Shougo/defx.nvim'
      Plug 'roxma/nvim-yarp'
      Plug 'roxma/vim-hug-neovim-rpc'
    endif
    Plug 'kristijanhusak/defx-icons'
    Plug 'ryanoasis/vim-devicons'
    Plug 'joshdick/onedark.vim'                                 " OneDark colorscheme
call plug#end()

" ###########################
" #                         #
" #      COLOR SCHEME       #
" #                         #
" ###########################
colorscheme onedark


" ########################
" #                      # 
" #     KEY MAPPINGS     # 
" #                      #
" ########################

" Uses Tab to trigger compeletion
inoremap <silent><expr> <TAB>
      \ pumvisible() ? "\<C-n>" :
      \ <SID>check_back_space() ? "\<TAB>" :
      \ coc#refresh()
inoremap <expr><S-TAB> pumvisible() ? "\<C-p>" : "\<C-h>"

function! s:check_back_space() abort
  let col = col('.') - 1
  return !col || getline('.')[col - 1]  =~# '\s'
endfunction

" Set leader to space
let mapleader = ' '

" ### Tab maipulation <leader>t ### 
nnoremap <Leader>tp :tabprevious<CR>
nnoremap <silent> <Leader>tt :tabnew<CR>
nnoremap <silent> <Leader>tn :tabnext<CR>
nnoremap <silent> <Leader>to :tabonly<CR>
nnoremap <silent> <Leader>td :tabclose<CR>


" ### Window manipulation ### 
nnoremap <Leader>wh <C-w>h               
nnoremap <Leader>wj <C-w>j                   
nnoremap <Leader>wk <C-w>k              
nnoremap <Leader>wl <C-w>l              
nnoremap <Leader>wd <C-w>q              
nnoremap <Leader>wH <C-w>H              
nnoremap <Leader>wJ <C-w>J              
nnoremap <Leader>wK <C-w>K              
nnoremap <Leader>wL <C-w>L              

" ### File Tree manipulation ###
nnoremap <silent> <Leader>ft :Defx -columns=icons:indent:filename:type<CR>

" ### buffer manipulation ### 
nnoremap <Leader>bl :ls<CR>             
nnoremap <Leader>bd :bdelete<CR>        
nnoremap <Leader>bn :bnext<CR>          
nnoremap <Leader>bp :bprevious<CR>

" ### Defx key mapping ### 
autocmd FileType defx call s:ConfigKeyMap()

" ### coc key-mapping ###
nnoremap <silent> <F1>  :CocCommand<CR> 
nnoremap <silent><expr> <Leader>cf
  \ CocAction('format') 
nnoremap <silent> <Leader>ce
  \ :CocList diagnostics<CR>

function! s:ConfigKeyMap() abort
  " open selected file in new buffer
  nnoremap <silent><buffer><expr> <CR>
    \ defx#do_action('drop')
  nnoremap <silent><buffer><expr> vs
    \ defx#do_action('drop', 'vsplit')
  nnoremap <silent><buffer><expr> s
    \ defx#do_action('drop', 'split') 
  nnoremap <silent><buffer><expr> o
    \ defx#do_action('open_tree', 'toggle')
  nnoremap <silent><buffer><expr> p
    \ defx#do_action('cd', ['..']) 
  nnoremap <silent><buffer><expr> n
    \ defx#do_action('new_file') 
  nnoremap <silent><buffer><expr> DD
    \ defx#do_action('remove')
  nnoremap <silent><buffer><expr> .. 
    \ defx#do_action('cd', ['..'])
endfunction




" ############################
" #                          #
" #     PLUGIN SETTINGS      #
" #                          #
" ############################
" ### Defx - The File Manager ### 
call defx#custom#option('_', {
  \ 'winwidth':   30,
  \ 'split':      'vertical',
  \ 'direction':  'botright',
  \ 'toggle':     1,
  \ 'resume':     1,
  \ }) 

" ### Lightline - Status ###
let g:lightline = {
  \ 'colorshceme': 'onedark',
  \ 'active': {
  \   'left': [ ['mode', 'paste'],
  \             ['bufnum'],  
  \             ['iconrelpath', 'modified'] ]
  \ },
  \ 'inactive': {
  \   'left': [ ['bufnum'],
  \             ['iconrelpath',  'modified'] ]
  \ },
  \ 'separator': { 'left': "\ue0b0", 'right': "\ue0b2" },
  \ 'subseparator': { 'left': "\ue0b1", 'right': "\ue0b3" },
  \ 'component_function': {
  \   'filetype': 'MyFiletype',
  \   'fileformat': 'MyFileformat',
  \ },
  \ 'component': {
  \   'iconrelpath': '%{WebDevIconsGetFileTypeSymbol()} %f',
  \ },
  \ 'tab': {
  \   'active': [ 'tabnum', 'iconfilename', 'modified' ],
  \   'inactive': [ 'tabnum', 'iconfilename', 'modified' ]
  \ },
  \ 'tabline': {
  \   'right': []
  \ },
  \ 'tab_component_function': {
  \   'iconfilename': 'IconFileName'
  \ }
  \ }
function! MyFiletype()
  return winwidth(0) > 70 ? (strlen(&filetype) ? &filetype . ' ' . WebDevIconsGetFileTypeSymbol() : 'no ft') : ''
endfunction
  
function! MyFileformat()
  return winwidth(0) > 70 ? (&fileformat . ' ' . WebDevIconsGetFileFormatSymbol()) : ''
endfunction

function! IconFileName(n)
  return WebDevIconsGetFileTypeSymbol(). ' ' . lightline#tab#filename(a:n)
endfunction 

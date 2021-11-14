echo 'indent.vim sourced'
let s:ft_indents = { 
    \ 'typescript': 2, 
    \ 'typescriptreact': 2
    \ }

let k = keys(s:ft_indents)

function! SetIndent(ft, size)
    autocmd FileType a:ft set shiftwidth=a:size
    autocmd FileType a:ft set tabstop=a:size
    autocmd FileType a:ft set softtabstop=a:size
endfunction

for i in k
    call SetIndent(i, s:ft_indents[i])
endfor


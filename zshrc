# load antigen
ANTIGEN_PATH="$HOME/antigen.zsh"
source $ANTIGEN_PATH

if [ $(uname -s) = 'Darwin' ]; then
	source ~/.bash_profile
fi 
# =====Antigen Configs=======
antigen use oh-my-zsh
antigen bundle git
antigen bundle pip
antigen bundle lein
antigen bundle command-not-found
antigen bundle docker
antigen bundle zsh-users/zsh-syntax-highlighting
antigen bundle esc/conda-zsh-completion
antigen apply

#####################################################
#													#
#						ALIAS						#
#													#	
#####################################################

alias watch-temp='sudo powermetrics --samplers smc |grep -i "CPU die temperature"'
alias ea='conda activate'
alias ipy=ipython 
alias dc='docker-compose'

eval $(thefuck --alias)
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init -)"
fi
eval "$(starship init zsh)"
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(lua $HOME/z.lua/z.lua --init zsh)"
export PYENV_ROOT="$HOME/.pyenv"
export PATH="$PYENV_ROOT/bin:$PATH"
eval "$(pyenv init --path)"

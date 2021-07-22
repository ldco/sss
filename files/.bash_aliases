# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep="grep --color=auto"
    alias fgrep="fgrep --color=auto"
    alias egrep="egrep --color=auto"
fi
# colored GCC warnings and errors
#export GCC_COLORS='error=01;31:warning=01;35:note=01;36:caret=01;32:locus=01:quote=01'
# some more ls aliases
alias ll="ls -alF"
alias la="ls -A"
alias l="ls -CF"
alias d="ls -ltr"
alias h="history"
alias hg="history | grep"
alias g="grep -i "
alias gr="grep -r "
alias fgr="find | grep "

alias dush="du -sch .[!.]* * | sort -h"
alias glan="glances"
alias upgrade="sudo apt update && sudo apt -y --allow-downgrades upgrade && sudo flatpak -y uninstall --unused && sudo flatpak repair && sudo flatpak -y update && sudo apt -y autoremove && sudo apt -y autoclean && sudo apt update"
alias upgradeserver="sudo apt update && sudo apt -y upgrade && sudo apt -y autoremove && sudo apt -y autoclean && sudo apt update && sudo systemctl reboot"
#aliases for git
alias ga="git add ."
alias gitc="git add . && git commit -am"
alias gpo="git push origin"
alias gpom="git push origin master"
alias gpomf="git push -f origin master"
alias gpod="git push origin dev"
alias gpodf="git push -f origin dev"
alias gco="git checkout"
alias gcom="git checkout master"
alias gcod="git checkout dev"
alias gmd="git merge dev"
alias gb="git branch"
alias grao="git remote add origin"
alias gclean="git remote prune origin && git repack && git prune-packed && git reflog expire --expire=1.month.ago && git gc --aggressive"
alias gundo="reset HEAD~1 --mixed"
# alias python="/usr/bin/python3.9"
# alias pip="python3.9 -m pip"
# alias python="python3"
# alias pip="pip3"

# Add an "alert" alias for long running commands.  Use like so:
#   sleep 10; alert
# alias alert='notify-send --urgency=low -i "$([ $? = 0 ] && echo terminal || echo error)" "$(history|tail -n1|sed -e '\''s/^\s*[0-9]\+\s*//;s/[;&|]\s*alert$//'\'')"'

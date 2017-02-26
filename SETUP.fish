#!/usr/bin/fish
# 
# 
# CRABTOOLKITDIR
if contains "Linux" (uname)
    set -x CRABTOOLKITDIR (dirname (readlink -f (status --current-filename)))
end
if contains "Darwin" (uname)
    set -x CRABTOOLKITDIR (dirname (perl -MCwd -e 'print Cwd::abs_path shift' (status --current-filename)))
end
export CRABTOOLKITDIR
#<DEBUG># echo "$CRABTOOLKITDIR"
# 
# Check
if [ x"$CRABTOOLKITDIR" = x"" ]
    exit
end
#
# PATH
if not contains "$CRABTOOLKITDIR/bin" $PATH
    set -x PATH "$CRABTOOLKITDIR/bin" $PATH
end
#
# LIST
set -x CRABTOOLKITCMD pdbi-uvt-go-average pdbi-uvt-go-uvfit
# 
# CHECK
# -- 20160427 only for interactive shell
# -- http://stackoverflow.com/questions/12440287/scp-doesnt-work-when-echo-in-bashrc
if status --is-interactive
  for TEMPTOOLKITCMD in {$CRABTOOLKITCMD}
    type $TEMPTOOLKITCMD
  end
end



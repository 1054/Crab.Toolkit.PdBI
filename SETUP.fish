#!/usr/bin/fish
#
# readlink
#if contains "Darwin" (uname)
#    function readlink
#        for i in (seq 1 (count $argv))
#            #echo "$argv[$i]"
#            if [ (expr substr + "$argv[$i]" 1 1) = "-" ]
#            	#check the input is not starting with "-"
#            	#echo "No"
#            else if [ (expr substr + "$argv[$i]" 1 1) = "/" ]
#            	#check the input is an absolute path
#            	#echo "Yes"
#            	if test -f "$argv[$i]"
#            		###echo "cd \"\$(dirname \$(pwd -P)/$argv[$i])\" && echo \$(pwd -P)/\$(basename \"$argv[$i]\")"
#            	    bash -c "cd \"\$(dirname \$(pwd -P)/$argv[$i])\" && echo \$(pwd -P)/\$(basename \"$argv[$i]\")"
#            	    #pwd
#            	else
#            		###echo "cd \"\$(pwd -P)/$argv[$i]\" && echo \$(pwd -P)/"
#            	    bash -c "cd \"\$(pwd -P)/$argv[$i]\" && echo \$(pwd -P)/"
#            	    #pwd
#            	end
#            else
#            	#check the input is a relative path
#            	#echo "Yes"
#            	if test -f "$argv[$i]"
#            		###echo "cd \"\$(dirname \$(pwd -P)/$argv[$i])\" && echo \$(pwd -P)/\$(basename \"$argv[$i]\")"
#            	    bash -c "cd \"\$(dirname \$(pwd -P)/$argv[$i])\" && echo \$(pwd -P)/\$(basename \"$argv[$i]\")"
#            	    #pwd
#            	else
#            		###echo "cd \"\$(pwd -P)/$argv[$i]\" && echo \$(pwd -P)/"
#            	    bash -c "cd \"\$(pwd -P)/$argv[$i]\" && echo \$(pwd -P)/"
#            	    #pwd
#            	end
#            end
#        end
#        #if [[ (count $argv) -gt 1 ]]; then if [[ "$1" == "-f" ]]; then shift; fi; fi
#        #DIR=$(echo "${1%/*}"); (cd "$DIR" && echo "$(pwd -P)/$(basename ${1})")
#    end
#    #readlinkff -f "../../"
#    #readlinkff -f "SETUP.fish"
#end
#exit
# 
# 
# <TODO> ONLY FOR LINUX FISH SHELL
if not contains "Linux" (uname)
    exit
end
# 
# 
# 
set -x CRABTOOLKITDIR (dirname (readlink -f (status --current-filename)))
export CRABTOOLKITDIR
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



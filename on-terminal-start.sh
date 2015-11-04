# The common additional terminal start-up commands of johnmcfarlane.
#
# To use this, please add the following line to ~/.bashrc:
#
#   source "$HOME"/bin/on-terminal-start.sh

# add this folder to the path
export PATH="$PATH":"$HOME"/bin

# helps make using RSA keys with Git bearable
eval "$(ssh-agent -s)"

# helpful coloring of terminal text (only suitable for humanoids)
force_color_prompt=yes


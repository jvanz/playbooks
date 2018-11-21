#!/bin/sh

# Download the archive of the github.com/jvanz/dotfiles to the master machine.
# Hence, it is not necessary to download the repo in the server used as a
# workstation (without admin access)

mkdir -p files

wget -O files/dotfiles.zip https://github.com/jvanz/dotfiles/archive/master.zip

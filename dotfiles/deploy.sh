#!/bin/sh

BASE=/mnt/cephfs/admin/sysadmin-dsp/dotfiles

ln -s ${BASE}/ansible.cfg ${HOME}/.ansible.cfg

ln -s ${BASE}/hgrc ${HOME}/.hgrc
ln -s ${BASE}/gitconfig ${HOME}/.gitconfig

mv -f ${HOME}/.bashrc ${HOME}/.bashrc.old
ln -s ${BASE}/bashrc ${HOME}/.bashrc

ln -s ${BASE}/tmux.conf ${HOME}/.tmux.conf

ln -s ${BASE}/vimrc ${HOME}/.vimrc
ln -s ${BASE}/vimfiles ${HOME}/.vim


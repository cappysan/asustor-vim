#!/usr/bin/env bash
#
set -eu -o pipefail

export PATH="/opt/x86_64-asustor-linux-gnu/bin:$(pwd)/opt/x86_64-asustor-linux-gnu/bin/:$PATH"
export CFLAGS="-O2"
export CXXFLAGS="-O2"
export LDFLAGS="-w -s -L$(pwd)/_build/opt/x86_64-asustor-linux-gnu/lib"

cd vim
make distclean || true

./configure \
  --build=x86_64-pc-linux-gnu \
  --host=x86_64-asustor-linux-gnu \
  --prefix=/usr/local/AppCentral/cappysan-vim \
  --with-local-dir=/opt/x86_64-asustor-linux-gnu \
  --with-tlib=ncurses \
  --with-features=huge \
  --enable-multibyte \
  --disable-icon-cache-update \
  --disable-desktop-database-update \
  --disable-nls \
  --disable-gtktest \
  ;
make

tmppath=$(mktemp -d)
make install DESTDIR=${tmppath}

cd ..
echo ${tmppath}
cp -rv ${tmppath}/usr/local/AppCentral/cappysan-vim/{bin,share} apk/

rm -vfr apk/share/{applications,icons,man}
rm -vfr apk/share/vim/vim91/tutor
rm -vf  apk/share/vim/vim91/{README.txt,vimrc_example.vim}
rm -vf  apk/bin/vimtutor
rm -fr ${tmppath}

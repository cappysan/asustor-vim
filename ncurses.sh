#!/usr/bin/env bash
#
set -eu -o pipefail

destdir=$(pwd)/_build

export PATH="/opt/x86_64-asustor-linux-gnu/bin:$PATH"
export CFLAGS="-fPIE -O2"
export CXXFLAGS="-fPIE -O2"
export LDFLAGS="-w -s"

cd ncurses
make distclean || true

./configure \
  --build=x86_64-pc-linux-gnu \
  --host=x86_64-asustor-linux-gnu \
  --prefix=/opt/x86_64-asustor-linux-gnu \
  --with-local-dir=/opt/x86_64-asustor-linux-gnu \
  --without-progs \
  --without-debug \
  --without-shared \
  --without-cxx-shared \
  --enable-termcap \
  --enable-ext-colors \
  --enable-ext-mouse \
  ;

make

make install DESTDIR=${destdir}

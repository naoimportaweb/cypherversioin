#!/bin/bash

# LIMPAR TUDO
if [ -f /tmp/cver.py ]; then
	rm /tmp/cver.py
fi 

if [ -f /etc/cver ]; then
	rm -r /etc/cver
fi

if [ -f /usr/bin/cver ]; then
	rm /usr/bin/cver
fi

# BAIXANDO E INSTALANDO NO LOCAL
wget -O /tmp/cver.py http://cyberframework.com.br/cryptoversion/client/cver.py
mkdir /etc/cver
cp /tmp/cver.py /etc/cver/cver.py
chmod +x /etc/cver/cver.py
ln -s /usr/bin/cver /etc/cver/cver.py





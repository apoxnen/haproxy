FROM haproxytech/haproxy-ubuntu:2.0
COPY haproxy.cfg /usr/local/etc/haproxy/haproxy.cfg
COPY backend_selector.lua /usr/local/etc/haproxy/backend_selector.lua
# COPY backend_selector.lua /etc/haproxy/backend_selector.lua

RUN apt-get update -y && apt-get install curl luarocks -y 

#RUN apt-get update && apt-get install --no-install-recommends -y \   
# vim-tiny \  
# && apt-get clean && rm -rf /var/lib/apt/lists/*

RUN mkdir /var/lib/haproxy/dev
RUN mkdir /var/lib/haproxy/dev/log

RUN luarocks install luasocket
RUN luarocks install lua-cjson

COPY test_load.sh test_load.sh
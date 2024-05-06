#!/bin/bash

# Lee la arquitectura del sistema
ARCHITECTURE=$(uname -m)

# Comprueba si la arquitectura es arm
if [ "$ARCHITECTURE" = "armv7l" ]; then
	apt install openssl libssl-dev pkg-config curl libffi-dev -y
	curl https://sh.rustup.rs -sSf  > /tmp/cargo1.sh
	chmod 777 /tmp/cargo1.sh
	/tmp/cargo1.sh --default-toolchain=1.72.1 -y
	export PATH="/root/.cargo/bin:${PATH}"
    export RUSTUP_TOOLCHAIN=1.72.1
	export OPENSSL_DIR=/usr/lib/ssl
	mkdir /usr/lib/ssl/include
	cp /usr/include/openssl/* /usr/lib/ssl/include
fi

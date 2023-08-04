SOLC = /usr/bin/solc

all:
	$(SOLC) --bin BB.sol --evm-version byzantium | awk 'NR>3' > BB.bin
	$(SOLC) --abi BB.sol --evm-version byzantium | awk 'NR>3' > BB.json
	$(SOLC) --metadata BB.sol --evm-version byzantium | awk 'NR>3' > BB.metadata.json
	truncate -s -1 BB.bin

install-py: all
	cp -v *.json ../python/eth_bb/data/
	cp -v *.bin ../python/eth_bb/data/

install: install-py

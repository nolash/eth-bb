# eth-bb

This is an attempt at making a smart contract to signal unidirectional content updates, which can be resolved to content.


## Intuition

Let's compare this to a blog.

A blog has a HTML render as default, but may provide alternate sources, like RSS, ActivityPub and more.

In this case, the default render is plain text. But it's possible to create alternate versions by mutating the post context. We'll see how. But let's get set up first.


## Setup

The setup has two types of requirements. One is infrastructure, the other is tooling.

Tooling is simple. Let's go through that first.

You will need python 3.8-3.10, preferably a virtual environment. And you will install a python module from this repository, as so (assuming your environment has been set up, replace x.x.x with the current version built):

```
cd python
python setup.py sdist
pip install dist/eth-bb-x.x.x.tar.gz
```

### Infrastructure

You will need two additional things to proceed:

- A "web3" JSON-RPC endpoint to communicate with an EVM node.
- A [keyfile](https://github.com/ethereum/wiki/wiki/Web3-Secret-Storage-Definition) for an address with sufficient gas token balance.

How to accomplish this is out of scope of this readme.

That being said, the python environment we have just created enables you to create new wallets on the command line, which you could fund for this particular purpose only. Issuing `eth-keyfile --help` in your terminal in the python environment should get your started with that.


### Publishing the contract

The python environment gives us access to the `chainlib-gen` tool, which is capable of generating the bytecode for publishing this contract.

A compressed example would look like this:

```
eth-gas -y <keyfile_path> --fee-limit 4000000 --data $(chainlib-gen eth_bb bytecode) -s -w 0
```

The output of this command is a transaction hash, from which the contract address easily be recovered:

```
eth-get <hash> -r -o contract
```


## Adding posts

This package defines the tool `eth-bb`. 

After the contract has been published, posts can be added using the `eth-bb` tool. Here are some examples:

```
# publish plain text content hash
eth-bb -y <keyfile_path> -e <contract_address> --fee-limit 100000 <256_bit_content_hash>

# publish plain text from file
eth-bb -y <keyfile_path> -e <contract_address> --fee-limit 100000 --file <file_to_publish>

# publish rss content from hash 
eth-bb -y <keyfile_path> -e <contract_address> --mime application/rss+xml --fee-limit 100000 <256_bit_content_hash>
```

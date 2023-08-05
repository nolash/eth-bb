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

Add a post with the `add(context,content)` smart contract method.

The context is like a subdomain. `bytes32(0)` means "global context."


### Using the tool

This package defines the tool `eth-bb-put`. 

After the contract has been published, posts can be added using the `eth-bb` tool. Here are some examples:

```
# publish plain text content hash (global context)
eth-bb-put -y <keyfile_path> -e <contract_address> --fee-limit 100000 <256_bit_content_hash>

# publish plain text from file (global context)
eth-bb-put -y <keyfile_path> -e <contract_address> --fee-limit 100000 --file <file_to_publish>

# publish plain text from file, with a context
eth-bb-put -y <keyfile_path> -e <contract_address> --context 2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae --fee-limit 100000 --file <file_to_publish>

# publish rss content from hash 
eth-bb-put -y <keyfile_path> -e <contract_address> --mime application/rss+xml --fee-limit 100000 <256_bit_content_hash>

# publish rss content from hash in context
eth-bb-put -y <keyfile_path> -e <contract_address> --context 2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae --mime application/rss+xml --fee-limit 100000 <256_bit_content_hash>
```


#### Calculating the context

If the `--context` parameter is given by itself, the entry will be recorded in the smart contract under that 256-bit context.

If no `--context` parameter is given, the entry will be recorded in the smart conrtact under the context `bytes32(0x0)`

If `--mime` is specified, then the UTF-8 byte value of the string passed to the argument will be appended to the 256 bit context (the corresponding byte value of the hex), separated by "." (0x2E). The context used for the smart contract submission will be the sha256 hash of that data.

For example; with `--context 2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae` and `--mime foo/bar`, the resulting context will be `3087da3a4531097111e85c59fe75593c92b92b4cf55bc3071224ed6c14cb48b9`.


## Retrieving posts

Number of posts for a specific contexts is retrieved with the smart contract method `entryCount(signer,context)`.

A single post in a specific contexts is retrieved with the smart contract method `entry(signer,context,idx)`, where `idx` is the zero-indexed index of the post (i.e. `entryCount(...)-1`).


### Using the tool

This package defines the tool `eth-bb-get`

It returns ranges of updates queried by author and context.


```
# get all updates from author Eb3907eCad74a0013c259D5874AE7f22DcBcC95C for the global context
eth-bb-get -e <contract_address> --fee-limit 100000 Eb3907eCad74a0013c259D5874AE7f22DcBcC95C

# get next 3 updates after skipping first 10 from author Eb3907eCad74a0013c259D5874AE7f22DcBcC95C for the global context
eth-bb-get -e <contract_address> --fee-limit 100000 --offset 10 --limit 3 Eb3907eCad74a0013c259D5874AE7f22DcBcC95C

# get last three updates from same author in reverse order
eth-bb-get -e <contract_address> --fee-limit 100000 --reverse --limit 3 Eb3907eCad74a0013c259D5874AE7f22DcBcC95C
```

By default a list of content hashes is returned, in sequence, one on each line.


#### Resolving content hashes

Using the `--resolve <spec>` flag, each content hash can be resolved into actual content before being output.

The builtin module `eth_bb.resolve` can automagically resolve resolver specs.

Currently `eth_bb.resolve` only implements the `http` resolver. When an HTTP-spec is detected, the url `<spec>/<hash>` will be constructed and used for a HTTP request to retrieve the data. For example, if the url is `http://localhost:8080` and the hash to be retrieved is `2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae`, the request will be made to `http://localhost:8080/2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae`.

The module to handle the resolver can be overridden using the `--resolver-module` flag. This must be a python module path, and must implement the method `resolve(spec, identifier)` which must return a _string_ with the resolved content. If the content could not be resolved, an empty string must be returned. It is advisable to _log an error_ on failing to resolve, describing the problem.

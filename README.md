# eth-bb

This is an attempt at making a smart contract to signal unidirectional content updates, which can be resolved to content.


## Intuition

Let's compare this to a blog.

A blog has a HTML render as default, but may provide alternate sources, like RSS, ActivityPub and more.

In this case, the default render is plain text. But it's possible to create alternate versions by mutating the post topic. We'll see how. But let's get set up first.


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

Add a post with the `add(topic,content)` smart contract method.

The topic is like a subdomain. `bytes32(0)` means "global topic."


### Using the tool

This package defines the tool `eth-bb-put`. 

After the contract has been published, posts can be added using the `eth-bb` tool. Here are some examples:

```
# publish plain text content hash (global topic)
eth-bb-put -y <keyfile_path> -e <contract_address> --fee-limit 100000 <256_bit_content_hash>

# publish plain text from file (global topic)
eth-bb-put -y <keyfile_path> -e <contract_address> --fee-limit 100000 --file <file_to_publish>

# publish plain text from file, with a topic
eth-bb-put -y <keyfile_path> -e <contract_address> --topic 0x2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae --fee-limit 100000 --file <file_to_publish>

# publish rss content from hash 
eth-bb-put -y <keyfile_path> -e <contract_address> --mime application/rss+xml --fee-limit 100000 <256_bit_content_hash>

# publish rss content from hash in topic, with topic defined as string instead of hex
eth-bb-put -y <keyfile_path> -e <contract_address> --topic foo --mime application/rss+xml --fee-limit 100000 <256_bit_content_hash>
```


#### Calculating the topic

If no `--topic` parameter is given, the entry will be recorded in the smart conrtact under the topic `bytes32(0x0)`

If the `--topic` parameter is given as a string, the topic will be the `sha256` sum of that string.

Otherwise, the `--topic` parameter _must_ be prefixed with `0x` and _must_ represent 32 bytes.

If `--mime` is specified, then the UTF-8 byte value of the string passed to the argument will be appended to the 256 bit topic (the corresponding byte value of the hex), separated by "." (0x2E). The topic used for the smart contract submission will be the sha256 hash of that data.

For example; with `--topic 0x2c26b46b68ffc68ff99b453c1d30413413422d706483bfa0f98a5e886266e7ae` (or `--topic foo`) and `--mime foo/bar`, the resulting topic will be `3087da3a4531097111e85c59fe75593c92b92b4cf55bc3071224ed6c14cb48b9`.


## Retrieving posts

Number of posts for a specific topics is retrieved with the smart contract method `entryCount(signer,topic)`.

A single post in a specific topics is retrieved with the smart contract method `entry(signer,topic,idx)`, where `idx` is the zero-indexed index of the post (i.e. `entryCount(...)-1`).


### Using the tool

This package defines the tool `eth-bb-get`

It returns ranges of updates queried by author and topic.


```
# get all updates from author Eb3907eCad74a0013c259D5874AE7f22DcBcC95C for the global topic
eth-bb-get -e <contract_address> --fee-limit 100000 Eb3907eCad74a0013c259D5874AE7f22DcBcC95C

# get next 3 updates after skipping first 10 from author Eb3907eCad74a0013c259D5874AE7f22DcBcC95C for the global topic
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

The [wala project](https://git.defalsify.org/wala/) provides functionality to easily PUT and GET using (sha256) content addressing.


#### Rendering

Using the `--render` flag, extra processing can be applied on resolved content before generating output.

Default behavior is to _suppress_ any content that does not match the rendering expectations. This behavior can be changed by specifying the `--verify` flag, which will terminate when non-conforming data is encountered.

With the `--render-module` flag, the module use to generate the rendering can be defined directly on the command line. The module _must_ contain a class called `Builder` which satisfies the pseudo-interface defined in `eth_bb.render.Renderer`. This repository contains a module `example.render` that demonstrates a simple render override.


## Scanning with eth-monitor

**eth-monitor 0.8.2 or greater is required**.

The [eth-monitor](https://git.defalsify.org/eth-monitor) tool enables syncing the transactions of the chain network with arbitrary processing code. The tools has a lot of features and switches to control its behavior, so please refer to the repository readme or its man page for details on how to use it.

The `eth_bb.filter` package can be referenced on the command line when invoking `eth-monitor`, which stores all transactions matching the `add(bytes32,bytes32)` signature to be processed.

There are currently three filters to handle resolution and storage of the matching transactions:

* `eth_bb.filter.mem`: effectively noop (base class for fs)
* `eth_bb.filter.fs`: stores records on filesystem, appended to `<bbpath>/<author>/<topic>/<YYYYMMDD>`
* `eth_bb.filter.sqlite`: stores records in sqlite database)

In the example below the sqlite flavor is used. It can be invoked against (future) transactions for the smart contract as:

`eth-monitor --exec <contract_address> --filter eth_bb.filter.sqlite --head`

By default, the sql db file will be placed in the working directory. This can be changed by specifying the path explicitly:

`eth-monitor --exec <contract_address> --filter eth_bb.filter.sqlite --head -k bbpath=<path_to_db>`

The filter can also resolve hashes against a [wala-like](https://git.defalsify.org/wala/) endpoint, by specifying the its url, e.g:

`eth-monitor --exec <contract_address> --filter eth_bb.filter.sqlite --head -k bbresolver=http://localhost:8080`

For every successfully resolved item, the content will be set in the `content` column of the database, and the `reaolved` column will be set to true.

On startup, any previously unresolved content will be attempted resolved. Failed resolution does not hinder operation.

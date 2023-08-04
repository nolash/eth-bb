pragma solidity >=0.8.0;

// SPDX-License-Identifier: AGPL-3.0-or-later

contract BB {
	mapping ( address => mapping ( bytes32 => bytes32[]) ) public entry;

	function add(bytes32 _ctx, bytes32 _content) public returns (uint256) {
		bytes32[] storage ctxPost;
		uint256 i;

		ctxPost = entry[msg.sender][_ctx];
		i = ctxPost.length;
		ctxPost.push(_content);
		return i;
	}
}

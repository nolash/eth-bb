pragma solidity >=0.8.0;

// SPDX-License-Identifier: AGPL-3.0-or-later

contract BB {
	mapping ( address => mapping ( bytes32 => bytes32[]) ) public entry;

	event NewEntry(address indexed _address, bytes32 indexed _context, uint256 indexed _idx, bytes32 _content);

	function add(bytes32 _ctx, bytes32 _content) public returns (uint256) {
		bytes32[] storage ctxPost;
		uint256 i;

		ctxPost = entry[msg.sender][_ctx];
		i = ctxPost.length;
		ctxPost.push(_content);
		emit NewEntry(msg.sender, _ctx, i, _content);
		return i;
	}

	function entryCount(address _author, bytes32 _ctx) public view returns(uint256) {
		return entry[_author][_ctx].length;
	}
}

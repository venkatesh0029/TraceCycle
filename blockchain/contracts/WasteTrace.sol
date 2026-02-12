// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract WasteTrace {
    struct Waste {
        uint256 id;
        string wasteType;
        string status;
        address owner;
        uint256 timestamp;
    }

    mapping(uint256 => Waste) public wastes;
    uint256 public count;

    event WasteCreated(uint256 id, address owner);
    event StatusUpdated(uint256 id, string status);
    event WasteTransferred(uint256 id, address from, address to);

    function createWaste(string memory _type) public {
        count++;
        wastes[count] = Waste(count, _type, "Generated", msg.sender, block.timestamp);
        emit WasteCreated(count, msg.sender);
    }

    function updateStatus(uint256 _id, string memory _status) public {
        require(wastes[_id].id != 0, "Waste not found");
        // Only owner can update status? Ideally yes, or authorized actors. For simplicity, allowing anyone for now or maybe just owner.
        // Let's restrict to owner for better security demonstration.
        require(wastes[_id].owner == msg.sender, "Not owner");
        wastes[_id].status = _status;
        emit StatusUpdated(_id, _status);
    }

    function transferWaste(uint256 _id, address _to) public {
        require(wastes[_id].owner == msg.sender, "Not owner");
        wastes[_id].owner = _to;
        emit WasteTransferred(_id, msg.sender, _to);
    }

    function getWaste(uint256 _id) public view returns (Waste memory) {
        return wastes[_id];
    }
}

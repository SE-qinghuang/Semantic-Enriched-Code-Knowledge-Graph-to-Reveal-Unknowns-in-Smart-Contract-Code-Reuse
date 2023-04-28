
pragma solidity ^0.4.23;

contract MultiOwnable {
  address public root;
  mapping (address => address) public owners; // owner => parent of owner

  constructor() public {
    root = msg.sender;
    owners[root] = root;
  }


  //ACCESS_CONTROL
  function newOwner(address _owner) external returns (bool) {
    require(_owner != 0);
    owners[_owner] = msg.sender;
    return true;
  }


}


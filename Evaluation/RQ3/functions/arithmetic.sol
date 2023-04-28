pragma solidity ^0.4.19;

contract test {

  mapping (address => uint256) balances;


  function withdraw(uint _amount) external returns (bool){
    //ARITHMETIC
    require(balances[msg.sender] - _amount > 0);
    msg.sender.transfer(_amount);
    //ARITHMETIC
    balances[msg.sender] -= _amount;
    return true;
  }

}

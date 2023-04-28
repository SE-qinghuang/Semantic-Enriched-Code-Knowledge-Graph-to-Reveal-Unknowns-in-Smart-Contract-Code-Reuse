
pragma solidity ^0.4.18;

contract Token {

   mapping(address => uint) balances;
   uint public totalSupply;
   event Transfer(address indexed _from, address indexed _to, uint256 _value);

   function Token(uint _initialSupply) {
     balances[msg.sender] = totalSupply = _initialSupply;
   }

   function transfer(address _to, uint _value) public returns (bool success) {
     //ARITHMETIC
     if(balances[msg.sender] - _value >= 0 && _value > 0) {
     	balances[msg.sender] -= _value;
     	balances[_to] += _value;
	Transfer(msg.sender,_to,_value);

	return true;
   }

 }
}
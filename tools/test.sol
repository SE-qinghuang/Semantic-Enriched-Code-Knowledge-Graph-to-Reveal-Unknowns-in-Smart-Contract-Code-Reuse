pragma solidity ^0.4.13;
/*News platform System change world**/

//Math operations with safety checks that throw on error
library SafeMath {

//division
  function div(uint256 a, uint256 b) internal constant returns (uint256) {
    assert(b > 0); 
    uint256 c = a / b;
    return c;
  }

}
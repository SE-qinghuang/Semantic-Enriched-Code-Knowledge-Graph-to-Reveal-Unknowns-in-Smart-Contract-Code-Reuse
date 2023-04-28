pragma solidity ^0.4.0;
contract SendBack {
    mapping (address => uint) userBalances;
    function withdrawBalance() {  
		uint amountToWithdraw = userBalances[msg.sender];
		userBalances[msg.sender] = 0;
        //UNCHECKED_Low_Level_CALLS
		msg.sender.send(amountToWithdraw);
	}
}
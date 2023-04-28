 pragma solidity ^0.4.15;

 contract Unprotected{
     address private owner;

     function Unprotected()
         public
     {
         owner = msg.sender;
     }

     // This function should be protected
     //ACCESS_CONTROL
     function changeOwner(address _newOwner)
         public
     {
        owner = _newOwner;
     }
 }

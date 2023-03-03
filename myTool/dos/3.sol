pragma solidity >= 0.4.19 < 0.6.0;

contract Test1 {
    uint256 public goal = 5000;

    function getGoal() public view returns (uint256) {
        return goal;
    }

    function sendGoal(address addr) public {
        addr.transfer(1 ether);
    }
}

contract Test2 {

    address[] members;

    function addMember(address addr) public {
        members.push(addr);
    }

    function transferMoney(Test1 t1) public {
        for (uint i = 0; i < members.length; ++i) {
            t1.sendGoal(members[i]);
        }
    }
}
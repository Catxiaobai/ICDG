pragma solidity >=0.4.19 <0.6.0;

contract Test1 {
    uint public goal = 5000;
    function getGoal() public view returns(uint) {
        return goal;
    }
}

contract Test2 {
    function transferMoney (Test1 t1, address addr) public {
        uint goal = t1.getGoal();
        if (3000 < goal) {
            addr.call.value(10);
        }
    }
}
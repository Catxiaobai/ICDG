pragma solidity >=0.4.19 <0.6.0;

contract Test1 {
    function getGoal() public pure returns (uint256) {
        return 5000;
    }
}

contract Test2 {
    function transferMoney(Test1 t1, uint256 b) public {
        uint256 goal_ = t1.getGoal();

        if (3000 < goal_) {
            msg.sender.call.value(10)();
        }
        if (now % b == 0) {
            msg.sender.transfer(goal_);
        }
        if (3000 > goal_) {
            b += goal_;
        }
    }
}

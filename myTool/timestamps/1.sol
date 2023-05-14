pragma solidity >=0.4.19 <0.6.0;

contract Test2 {
    function bug_time_inter(Test1 t1, uint b) public payable {
        uint256 goal_ = t1.getGoal();
        if (3000 < goal_) {
            if (now % b == 0) {
                // winner    //bug
                msg.sender.transfer(goal_);
            }
        }
    }
}

contract Test1 {
    //uint256 public goal = 5000;

    function getGoal() public pure returns (uint256) {
        return 5000;
    }
}

pragma solidity >=0.4.22 <0.6.0;

contract Test2 {
    function bug_time_inter(Test1 t1) public payable {
        uint256 goal_ = t1.getGoal();
        uint256 time = now;
        if (3000 < goal_) {
            if (time % 15 == 0) {
                // winner    //bug
                msg.sender.transfer(goal_);
            }
        }
    }
}

contract Test1 {
    uint256 public goal = 5000;

    function getGoal() public view returns (uint256) {
        return goal;
    }
}

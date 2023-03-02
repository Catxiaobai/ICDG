pragma solidity >=0.4.19 <0.6.0;

contract Test2 {
    function bug_intou_inter(Test1 t1, uint b) public view {
        uint goal_ = t1.getGoal();
        if (3000 < goal_) {
            require(b + goal_ >= b);
            b = b + goal_;
        }
    }
}

contract Test1 {
    uint public goal = 5000;

    function getGoal() public view returns (uint){
        return goal;
    }
}
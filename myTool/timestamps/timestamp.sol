pragma solidity >=0.4.19 <0.6.0;

contract Test2{
    function bug_time_inter(Test1 t1) public payable {
    uint goal_ = t1.getGoal();
    if(3000 < goal_) {
        if(now % 15 == 0) { // winner    //bug
            msg.sender.transfer(goal_);
        }
    }
}
}

contract Test1{
    uint public goal = 5000;
    function getGoal() public view returns(uint){
        return goal;
    }
}

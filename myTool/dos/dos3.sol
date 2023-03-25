pragma solidity >=0.4.19 <0.6.0;

contract Test1 {
    function getGoal() public pure returns (uint256) {
        return 5000;
    }
}

contract Test2 {
    function transferMoney(Test1 t1, address addr) public payable {
    uint256 x=10;
    	while(x>0){
    	x--;
    	}
        uint256 goal = t1.getGoal();

    }
}

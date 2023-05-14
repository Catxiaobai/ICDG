pragma solidity >= 0.4.19 < 0.6.0;

contract Test1 {
    uint256 public goal = 5000;

    function getGoal() public view returns (uint256) {
        return goal;
    }

    function setGoal(uint256 x) public {
        goal = x;
    }
    
}

contract Test2 {
    address[] members;

    function transferMoney(Test1 t1, address addr) public {
        uint256 goal = t1.getGoal();
        while (true) {
            for (uint i = 0; i < members.length; ++i) {
            if (members.length < 100) {
                // useless check
            }
            address(t1).transfer(goal);
        }
        }
    }
}
/*


Test1:
608060405261138860005534801561001657600080fd5b50610117806100266000396000f3006080604052600436106053576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063401938831460585780634b29c448146080578063b97a7d241460aa575b600080fd5b348015606357600080fd5b50606a60d2565b6040518082815260200191505060405180910390f35b348015608b57600080fd5b5060a86004803603810190808035906020019092919050505060d8565b005b34801560b557600080fd5b5060bc60e2565b6040518082815260200191505060405180910390f35b60005481565b8060008190555050565b600080549050905600a165627a7a723058200046dc04b493e140f8f7e4217579f611b0be948235d97b7b6ad2e73bea64935a0029
Uncheck External Calls: false
Strict Balance Equality: false
Transaction State Dependency: false
Block Info Dependency: false
Greedy Contract: false
DoS Under External Influence: false
Nest Call: false
Reentrancy: false
Code Coverage:0.9937106918238994
Miss recognized Jump: false
Cyclomatic Complexity: 2
Number of Instructions: 159

Running time：59ms

进程已结束,退出代码0




Test2:
608060405234801561001057600080fd5b506101fa806100206000396000f300608060405260043610610041576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063e7d0aae914610046575b600080fd5b34801561005257600080fd5b506100a7600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190803573ffffffffffffffffffffffffffffffffffffffff1690602001909291905050506100a9565b005b6000808373ffffffffffffffffffffffffffffffffffffffff1663b97a7d246040518163ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401602060405180830381600087803b15801561011057600080fd5b505af1158015610124573d6000803e3d6000fd5b505050506040513d602081101561013a57600080fd5b810190808051906020019092919050505091505b6001156101c857600090505b6000805490508110156101c357606460008054905050508373ffffffffffffffffffffffffffffffffffffffff166108fc839081150290604051600060405180830381858888f193505050501580156101b7573d6000803e3d6000fd5b5080600101905061015a565b61014e565b505050505600a165627a7a72305820883326b6ba4bf1e0ebbfc81bb3083b67314d3d272040bd5f9ec68c7f367327030029
Uncheck External Calls: false
Strict Balance Equality: false
Transaction State Dependency: false
Block Info Dependency: false
Greedy Contract: false
DoS Under External Influence: true
Nest Call: false
Reentrancy: false
Code Coverage:0.9959677419354839
Miss recognized Jump: false
Cyclomatic Complexity: 4
Number of Instructions: 248

Running time：80ms

*/
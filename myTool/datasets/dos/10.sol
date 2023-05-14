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

    function transferMoney(Test1 t1) public {
        while (true) {
            uint256 goal = t1.getGoal();
            if (goal > 100) {
                goal -= 100;
                t1.setGoal(goal);
            }
            else break;
        }
    }
}
/*
不限制循环大小
Test1:
608060405261138860005534801561001657600080fd5b50610117806100266000396000f3006080604052600436106053576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063401938831460585780634b29c448146080578063b97a7d241460aa575b600080fd5b348015606357600080fd5b50606a60d2565b6040518082815260200191505060405180910390f35b348015608b57600080fd5b5060a86004803603810190808035906020019092919050505060d8565b005b34801560b557600080fd5b5060bc60e2565b6040518082815260200191505060405180910390f35b60005481565b8060008190555050565b600080549050905600a165627a7a723058201d62421a6397fdf3a61f1bdff33f6af3d023fa49fee405b647154cedf6307b540029
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

Running time：69ms

进程已结束,退出代码0



Test2:
608060405234801561001057600080fd5b50610209806100206000396000f300608060405260043610610041576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806386ce983514610046575b600080fd5b34801561005257600080fd5b50610087600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050610089565b005b60005b6001156101d9578173ffffffffffffffffffffffffffffffffffffffff1663b97a7d246040518163ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401602060405180830381600087803b1580156100f757600080fd5b505af115801561010b573d6000803e3d6000fd5b505050506040513d602081101561012157600080fd5b8101908080519060200190929190505050905060648111156101cf576064810390508173ffffffffffffffffffffffffffffffffffffffff16634b29c448826040518263ffffffff167c010000000000000000000000000000000000000000000000000000000002815260040180828152602001915050600060405180830381600087803b1580156101b257600080fd5b505af11580156101c6573d6000803e3d6000fd5b505050506101d4565b6101d9565b61008c565b50505600a165627a7a7230582084fb84661eb08414711312352546d56c853daf3b8469103f57472f50cadd840d0029
Uncheck External Calls: false
Strict Balance Equality: false
Transaction State Dependency: false
Block Info Dependency: false
Greedy Contract: false
DoS Under External Influence: false
Nest Call: false
Reentrancy: false
Code Coverage:0.9959016393442623
Miss recognized Jump: false
Cyclomatic Complexity: 4
Number of Instructions: 244

Running time：83ms
*/
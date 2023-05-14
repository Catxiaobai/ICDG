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

    function transferMoney(Test1 t1) public {
        for (uint i = 0; i < members.length; ++i) {
            if (members.length > 10) break; // 第一个循环不超过10次
            uint256 goal = t1.getGoal();
            while (goal >= 1) {
                address(t1).transfer(1);
                goal -= 1;
            } //第二个循环次数有限但不定
        }
    }
}
/*
Test1:
608060405261138860005534801561001657600080fd5b50610117806100266000396000f3006080604052600436106053576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff168063401938831460585780634b29c448146080578063b97a7d241460aa575b600080fd5b348015606357600080fd5b50606a60d2565b6040518082815260200191505060405180910390f35b348015608b57600080fd5b5060a86004803603810190808035906020019092919050505060d8565b005b34801560b557600080fd5b5060bc60e2565b6040518082815260200191505060405180910390f35b60005481565b8060008190555050565b600080549050905600a165627a7a723058207c5056cffece4afa9a90fc7761ac54b0fbf6d65897d6952e30db861e0458c7b30029
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

Running time：57ms

进程已结束,退出代码0



Test2:
608060405234801561001057600080fd5b506101ec806100206000396000f300608060405260043610610041576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806386ce983514610046575b600080fd5b34801561005257600080fd5b50610087600480360381019080803573ffffffffffffffffffffffffffffffffffffffff169060200190929190505050610089565b005b600080600091505b6000805490508210156101bb57600a60008054905011156100b1576101bb565b8273ffffffffffffffffffffffffffffffffffffffff1663b97a7d246040518163ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401602060405180830381600087803b15801561011557600080fd5b505af1158015610129573d6000803e3d6000fd5b505050506040513d602081101561013f57600080fd5b810190808051906020019092919050505090505b6001811015156101b0578273ffffffffffffffffffffffffffffffffffffffff166108fc60019081150290604051600060405180830381858888f193505050501580156101a4573d6000803e3d6000fd5b50600181039050610153565b816001019150610091565b5050505600a165627a7a7230582091fe0201a7dc78cd50c726d4916351783e11347edac0f3ed85cfa295c78eacf40029
Uncheck External Calls: false
Strict Balance Equality: false
Transaction State Dependency: false
Block Info Dependency: false
Greedy Contract: false
DoS Under External Influence: true
Nest Call: false
Reentrancy: false
Code Coverage:0.9959839357429718
Miss recognized Jump: false
Cyclomatic Complexity: 5
Number of Instructions: 249

Running time：85ms

进程已结束,退出代码0

*/
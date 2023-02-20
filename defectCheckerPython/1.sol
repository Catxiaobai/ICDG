pragma solidity >=0.4.22 <0.6.0;

contract Overflow {
    uint private sellerBalance = 0;

    function add(uint value) public {
        sellerBalance += value;
        assert(sellerBalance >= value);
    }
}

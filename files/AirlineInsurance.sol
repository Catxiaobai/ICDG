pragma solidity ^0.8.0;

contract AirlineInsurance {
    address public insurer;
    address public insured;
    uint public amount;
    uint public premium;
    uint public deadline;
    bool public isPaid;

    constructor(address _insurer, address _insured, uint _amount, uint _premium, uint _deadline) {
        insurer = _insurer;
        insured = _insured;
        amount = _amount;
        premium = _premium;
        deadline = _deadline;
        isPaid = false;
    }

    function pay() public payable {
        require(msg.value == premium, "Premium amount is not correct");
        isPaid = true;
    }

    function claim() public {
        require(msg.sender == insured, "Only insured can claim");
        require(block.timestamp > deadline, "Deadline has not yet passed");
        require(isPaid == true, "Premium has not been paid");
        payable(insured).transfer(amount);
    }
}

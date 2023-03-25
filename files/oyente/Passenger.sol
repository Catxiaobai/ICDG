pragma solidity >=0.4.19 <0.6.0;

import "./Insurance.sol";
import "./Flight.sol";

contract Passenger {
    address public passengerAddress; // 乘客地址
    uint256 public totalPayouts; // 总赔偿金额
    uint256 public totalPremiums; // 总保险费用
    uint256 public numPolicies; // 购买的保险份数

    mapping(uint256 => bool) public policies; // 购买保险份数到是否已购买的映射
    mapping(uint256 => uint256) public payouts; // 购买保险份数到赔偿金额的映射

    Insurance public insurance;
    Flight public flight;

    function Passenger(address _passengerAddress, address _insuranceAddress) public {
        passengerAddress = _passengerAddress;
        insurance = Insurance(_insuranceAddress);
    }

    // 购买保险
    function buyInsurance(uint256 policyNumber) public payable {
        require(
            msg.value == insurance.premium()
        );
        require(!policies[policyNumber]);

        policies[policyNumber] = true;
        numPolicies++;
        totalPremiums += msg.value;
        insurance.buyInsurance.value(msg.value)();
    }

    // 航班延误赔偿
    function claimPayout(uint256 policyNumber) public {
        require(
            policies[policyNumber]);

        bool isDelayed = flight.isDelayed();
        require(isDelayed);

        uint256 payoutAmount = insurance.compensation();
        require(
            payoutAmount > payouts[policyNumber]
        );

        payouts[policyNumber] = payoutAmount;
        totalPayouts += payoutAmount; //注入整数溢出漏洞

        msg.sender.transfer(payoutAmount);
    }

    // 查询余额
    function getBalance() public view returns (uint256) {
        return address(this).balance;
    }
}

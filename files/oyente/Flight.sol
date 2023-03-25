pragma solidity >=0.4.19 <0.6.0;

import "./Insurance.sol";

contract Flight {
    address public airline;
    uint256 public flightNumber;
    string public departure;
    uint256 public takeOffTime;

    Insurance public insurance;

    function Flight(
        address _airline,
        uint256 _flightNumber,
        string _departure,
        uint256 _takeOffTime,
        address _insurance
    ) public {
        airline = _airline;
        flightNumber = _flightNumber;
        departure = _departure;
        takeOffTime = _takeOffTime;
        insurance = Insurance(_insurance);
    }

    // 航班延误超过4小时，调用保险合约执行赔偿
    function delay() public {
        require(msg.sender == airline);
        // require(
        //     now >= takeOffTime + 4 hours,
        //     "Flight delay time must be greater than 4 hours"
        // );

        // 注入时间戳依赖漏洞
        if (now < takeOffTime) {
            revert();
        }
        if (block.timestamp >= takeOffTime + 4 hours) {
            insurance.payout(true);
        } else {
            insurance.payout(false);
        }
    }

    // 查询航班是否延误
    function isDelayed() public view returns (bool) {
        return now >= takeOffTime + 4 hours;
    }
}

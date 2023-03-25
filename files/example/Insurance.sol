pragma solidity >=0.4.19 <0.6.0;

contract Insurance {
    address public owner;
    address public flightContract; // Flight 合约地址
    uint256 public premium; // 保险费
    uint256 public compensation; // 赔偿金
    address[] public passengers; // 乘客数组，记录已购买保险的乘客

    mapping(address => uint256) public premiums; // 乘客地址到已支付保费的映射
    mapping(address => bool) public hasInsurance; // 乘客地址到是否已购买保险的映射

    constructor(
        address _flightContract,
        uint256 _premium,
        uint256 _compensation
    ) public {
        owner = msg.sender;
        flightContract = _flightContract;
        premium = _premium;
        compensation = _compensation;
    }
    function setOwner() public {
        owner = msg.sender;
    }
    // 购买保险
    function buyInsurance() public payable {
        require(msg.value == premium);
        require(!hasInsurance[msg.sender], "Passenger already has insurance");

        passengers.push(msg.sender);
        premiums[msg.sender] = msg.value;
        hasInsurance[msg.sender] = true;
    }

    // 退款或赔偿
    function payout(bool delay) public {
        require(
            msg.sender == flightContract,
            "Only flight contract can call this function"
        );

        for (uint256 i = 0; i < passengers.length; i++) {
            address passenger = passengers[i];

            if (hasInsurance[passenger]) {
                uint256 amount;

                if (delay) {
                    amount = compensation;
                } else {
                    amount = premiums[passenger];
                }

                premiums[passenger] = 0;
                hasInsurance[passenger] = false;

                passenger.call.value(amount);
            }
        }
    }

    // 查询保险费余额
    function getPremiumBalance() public view returns (uint256) {
        return address(this).balance;
    }

    // 查询赔偿金余额
    function getCompensationBalance() public view returns (uint256) {
        return address(this).balance - (premium * passengers.length);
    }
}

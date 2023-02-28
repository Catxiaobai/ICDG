pragma solidity >=0.4.19 <0.6.0;

contract Test2 {
    uint256 public value;

    function setValue(uint256 _value) public {
        value = _value;
    }

    function doS() public pure{
        while (true) {
            uint256 a = 0;
            a = a + 1;
        }
    }
}

contract Test1 {
    Test2 public test2;

    constructor(Test2 _test2) public {
        test2 = _test2;
    }

    function setValueInTest2(uint256 _value) public {
        test2.setValue(_value);
    }

    function callDoSInTest2() public view{
        test2.doS();
    }
}

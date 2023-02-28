pragma solidity >=0.4.19 <0.6.0;

contract Test1 {
    function doS() public pure{
        while (true) {
            uint256 a = 0;
            a = a + 1;
        }
    }
}

contract Test2 {
    function callDoS(Test1 test1) public pure{
        test1.doS();
    }
}

pragma solidity >=0.4.19 <0.6.0;

contract Test1 {
    uint a = 0;
    function doS() public payable{
        while (true) {
            a = a + 1;
        }
    }
}

contract Test2 {
    function callDoS(Test1 test1) public payable{
        test1.doS();
    }
}

pragma solidity >=0.4.19 <0.6.0;

contract Test1 {
    function doS(address x) public payable {
        while (true) {
            x.transfer(0.1 ether);
        }
    }
}

contract Test2 {
    function callDoS(Test1 test1, address x) public {
        test1.doS(x);
    }
}

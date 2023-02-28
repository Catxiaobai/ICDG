pragma solidity ^0.8.0;

contract Airline {
    struct Flight {
        string flightNumber;
        uint256 departureTime;
        string origin;
        string destination;
        uint256 capacity;
        uint256 bookedSeats;
    }

    struct Passenger {
        string name;
        uint256 id;
        string flightNumber;
        uint256 seatNumber;
    }

    address public owner;
    mapping (string => Flight) public flights;
    mapping (uint256 => Passenger) public passengers;
    uint256 public passengerCount = 0;

    constructor() {
        owner = msg.sender;
    }

    modifier onlyOwner() {
        require(msg.sender == owner, "Only the owner can perform this action");
        _;
    }

    function registerFlight(string memory _flightNumber, uint256 _departureTime, string memory _origin, string memory _destination, uint256 _capacity) public onlyOwner {
        require(flights[_flightNumber].departureTime == 0, "This flight already exists");
        flights[_flightNumber] = Flight(_flightNumber, _departureTime, _origin, _destination, _capacity, 0);
    }

    function bookSeat(string memory _flightNumber, string memory _name, uint256 _id, uint256 _seatNumber) public {
        require(flights[_flightNumber].departureTime > 0, "This flight does not exist");
        require(passengers[_id].id == 0, "This passenger already has a seat booked");
        require(flights[_flightNumber].capacity > flights[_flightNumber].bookedSeats, "This flight is fully booked");
        passengers[_id] = Passenger(_name, _id, _flightNumber, _seatNumber);
        flights[_flightNumber].bookedSeats++;
        passengerCount++;
    }

    function reportIncident(string memory _flightNumber, uint256 _departureTime, string memory _origin, string memory _destination) public onlyOwner {
        // Handle incident reporting logic here, e.g. log the incident and notify the insurance contract.
    }
}

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";

contract Escrow is Ownable, ReentrancyGuard {
    IERC20 public MockUSDT;  // USDT token contract
    address public jobMarketplace; // Only JobMarketplace can call escrow functions

    struct EscrowInfo {
        address employer;
        address freelancer;
        uint256 amount;
        bool isFunded;
        bool isReleased;
    }

    mapping(bytes32 => EscrowInfo) public escrows; // Job ID → Escrow details

    event FundsDeposited(bytes32 indexed jobId, address indexed employer, uint256 amount);
    event FundsReleased(bytes32 indexed jobId, address indexed freelancer, uint256 amount);
    event FundsRefunded(bytes32 indexed jobId, address indexed employer, uint256 amount);

    modifier onlyMarketplace() {
        require(msg.sender == jobMarketplace, "Only JobMarketplace can call this");
        _;
    }

    constructor(address _MockUSDT, address initialOwner) Ownable(initialOwner) {
       
        MockUSDT = IERC20(_MockUSDT);
    }

    function setJobMarketplace(address _jobMarketplace) external onlyOwner {
        jobMarketplace = _jobMarketplace;
    }

    function depositFunds(bytes32 jobId, address employer, uint256 amount) external onlyMarketplace nonReentrant {
        require(escrows[jobId].amount == 0, "Escrow already exists");
        require(MockUSDT.transferFrom(employer, address(this), amount), "Transfer failed");

        escrows[jobId] = EscrowInfo({
            employer: employer,
            freelancer: address(0),
            amount: amount,
            isFunded: true,
            isReleased: false
        });

        emit FundsDeposited(jobId, employer, amount);
    }

    function assignFreelancer(bytes32 jobId, address freelancer) external onlyMarketplace {
        require(escrows[jobId].isFunded, "Escrow not funded");
        require(escrows[jobId].freelancer == address(0), "Freelancer already assigned");

        escrows[jobId].freelancer = freelancer;
    }

    function releaseFunds(bytes32 jobId) external onlyMarketplace nonReentrant {
        EscrowInfo storage escrow = escrows[jobId];
        require(escrow.isFunded, "No funds in escrow");
        require(escrow.freelancer != address(0), "Freelancer not assigned");
        require(!escrow.isReleased, "Funds already released");

        escrow.isReleased = true;
        require(MockUSDT.transfer(escrow.freelancer, escrow.amount), "Transfer to freelancer failed");

        emit FundsReleased(jobId, escrow.freelancer, escrow.amount);
    }

    function refundEmployer(bytes32 jobId) external onlyMarketplace nonReentrant {
        EscrowInfo storage escrow = escrows[jobId];
        require(escrow.isFunded, "No funds in escrow");
        require(escrow.freelancer == address(0), "Cannot refund after freelancer assigned");

        uint256 refundAmount = escrow.amount;
        escrow.amount = 0;
        escrow.isFunded = false;

        require(MockUSDT.transfer(escrow.employer, refundAmount), "Refund failed");

        emit FundsRefunded(jobId, escrow.employer, refundAmount);
    }
}

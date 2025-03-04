// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/utils/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/Pausable.sol";
import "./Escrow.sol"; // Import escrow contract

contract JobMarketplace is ReentrancyGuard {
    struct Job {
        string title;
        string description;
        uint256 budget;
        address employer;
        address freelancer;
        bool completed;
    }

    struct FreelancerProfile {
        string name;
        string ipfsHash;  // Skill set is stored offchain IPFS
        bool exists;
    }

    IERC20 public MockUSDT;
    Escrow public escrowContract;
    
    mapping(bytes32 => Job) public jobs; // Unique job ID → Job details
    mapping(address => FreelancerProfile) public freelancerProfiles;
    mapping(bytes32 => address[]) public jobRecommendations;
    mapping(bytes32 => address[]) public jobApplications; 

    event JobCreated(bytes32 indexed jobId, string title, address employer, uint256 budget);
    event JobAssigned(bytes32 indexed jobId, address freelancer);
    event JobCompleted(bytes32 indexed jobId, address freelancer, uint256 payout);
    event JobApplied(bytes32 indexed jobId, address freelancer);

    constructor(address _MockUSDT, address _escrow) {
        MockUSDT = IERC20(_MockUSDT);
        escrowContract = Escrow(_escrow);
    }


    function registerFreelancer(string memory _name, string memory _ipfsHash) external {
        require(!freelancerProfiles[msg.sender].exists, "Profile already exists");
    
        freelancerProfiles[msg.sender] = FreelancerProfile({
            name: _name,
            ipfsHash: _ipfsHash,
            exists: true
        });
    }

    function generateJobId(string memory _title, address _employer) public view returns (bytes32) {
        return keccak256(abi.encodePacked(_title, _employer, block.timestamp));
    }
    

    function createJob(string memory _title, string memory _description, uint256 _budget) 
        external nonReentrant returns (bytes32){
        bytes32 jobId = generateJobId(_title, msg.sender);
        require(jobs[jobId].budget == 0, "Job already exists");

        jobs[jobId] = Job({
            title: _title,
            description: _description,
            budget: _budget,
            employer: msg.sender,
            freelancer: address(0),
            completed: false
        });

        try escrowContract.depositFunds(jobId, msg.sender, _budget) {
            emit JobCreated(jobId, _title, msg.sender, _budget);
            return jobId; // ✅ Return Job ID to the caller
        } catch {
            delete jobs[jobId];
            revert("Failed to depositFunds");
        }
    }

    function applyForJob(bytes32 jobId) external {
        Job storage job = jobs[jobId];
        require(job.budget > 0, "Job does not exist");
        require(job.freelancer == address(0), "Job already assigned");
        require(freelancerProfiles[msg.sender].exists, "Freelancer must be registered");
    
        jobApplications[jobId].push(msg.sender);
        emit JobApplied(jobId, msg.sender);
    }
    
    function storeAIRecommendations(bytes32 jobId, address[] memory recommendedFreelancers) external  {
        Job storage job = jobs[jobId];

        require(jobs[jobId].budget > 0, "Job does not exist");
        require(msg.sender == job.employer, "Only employer can complete job");
        delete jobRecommendations[jobId]; // Clear old recommendations
    
        for (uint256 i = 0; i < recommendedFreelancers.length; i++) {
            jobRecommendations[jobId].push(recommendedFreelancers[i]);
        }
    }
    
    

    function autoAssignJob(bytes32 jobId, address freelancer) external nonReentrant {
        Job storage job = jobs[jobId];
        require(job.employer != address(0), "Job does not exist");
        require(job.freelancer == address(0), "Job already assigned");
        require(freelancerProfiles[freelancer].exists, "Freelancer must be registered");
    
        bool isValidFreelancer = false;
        
        // Check AI recommendations
        for (uint256 i = 0; i < jobRecommendations[jobId].length; i++) {
            if (jobRecommendations[jobId][i] == freelancer) {
                isValidFreelancer = true;
                break;
            }
        }
    
        // Check job applications
        if (!isValidFreelancer) {
            for (uint256 i = 0; i < jobApplications[jobId].length; i++) {
                if (jobApplications[jobId][i] == freelancer) {
                    isValidFreelancer = true;
                    break;
                }
            }
        }
    
        require(isValidFreelancer, "No AI recommendation or job application for this freelancer");
    
        job.freelancer = freelancer;
    
        try escrowContract.assignFreelancer(jobId, freelancer) {
            emit JobAssigned(jobId, freelancer);
        } catch {
            revert("Failed to assign freelancer in escrow");
        }
    }
    
    
    
    function completeJob(bytes32 jobId) external  nonReentrant {
        Job storage job = jobs[jobId];
        require(msg.sender == job.employer, "Only employer can complete job");
        require(job.freelancer != address(0), "No freelancer assigned");
        require(!job.completed, "Job already completed");

        job.completed = true;

        // Release funds to freelancer
        try escrowContract.releaseFunds(jobId) {
            emit JobCompleted(jobId, job.freelancer, job.budget);
        } catch {
            revert("Failed to release funds");
        }
    }

    function cancelJob(bytes32 jobId) external  nonReentrant {
        Job storage job = jobs[jobId];
        require(msg.sender == job.employer, "Only employer can cancel job");
        require(job.freelancer == address(0), "Cannot cancel after freelancer assigned");

        delete jobs[jobId];

        escrowContract.refundEmployer(jobId);
    }
}

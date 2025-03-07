// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {MockUSDT} from "../src/MockUSDT.sol";
import {Escrow} from "../src/Escrow.sol";
import {JobMarketplace} from "../src/JobMarketPlace.sol";
contract MarketPlaceTest is Test {
    MockUSDT  mockUSDT;
    Escrow escrow;
    JobMarketplace jobmarketplace;
    address freelancer = makeAddr("depositor1");
    address employer = makeAddr("depositor2");
    address owner = makeAddr("owner");

    function setUp() public {
        mockUSDT = new MockUSDT();
        escrow = new Escrow(address(mockUSDT),address(owner));
        jobmarketplace = new JobMarketplace(address(mockUSDT), address(escrow));
        vm.label(address(jobmarketplace), "Job_MarketPlace");
        vm.label(address(escrow), "Escrow");
        vm.label(address(mockUSDT), "mockUSDT");
    }

    function test_CreateJob() public {
        vm.startPrank(owner);
        escrow.setJobMarketplace(address(jobmarketplace));
        mockUSDT.mint(address(owner),2000000000000000000);
        mockUSDT.approve(address(escrow),20000000000000000);
        jobmarketplace.createJob("lala", "lala", 2000000000000000);
    }

}

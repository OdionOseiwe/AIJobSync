// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Script, console} from "forge-std/Script.sol";
import {MockUSDT} from "../src/MockUSDT.sol";
import {Escrow} from "../src/Escrow.sol";
import {JobMarketplace} from "../src/JobMarketPlace.sol";

contract DeploymentScript is Script {
    function setUp() public {}

    function run() public {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");

        vm.startBroadcast(deployerPrivateKey);

        MockUSDT  mockUSDT = new MockUSDT();
        Escrow escrow = new Escrow(address(mockUSDT),0x6644EA302A634e131F4afD73E744f03271A13d1E);
        JobMarketplace jobmarketplace = new JobMarketplace(address(mockUSDT), address(escrow));


        vm.stopBroadcast();
    }
}

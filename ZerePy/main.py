import json
import requests
from typing import Dict, List, Any, Optional
from web3 import Web3
from src.cli import ZerePyCLI

class FreelancerRecommendationAgent:
    def __init__(self, web3_provider_url: str, contract_address: str, contract_abi: List[Dict]):
        """
        Initialize the AI agent with Web3 connection and contract details.
        
        Args:
            web3_provider_url: URL of the Ethereum node
            contract_address: Address of the smart contract
            contract_abi: ABI of the smart contract
        """
        self.web3 = Web3(Web3.HTTPProvider(web3_provider_url))
        self.contract = self.web3.eth.contract(address=contract_address, abi=contract_abi)
        self.ipfs_gateway = "https://ipfs.io/ipfs/"
    
    def fetch_profile_from_ipfs(self, ipfs_hash: str) -> Optional[Dict]:
        """
        Fetch a freelancer profile from IPFS.
        
        Args:
            ipfs_hash: IPFS hash of the freelancer profile
            
        Returns:
            Freelancer profile as a dictionary or None if fetch fails
        """
        try:
            response = requests.get(f"{self.ipfs_gateway}{ipfs_hash}", timeout=10)
            response.raise_for_status()
            return json.loads(response.text)
        except (requests.RequestException, json.JSONDecodeError) as e:
            print(f"Error fetching profile {ipfs_hash}: {str(e)}")
            return None
    
    def fetch_all_profiles(self, ipfs_hashes: List[str]) -> List[Dict]:
        """
        Fetch all freelancer profiles from IPFS.
        
        Args:
            ipfs_hashes: List of IPFS hashes
            
        Returns:
            List of freelancer profiles
        """
        profiles = []
        for ipfs_hash in ipfs_hashes:
            profile = self.fetch_profile_from_ipfs(ipfs_hash)
            if profile:
                profiles.append(profile)
        return profiles
    
    def filter_freelancers(self, profiles: List[Dict], requirement: Dict) -> List[Dict]:
        """
        Filter freelancers based on requirements.
        
        Args:
            profiles: List of freelancer profiles
            requirement: Dictionary containing filtering criteria
            
        Returns:
            List of filtered freelancer profiles
        """
        filtered_profiles = []
        
        for profile in profiles:
            # Check if profile has all required skills
            if "required_skills" in requirement:
                has_all_skills = all(skill in profile.get("skills", []) for skill in requirement["required_skills"])
                if not has_all_skills:
                    continue
            
            # Check if profile meets experience requirement
            if "min_experience" in requirement and profile.get("experience", 0) < requirement["min_experience"]:
                continue
                
            # Check if profile meets hourly rate requirement
            if "max_hourly_rate" in requirement and profile.get("hourly_rate", float('inf')) > requirement["max_hourly_rate"]:
                continue
                
            filtered_profiles.append(profile)
            
        return filtered_profiles
    
    def store_recommendations(self, job_id: str, recommended_freelancers: List[Dict], employer_address: str, private_key: str) -> Optional[str]:
        """
        Store recommendations in the smart contract.
        
        Args:
            job_id: ID of the job
            recommended_freelancers: List of recommended freelancer profiles
            employer_address: Ethereum address of the employer
            private_key: Private key of the employer for transaction signing
            
        Returns:
            Transaction hash if successful, None otherwise
        """
        try:
            # Extract Ethereum addresses from profiles
            freelancer_addresses = [profile["address"] for profile in recommended_freelancers]
            
            # Convert job_id to bytes32 if it's not already
            if not isinstance(job_id, bytes):
                job_id_bytes = self.web3.to_bytes(hexstr=job_id) if job_id.startswith('0x') else self.web3.to_bytes(text=job_id)
            else:
                job_id_bytes = job_id
                
            # Build transaction
            nonce = self.web3.eth.get_transaction_count(employer_address)
            tx = self.contract.functions.storeAIRecommendations(
                job_id_bytes,
                freelancer_addresses
            ).build_transaction({
                'from': employer_address,
                'gas': 2000000,
                'gasPrice': self.web3.eth.gas_price,
                'nonce': nonce,
            })
            
            # Sign and send transaction
            signed_tx = self.web3.eth.account.sign_transaction(tx, private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            # Wait for transaction receipt
            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            
            if receipt.status == 1:
                return self.web3.to_hex(tx_hash)
            else:
                print("Transaction failed")
                return None
                
        except Exception as e:
            print(f"Error storing recommendations: {str(e)}")
            return None
    
    def recommend_freelancers(self, job_id: str, requirement: Dict, ipfs_hashes: List[str], 
                             employer_address: str, private_key: str) -> Dict:
        """
        Main function to recommend freelancers.
        
        Args:
            job_id: ID of the job
            requirement: Dictionary containing filtering criteria
            ipfs_hashes: List of IPFS hashes for freelancer profiles
            employer_address: Ethereum address of the employer
            private_key: Private key of the employer for transaction signing
            
        Returns:
            Dictionary containing result of the recommendation process
        """
        # Fetch all profiles
        profiles = self.fetch_all_profiles(ipfs_hashes)
        
        if not profiles:
            return {
                "success": False,
                "message": "Failed to fetch freelancer profiles from IPFS"
            }
        
        # Filter freelancers based on requirements
        filtered_profiles = self.filter_freelancers(profiles, requirement)
        
        if not filtered_profiles:
            return {
                "success": False,
                "message": "No freelancers match the given requirements"
            }
        
        # Store recommendations in smart contract
        tx_hash = self.store_recommendations(job_id, filtered_profiles, employer_address, private_key)
        
        if tx_hash:
            return {
                "success": True,
                "message": f"Successfully stored {len(filtered_profiles)} freelancer recommendations",
                "transaction_hash": tx_hash,
                "recommended_freelancers": [
                    {"name": profile["name"], "address": profile["address"]} 
                    for profile in filtered_profiles
                ]
            }
        else:
            return {
                "success": False,
                "message": "Failed to store recommendations in the smart contract"
            }


# ... (keep all the previous code the same until the FreelancerRecommendationCLI class)

class FreelancerRecommendationCLI(ZerePyCLI):
    def __init__(self, web3_provider_url: str, contract_address: str, contract_abi: List[Dict]):
        """
        Initialize the CLI with the AI agent.
        """
        super().__init__()
        self.agent = FreelancerRecommendationAgent(web3_provider_url, contract_address, contract_abi)
    
    def parse_arguments(self):
        """
        Parse command line arguments
        """
        import argparse
        import json
        
        parser = argparse.ArgumentParser(description='Freelancer Recommendation Agent')
        parser.add_argument('--job_id', required=True, help='Job ID (bytes32)')
        parser.add_argument('--requirement', required=True, type=json.loads, 
                          help='JSON string containing requirements')
        parser.add_argument('--ipfs_hashes', required=True, type=json.loads,
                          help='JSON array of IPFS hashes')
        parser.add_argument('--employer_address', required=True,
                          help='Ethereum address of the employer')
        parser.add_argument('--private_key', required=True,
                          help='Private key for transaction signing')
        
        return parser.parse_args()
    
    def execute(self):
        """
        Execute the CLI application
        """
        args = self.parse_arguments()
        
        result = self.run({
            "job_id": args.job_id,
            "requirement": args.requirement,
            "ipfs_hashes": args.ipfs_hashes,
            "employer_address": args.employer_address,
            "private_key": args.private_key
        })
        
        print(json.dumps(result, indent=2))


def main():
    """
    Main entry point for the CLI application.
    """
    # These would typically be loaded from environment variables or config files
    web3_provider_url = "https://rpc.blaze.soniclabs.com"
    contract_address = "0xCAC5cc02B4B67Ebe787Ba00AB00f31e3f16E7cD6"
    
    with open('contract_abi.json', 'r') as f:
        contract_abi = json.load(f)

    cli = FreelancerRecommendationCLI(web3_provider_url, contract_address, contract_abi)
    cli.execute()  # Changed from cli.start() to cli.execute()


if __name__ == "__main__":
    main()



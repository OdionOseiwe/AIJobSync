import json
import logging
import os
import requests
from datetime import datetime
from typing import Dict, List, Any, Optional
from web3 import Web3
from src.cli import ZerePyCLI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("freelancer_agent")

# JobMarketplace ABI
JOB_MARKETPLACE_ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}],
        "name": "jobs",
        "outputs": [
            {"internalType": "string", "name": "title", "type": "string"},
            {"internalType": "string", "name": "description", "type": "string"},
            {"internalType": "uint256", "name": "budget", "type": "uint256"},
            {"internalType": "address", "name": "employer", "type": "address"},
            {"internalType": "address", "name": "freelancer", "type": "address"},
            {"internalType": "bool", "name": "completed", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"internalType": "bytes32", "name": "jobId", "type": "bytes32"},
            {"internalType": "address[]", "name": "recommendedFreelancers", "type": "address[]"}
        ],
        "name": "storeAIRecommendations",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "address", "name": "", "type": "address"}],
        "name": "freelancerProfiles",
        "outputs": [
            {"internalType": "string", "name": "name", "type": "string"},
            {"internalType": "string", "name": "ipfsHash", "type": "string"},
            {"internalType": "bool", "name": "exists", "type": "bool"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "", "type": "bytes32"}, {"internalType": "uint256", "name": "", "type": "uint256"}],
        "name": "jobRecommendations",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
]

class FreelancerAgent:
    """Agent for recommending freelancers for jobs from JobMarketplace contract"""
    
    def __init__(
        self, 
        sonic_rpc_url: str,
        sonic_private_key: str,
        job_marketplace_address: str,
        ipfs_gateway: str = "https://ipfs.io/ipfs",
        allora_api_key: str = ""
    ):
        self.ipfs_gateway = ipfs_gateway
        self.allora_api_key = allora_api_key
        
        # Initialize Web3 connection
        self.mock_mode = not sonic_rpc_url or not sonic_private_key or not job_marketplace_address
        if not self.mock_mode:
            try:
                self.web3 = Web3(Web3.HTTPProvider(sonic_rpc_url))
                self.account = self.web3.eth.account.from_key(sonic_private_key)
                self.address = self.account.address
                
                # Initialize contract
                self.job_marketplace = self.web3.eth.contract(
                    address=Web3.to_checksum_address(job_marketplace_address),
                    abi=JOB_MARKETPLACE_ABI
                )
                
                logger.info(f"Connected to Sonic chain: {self.web3.is_connected()}")
            except Exception as e:
                logger.error(f"Failed to connect to Sonic chain: {str(e)}")
                self.mock_mode = True
        
        if self.mock_mode:
            logger.warning("Agent initialized in mock mode - will use sample data")
        
        # Initialize ZerePyCLI for actions
        self.cli = ZerePyCLI()
        self._register_actions()
    
    def _register_actions(self):
        """Register custom actions with ZerePyCLI"""
        self.cli.register_action("get-job-details", self.get_job_details)
        self.cli.register_action("get-registered-freelancers", self.get_registered_freelancers)
        self.cli.register_action("get-ipfs-content", self.get_ipfs_content)
        self.cli.register_action("analyze-job-requirements", self.analyze_job_requirements)
        self.cli.register_action("match-freelancer-profile", self.match_freelancer_profile)
        self.cli.register_action("store-recommendations", self.store_recommendations)
    
    def recommend_freelancers(self, job_id: str) -> Dict[str, Any]:
        """
        Complete workflow to recommend freelancers for a job.
        
        Args:
            job_id: ID of the job in the JobMarketplace contract
            
        Returns:
            Dict containing job details, requirements, and recommended freelancers
        """
        try:
            logger.info(f"Processing job ID: {job_id}")
            
            # Step 1: Get job details
            job_result = self.get_job_details(job_id=job_id)
            if not job_result["success"]:
                return {"success": False, "error": job_result["error"]}
            
            job_details = job_result["job_details"]
            logger.info(f"Processing job: {job_details['title']}")
            
            # Step 2: Analyze job requirements
            req_result = self.analyze_job_requirements(description=job_details["description"])
            if not req_result["success"]:
                return {"success": False, "error": req_result["error"]}
            
            requirements = req_result["requirements"]
            
            # Step 3: Get registered freelancers
            freelancers_result = self.get_registered_freelancers()
            if not freelancers_result["success"]:
                return {"success": False, "error": freelancers_result["error"]}
            
            freelancers = freelancers_result["freelancers"]
            
            # Step 4: Process each freelancer
            matches = []
            
            for freelancer in freelancers:
                # Get IPFS profile
                ipfs_result = self.get_ipfs_content(ipfs_hash=freelancer["ipfsHash"])
                if not ipfs_result["success"]:
                    continue
                    
                try:
                    profile = json.loads(ipfs_result["content"])
                    profile["address"] = freelancer["address"]
                    profile["name"] = freelancer["name"]
                    
                    # Calculate match score
                    match_result = self.match_freelancer_profile(
                        requirements=requirements, 
                        profile=profile
                    )
                    
                    if match_result["success"]:
                        matches.append({
                            "address": freelancer["address"],
                            "name": freelancer["name"],
                            "score": match_result["match_result"]["score"],
                            "matching_skills": match_result["match_result"]["matching_skills"],
                            "missing_skills": match_result["match_result"]["missing_skills"],
                            "comments": match_result["match_result"]["comments"]
                        })
                except json.JSONDecodeError:
                    logger.error(f"Invalid JSON in IPFS content for {freelancer['ipfsHash']}")
                    continue
            
            # Sort by score (descending)
            matches.sort(key=lambda x: x["score"], reverse=True)
            
            # Get top recommendations (limit to 5)
            top_recommendations = matches[:5]
            
            # Store recommendations on-chain
            if top_recommendations:
                recommended_addresses = [rec["address"] for rec in top_recommendations]
                store_result = self.store_recommendations(
                    job_id=job_id, 
                    recommended_freelancers=recommended_addresses
                )
                
                if not store_result["success"]:
                    logger.warning(f"Failed to store recommendations: {store_result.get('error')}")
            
            # Save recommendations to file
            with open(f"job_{job_id}_recommendations.json", "w") as f:
                json.dump({
                    "job_details": job_details,
                    "requirements": requirements,
                    "recommendations": top_recommendations
                }, f, indent=2)
            
            logger.info(f"Generated {len(top_recommendations)} recommendations for job {job_id}")
            return {
                "success": True,
                "job_details": job_details,
                "requirements": requirements,
                "recommendations": top_recommendations
            }
            
        except Exception as e:
            logger.error(f"Error recommending freelancers: {str(e)}")
            return {"success": False, "error": f"Error recommending freelancers: {str(e)}"}
    
    def process_all_active_jobs(self) -> Dict[str, Any]:
        """Process all active jobs and generate recommendations"""
        try:
            # For MVP, we'll just process the test job
            logger.info("Processing test job")
            result = self.recommend_freelancers(job_id="test")
            
            return {
                "success": True,
                "processed_jobs": 1,
                "results": [result]
            }
            
        except Exception as e:
            logger.error(f"Error processing active jobs: {str(e)}")
            return {"success": False, "error": f"Error processing active jobs: {str(e)}"}
    
    def get_job_details(self, **kwargs) -> Dict[str, Any]:
        """Get job details by job ID"""
        try:
            job_id = kwargs.get("job_id")
            if not job_id:
                logger.error("No job ID provided")
                return {"success": False, "error": "No job ID provided"}
            
            # For testing: return mock data if job_id is "test"
            if job_id == "test":
                return {
                    "success": True,
                    "job_details": {
                        "title": "Smart Contract Developer for Sonic Blockchain",
                        "description": "We need an experienced Solidity developer to build a DeFi protocol on Sonic blockchain. Must have experience with AMMs, yield farming, and security best practices. Knowledge of Sonic blockchain architecture is a plus.",
                        "budget": 5000,
                        "employer": "0xEmployerAddress",
                        "freelancer": "0x0000000000000000000000000000000000000000",
                        "completed": False
                    }
                }
                
            if self.mock_mode:
                return {"success": False, "error": "Cannot get job details in mock mode"}
                
            # Convert string job ID to bytes32 if needed
            if isinstance(job_id, str) and job_id.startswith("0x"):
                job_id = bytes.fromhex(job_id[2:])
                
            job = self.job_marketplace.functions.jobs(job_id).call()
            
            job_details = {
                "title": job[0],
                "description": job[1],
                "budget": job[2],
                "employer": job[3],
                "freelancer": job[4],
                "completed": job[5]
            }
            
            logger.info(f"Retrieved job details for job ID: {job_id.hex() if isinstance(job_id, bytes) else job_id}")
            return {"success": True, "job_details": job_details}
            
        except Exception as e:
            logger.error(f"Failed to get job details: {str(e)}")
            return {"success": False, "error": f"Error getting job details: {str(e)}"}
    
    def get_registered_freelancers(self, **kwargs) -> Dict[str, Any]:
        """Get registered freelancers from events"""
        try:
            # For MVP, we'll use mock data
            # In a real implementation, you'd query events or use a more efficient method
            
            # Mock data for demonstration
            freelancers = [
                {
                    "address": "0x123abc...",
                    "name": "John Doe",
                    "ipfsHash": "QmT78zSuBmuS4z925WZfrqQ1qHaJ56DQaTfyMUF7F8ff5o"
                },
                {
                    "address": "0x456def...",
                    "name": "Jane Smith",
                    "ipfsHash": "QmW7Uc3vnh7J5aJ56DQaTfyMUF7F8ff5oT78zSuBmuS4z9"
                },
                {
                    "address": "0x789ghi...",
                    "name": "Michael Brown",
                    "ipfsHash": "QmX9Z8zSuBmuS4z925WZfrqQ1qHaJ56DQaTfyMUF7F8ff5o"
                }
            ]
            
            logger.info(f"Retrieved {len(freelancers)} freelancers")
            return {"success": True, "freelancers": freelancers}
            
        except Exception as e:
            logger.error(f"Failed to get freelancers: {str(e)}")
            return {"success": False, "error": f"Error getting freelancers: {str(e)}"}
    
    def get_ipfs_content(self, **kwargs) -> Dict[str, Any]:
        """Retrieve content from IPFS by hash"""
        try:
            ipfs_hash = kwargs.get("ipfs_hash")
            if not ipfs_hash:
                logger.error("No IPFS hash provided")
                return {"success": False, "error": "No IPFS hash provided"}
                
            # For testing, return mock data for specific hashes
            if ipfs_hash == "QmT78zSuBmuS4z925WZfrqQ1qHaJ56DQaTfyMUF7F8ff5o":
                return {"success": True, "content": json.dumps({
                    "name": "John Doe",
                    "skills": ["JavaScript", "Solidity", "React", "Web3.js", "Smart Contracts"],
                    "experienceYears": 5,
                    "hourlyRate": 75,
                    "rating": 4.8,
                    "completedJobs": 23,
                    "bio": "Blockchain developer with 5 years of experience in DeFi and NFT projects. Specialized in Solidity smart contract development and React frontends.",
                    "portfolio": [
                        {
                            "title": "DeFi Dashboard",
                            "description": "Built a dashboard for tracking DeFi investments across multiple protocols",
                            "link": "https://github.com/johndoe/defi-dashboard"
                        },
                        {
                            "title": "NFT Marketplace",
                            "description": "Developed smart contracts for an NFT marketplace with royalty support",
                            "link": "https://github.com/johndoe/nft-marketplace"
                        }
                    ],
                    "certifications": ["Ethereum Developer Certification", "Web3 Security Certification"],
                    "languages": ["English", "Spanish"],
                    "availability": "20 hours per week",
                    "timezone": "UTC-5"
                })}
            elif ipfs_hash == "QmW7Uc3vnh7J5aJ56DQaTfyMUF7F8ff5oT78zSuBmuS4z9":
                return {"success": True, "content": json.dumps({
                    "name": "Jane Smith",
                    "skills": ["Python", "Rust", "Blockchain Architecture", "Zero-Knowledge Proofs", "Sonic Blockchain"],
                    "experienceYears": 8,
                    "hourlyRate": 95,
                    "rating": 4.9,
                    "completedJobs": 31,
                    "bio": "Senior blockchain architect with expertise in zero-knowledge proofs and layer 2 scaling solutions. Recently worked on Sonic blockchain projects.",
                    "portfolio": [
                        {
                            "title": "ZK Rollup Implementation",
                            "description": "Developed a ZK rollup solution for a major DeFi protocol",
                            "link": "https://github.com/janesmith/zk-rollup"
                        },
                        {
                            "title": "Sonic Chain Integration",
                            "description": "Built cross-chain bridges for Sonic blockchain",
                            "link": "https://github.com/janesmith/sonic-bridge"
                        }
                    ],
                    "certifications": ["ZK Proof Specialist", "Rust Programming Advanced"],
                    "languages": ["English", "French", "German"],
                    "availability": "30 hours per week",
                    "timezone": "UTC+1"
                })}
            elif ipfs_hash == "QmX9Z8zSuBmuS4z925WZfrqQ1qHaJ56DQaTfyMUF7F8ff5o":
                return {"success": True, "content": json.dumps({
                    "name": "Michael Brown",
                    "skills": ["Go", "Rust", "Blockchain", "Smart Contracts", "Distributed Systems"],
                    "experienceYears": 7,
                    "hourlyRate": 90,
                    "rating": 4.7,
                    "completedJobs": 28,
                    "bio": "Senior blockchain engineer with a focus on Rust-based smart contracts and distributed systems.",
                    "portfolio": [
                        {
                            "title": "Cross-Chain Bridge",
                            "description": "Developed a cross-chain bridge connecting Ethereum and Polkadot.",
                            "link": "https://github.com/michaelbrown/cross-chain-bridge"
                        },
                        {
                            "title": "Zero-Knowledge Identity Protocol",
                            "description": "Implemented a zk-SNARK-based identity verification system.",
                            "link": "https://github.com/michaelbrown/zk-id"
                        }
                    ],
                    "certifications": ["Certified Blockchain Expert", "Rust Programming Certification"],
                    "languages": ["English", "German"],
                    "availability": "40 hours per week",
                    "timezone": "UTC+3"
                })}
            
            # For real implementation, fetch from IPFS
            try:
                url = f"{self.ipfs_gateway}/{ipfs_hash}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    logger.info(f"Retrieved content from IPFS: {ipfs_hash}")
                    return {"success": True, "content": response.text}
                else:
                    logger.error(f"Failed to retrieve content from IPFS: {ipfs_hash}")
                    return {"success": False, "error": f"Failed to retrieve content from IPFS: {response.status_code}"}
            except requests.RequestException:
                logger.error(f"Request to IPFS gateway failed for {ipfs_hash}")
                return {"success": False, "error": "IPFS gateway request failed"}
            
        except Exception as e:
            logger.error(f"Error retrieving IPFS content: {str(e)}")
            return {"success": False, "error": f"Error retrieving IPFS content: {str(e)}"}
    
    def analyze_job_requirements(self, **kwargs) -> Dict[str, Any]:
        """Extract key requirements from job description using Allora AI"""
        try:
            description = kwargs.get("description")
            if not description:
                logger.error("No job description provided")
                return {"success": False, "error": "No job description provided"}
            
            # Use Allora AI to extract requirements if available
            if self.allora_api_key:
                try:
                    # Prepare prompt for Allora
                    prompt = f"""
                    Extract the key skills and requirements from this job description:
                    
                    {description}
                    
                    Return a JSON object with the following structure:
                    {{
                        "skills": ["skill1", "skill2", ...],
                        "experience_years": number,
                        "job_type": "full-time/part-time/contract",
                        "location_requirements": "remote/onsite/hybrid"
                    }}
                    """
                    
                    # Call Allora API
                    headers = {
                        "Authorization": f"Bearer {self.allora_api_key}",
                        "Content-Type": "application/json"
                    }
                    
                    data = {
                        "prompt": prompt,
                        "max_tokens": 500,
                        "temperature": 0.3
                    }
                    
                    response = requests.post(
                        "https://api.allora.ai/v1/generate", 
                        headers=headers, 
                        json=data
                    )
                    response.raise_for_status()
                    
                    result = response.json()
                    requirements = json.loads(result.get("text", "{}"))
                    
                    logger.info(f"Extracted requirements using Allora: {requirements}")
                    return {
                        "success": True, 
                        "requirements": requirements
                    }
                except Exception as e:
                    logger.warning(f"Allora API call failed: {str(e)}. Using fallback.")
            
            # Fallback for testing or if Allora is not available
            logger.info("Using fallback requirements extraction")
            
            # Simple keyword extraction for skills
            keywords = [
                "Solidity", "DeFi", "AMM", "Yield Farming", "Smart Contracts", 
                "Security", "Sonic Blockchain", "JavaScript", "React", "Web3.js",
                "Python", "Rust", "Go", "TypeScript", "Node.js", "Docker",
                "AWS", "Azure", "Google Cloud", "DevOps", "CI/CD", "Testing",
                "Blockchain", "Ethereum", "Bitcoin", "Polkadot", "Cosmos",
                "Zero-Knowledge Proofs", "Layer 2", "Rollups", "NFT"
            ]
            
            # Extract skills by checking for keywords in the description
            skills = []
            for keyword in keywords:
                if keyword.lower() in description.lower():
                    skills.append(keyword)
            
            # Determine experience years (simple heuristic)
            experience_years = 3  # Default
            if "senior" in description.lower() or "experienced" in description.lower():
                experience_years = 5
            if "junior" in description.lower() or "entry" in description.lower():
                experience_years = 1
            
            # Determine job type
            job_type = "contract"  # Default
            if "full-time" in description.lower() or "full time" in description.lower():
                job_type = "full-time"
            if "part-time" in description.lower() or "part time" in description.lower():
                job_type = "part-time"
            
            # Determine location requirements
            location = "remote"  # Default
            if "onsite" in description.lower() or "on-site" in description.lower() or "on site" in description.lower():
                location = "onsite"
            if "hybrid" in description.lower():
                location = "hybrid"
            
            mock_requirements = {
                "skills": skills if skills else ["Solidity", "DeFi", "AMM", "Yield Farming", "Smart Contracts", "Security", "Sonic Blockchain"],
                "experience_years": experience_years,
                "job_type": job_type,
                "location_requirements": location
            }
            
            return {
                "success": True,
                "requirements": mock_requirements
            }
            
        except Exception as e:
            logger.error(f"Error analyzing job requirements: {str(e)}")
            return {"success": False, "error": f"Error analyzing job requirements: {str(e)}"}
    
def match_freelancer_profile(self, **kwargs) -> Dict[str, Any]:
    """Calculate match score between job requirements and freelancer profile"""
    try:
        requirements = kwargs.get("requirements")
        profile = kwargs.get("profile")
        
        if not requirements or not profile:
            logger.error("Missing requirements or profile data")
            return {"success": False, "error": "Missing requirements or profile data"}
        
        # Use Allora AI if available
        if self.allora_api_key:
            try:
                # Prepare prompt for Allora
                prompt = f"""
                Calculate a match score (0-100) between this job requirements and freelancer profile:
                
                Job Requirements:
                {json.dumps(requirements, indent=2)}
                
                Freelancer Profile:
                {json.dumps(profile, indent=2)}
                
                Return a JSON object with the following structure:
                {{
                    "score": number,
                    "matching_skills": ["skill1", "skill2", ...],
                    "missing_skills": ["skill1", "skill2", ...],
                    "comments": "string explaining the match"
                }}
                """
                
                # Call Allora API
                headers = {
                    "Authorization": f"Bearer {self.allora_api_key}",
                    "Content-Type": "application/json"
                }
                
                data = {
                    "prompt": prompt,
                    "max_tokens": 500,
                    "temperature": 0.3
                }
                
                response = requests.post(
                    "https://api.allora.ai/v1/generate", 
                    headers=headers, 
                    json=data
                )
                response.raise_for_status()
                
                result = response.json()
                match_result = json.loads(result.get("text", "{}"))
                
                logger.info(f"Match score using Allora: {match_result['score']}")
                return {
                    "success": True, 
                    "match_result": match_result
                }
            except Exception as e:
                logger.warning(f"Allora API call failed: {str(e)}. Using fallback.")
        
        # Fallback for testing or if Allora is not available
        logger.info("Using fallback matching algorithm")
        
        # Calculate a simple match score based on skills overlap
        req_skills = set(requirements.get("skills", []))
        profile_skills = set(profile.get("skills", []))
        
        matching_skills = list(req_skills.intersection(profile_skills))
        missing_skills = list(req_skills - profile_skills)
        
        # Simple score calculation: percentage of required skills that match
        if len(req_skills) > 0:
            skill_score = (len(matching_skills) / len(req_skills)) * 100
        else:
            skill_score = 100
        
        # Experience bonus/penalty
        exp_score = 0
        req_exp = requirements.get("experience_years", 0)
        profile_exp = profile.get("experienceYears", 0)
        
        if profile_exp >= req_exp:
            exp_score = 10  # Bonus for meeting or exceeding experience requirement
        else:
            exp_score = -10  # Penalty for not meeting experience requirement
        
        # Calculate final score
        score = min(100, max(0, int(skill_score + exp_score)))
        
        # Generate comment
        if score >= 80:
            comment = f"Excellent match with {len(matching_skills)} of {len(req_skills)} required skills."
        elif score >= 60:
            comment = f"Good match with most key skills, but missing {len(missing_skills)} required skills."
        else:
            comment = f"Not an ideal match, missing {len(missing_skills)} required skills."
            
        if profile_exp > req_exp:
            comment += f" Has {profile_exp} years of experience, exceeding the required {req_exp} years."
        elif profile_exp == req_exp:
            comment += f" Has exactly the required {req_exp} years of experience."
        else:
            comment += f" Has only {profile_exp} years of experience, less than the required {req_exp} years."
        
        match_result = {
            "score": score,
            "matching_skills": matching_skills,
            "missing_skills": missing_skills,
            "comments": comment
        }
        
        return {
            "success": True,
            "match_result": match_result
        }
        
    except Exception as e:
        logger.error(f"Error calculating match score: {str(e)}")
        return {"success": False, "error": f"Error calculating match score: {str(e)}"}

def store_recommendations(self, **kwargs) -> Dict[str, Any]:
    """Store AI recommendations for a job on-chain"""
    try:
        job_id = kwargs.get("job_id")
        recommended_freelancers = kwargs.get("recommended_freelancers", [])
        
        if not job_id or not recommended_freelancers:
            logger.error("Missing job ID or recommendations")
            return {"success": False, "error": "Missing job ID or recommendations"}
        
        # For testing mode, just log and return success
        if job_id == "test" or self.mock_mode:
            logger.info(f"TEST MODE: Would store {len(recommended_freelancers)} recommendations for job {job_id}")
            return {
                "success": True,
                "transaction_hash": "0xMockTransactionHashForTesting",
                "block_number": 12345678
            }
        
        # Convert string job ID to bytes32 if needed
        if isinstance(job_id, str) and job_id.startswith("0x"):
            job_id = bytes.fromhex(job_id[2:])
            
        # Build transaction
        tx = self.job_marketplace.functions.storeAIRecommendations(
            job_id,
            recommended_freelancers
        ).build_transaction({
            'from': self.address,
            'nonce': self.web3.eth.get_transaction_count(self.address),
            'gasPrice': self.web3.eth.gas_price,
            'chainId': self.web3.eth.chain_id
        })
        
        # Sign and send transaction
        signed_tx = self.account.sign_transaction(tx)
        tx_hash = self.web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for transaction receipt
        receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
        
        logger.info(f"Stored recommendations for job {job_id.hex() if isinstance(job_id, bytes) else job_id}")
        return {
            "success": receipt.status == 1,
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber
        }
        
    except Exception as e:
        logger.error(f"Failed to store recommendations: {str(e)}")
        return {"success": False, "error": f"Error storing recommendations: {str(e)}"}

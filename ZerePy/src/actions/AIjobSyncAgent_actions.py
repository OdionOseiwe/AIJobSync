import logging
import json
import os
import requests
from web3 import Web3
from dotenv import load_dotenv
from zerepy import register_action

load_dotenv()
logger = logging.getLogger("actions.freelancer_actions")

# Initialize Web3
rpc_url = os.getenv("ETH_RPC_URL")
web3 = Web3(Web3.HTTPProvider(rpc_url))

# Set up account
private_key = os.getenv("ETH_PRIVATE_KEY")
account = web3.eth.account.from_key(private_key)
address = account.address

# Load contract ABI (simplified for MVP)
JOB_MARKETPLACE_ADDRESS = os.getenv("JOB_MARKETPLACE_ADDRESS")
JOB_MARKETPLACE_ABI = [
    {
        "inputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
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
            {"internalType": "uint256", "name": "jobId", "type": "uint256"},
            {"internalType": "address[]", "name": "recommendations", "type": "address[]"}
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
    }
]

marketplace_contract = web3.eth.contract(
    address=web3.to_checksum_address(JOB_MARKETPLACE_ADDRESS),
    abi=JOB_MARKETPLACE_ABI
)

@register_action("get-job-details")
def get_job_details(agent, **kwargs):
    """Get job details by job ID"""
    try:
        job_id = kwargs.get("job_id")
        if not job_id:
            logger.error("No job ID provided")
            return {"success": False, "error": "No job ID provided"}
            
        job = marketplace_contract.functions.jobs(job_id).call()
        
        job_details = {
            "title": job[0],
            "description": job[1],
            "budget": job[2],
            "employer": job[3],
            "freelancer": job[4],
            "completed": job[5]
        }
        
        logger.info(f"Retrieved job details for job ID: {job_id}")
        return {"success": True, "job_details": job_details}
        
    except Exception as e:
        logger.error(f"Failed to get job details: {str(e)}")
        return {"success": False, "error": f"Error getting job details: {str(e)}"}

@register_action("get-ipfs-content")
def get_ipfs_content(agent, **kwargs):
    """Retrieve content from IPFS by hash"""
    try:
        ipfs_hash = kwargs.get("ipfs_hash")
        if not ipfs_hash:
            logger.error("No IPFS hash provided")
            return {"success": False, "error": "No IPFS hash provided"}
            
        gateway = os.getenv("IPFS_GATEWAY", "https://ipfs.io/ipfs/")
        url = f"{gateway}{ipfs_hash}"
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            logger.info(f"Retrieved content from IPFS: {ipfs_hash}")
            return {"success": True, "content": response.text}
        else:
            logger.error(f"Failed to retrieve content from IPFS: {ipfs_hash}")
            return {"success": False, "error": f"Failed to retrieve content from IPFS: {response.status_code}"}
        
    except Exception as e:
        logger.error(f"Error retrieving IPFS content: {str(e)}")
        return {"success": False, "error": f"Error retrieving IPFS content: {str(e)}"}

@register_action("analyze-job-requirements")
def analyze_job_requirements(agent, **kwargs):
    """Extract key requirements from job description using LLM"""
    try:
        description = kwargs.get("description")
        if not description:
            logger.error("No job description provided")
            return {"success": False, "error": "No job description provided"}
        
        # Use the LLM to extract requirements
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
        
        # Use the configured LLM connection
        llm_response = agent.connection_manager.connections["openai"].generate(prompt)
        
        # Parse the JSON response
        try:
            requirements = json.loads(llm_response)
            logger.info(f"Extracted requirements: {requirements}")
            return {"success": True, "requirements": requirements}
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            return {"success": False, "error": "Failed to parse requirements"}
        
    except Exception as e:
        logger.error(f"Error analyzing job requirements: {str(e)}")
        return {"success": False, "error": f"Error analyzing job requirements: {str(e)}"}

@register_action("match-freelancer-profile")
def match_freelancer_profile(agent, **kwargs):
    """Calculate match score between job requirements and freelancer profile"""
    try:
        requirements = kwargs.get("requirements")
        profile = kwargs.get("profile")
        
        if not requirements or not profile:
            logger.error("Missing requirements or profile data")
            return {"success": False, "error": "Missing requirements or profile data"}
        
        # Use the LLM to calculate a match score
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
        
        # Use the configured LLM connection
        llm_response = agent.connection_manager.connections["openai"].generate(prompt)
        
        # Parse the JSON response
        try:
            match_result = json.loads(llm_response)
            logger.info(f"Match score: {match_result['score']}")
            return {"success": True, "match_result": match_result}
        except json.JSONDecodeError:
            logger.error("Failed to parse LLM response as JSON")
            return {"success": False, "error": "Failed to parse match result"}
        
    except Exception as e:
        logger.error(f"Error calculating match score: {str(e)}")
        return {"success": False, "error": f"Error calculating match score: {str(e)}"}

@register_action("store-recommendations")
def store_recommendations(agent, **kwargs):
    """Store AI recommendations for a job on-chain"""
    try:
        job_id = kwargs.get("job_id")
        recommended_freelancers = kwargs.get("recommended_freelancers", [])
        
        if not job_id or not recommended_freelancers:
            logger.error("Missing job ID or recommendations")
            return {"success": False, "error": "Missing job ID or recommendations"}
            
        # Build transaction
        tx = marketplace_contract.functions.storeAIRecommendations(
            job_id,
            recommended_freelancers
        ).build_transaction({
            'from': address,
            'nonce': web3.eth.get_transaction_count(address),
            'gasPrice': web3.eth.gas_price,
            'chainId': web3.eth.chain_id
        })
        
        # Sign and send transaction
        signed_tx = account.sign_transaction(tx)
        tx_hash = web3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
        # Wait for transaction receipt
        receipt = web3.eth.wait_for_transaction_receipt(tx_hash)
        
        logger.info(f"Stored recommendations for job {job_id}")
        return {
            "success": receipt.status == 1,
            "transaction_hash": tx_hash.hex(),
            "block_number": receipt.blockNumber
        }
        
    except Exception as e:
        logger.error(f"Failed to store recommendations: {str(e)}")
        return {"success": False, "error": f"Error storing recommendations: {str(e)}"}

@register_action("recommend-freelancers")
def recommend_freelancers(agent, **kwargs):
    """Complete workflow to recommend freelancers for a job"""
    try:
        job_id = kwargs.get("job_id")
        if not job_id:
            logger.error("No job ID provided")
            return {"success": False, "error": "No job ID provided"}
            
        # Step 1: Get job details
        job_result = agent.execute_action("get-job-details", job_id=job_id)
        if not job_result["success"]:
            return {"success": False, "error": job_result["error"]}
        
        job_details = job_result["job_details"]
        logger.info(f"Processing job: {job_details['title']}")
        
        # Step 2: Analyze job requirements
        req_result = agent.execute_action("analyze-job-requirements", description=job_details["description"])
        if not req_result["success"]:
            return {"success": False, "error": req_result["error"]}
        
        requirements = req_result["requirements"]
        
        # Step 3: Get registered freelancers (using mock data for MVP)
        # In a real implementation, you'd query events or use a more efficient method
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
            }
        ]
        
        # Step 4: Process each freelancer
        matches = []
        for freelancer in freelancers:
            # Get IPFS profile
            ipfs_result = agent.execute_action("get-ipfs-content", ipfs_hash=freelancer["ipfsHash"])
            if not ipfs_result["success"]:
                continue
                
            try:
                profile = json.loads(ipfs_result["content"])
                profile["address"] = freelancer["address"]
                profile["name"] = freelancer["name"]
                
                # Calculate match score
                match_result = agent.execute_action(
                    "match-freelancer-profile", 
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
            store_result = agent.execute_action(
                "store-recommendations", 
                job_id=job_id, 
                recommended_freelancers=recommended_addresses
            )
            
            if not store_result["success"]:
                logger.warning(f"Failed to store recommendations: {store_result.get('error')}")
        
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

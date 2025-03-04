import argparse
import json
import logging
import os
from dotenv import load_dotenv
from zerepy import Agent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Import custom actions
from actions.freelancer_actions import *

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description='Freelancer Matching Agent')
    parser.add_argument('--job', type=str, help='Process a specific job ID')
    parser.add_argument('--monitor', action='store_true', help='Monitor for new jobs')
    
    args = parser.parse_args()
    
    # Initialize Zerepy agent
    agent = Agent()
    
    # Load the freelancer agent
    agent.load_agent("freelancer_agent")
    
    # Configure connections
    print("Configuring connections...")
    
    # Configure OpenAI connection
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        return
    
    agent.connection_manager.configure_connection("openai", {
        "api_key": openai_api_key
    })
    
    # Configure Ethereum connection
    eth_rpc_url = os.getenv("ETH_RPC_URL")
    eth_private_key = os.getenv("ETH_PRIVATE_KEY")
    if not eth_rpc_url or not eth_private_key:
        print("Error: Ethereum configuration not found in environment variables")
        return
    
    agent.connection_manager.configure_connection("ethereum", {
        "rpc_url": eth_rpc_url,
        "private_key": eth_private_key
    })
    
    if args.job:
        print(f"Processing job ID: {args.job}")
        result = agent.execute_action("recommend-freelancers", job_id=args.job)
        
        if result["success"]:
            print("\nJob processed successfully!")
            print(f"Job Title: {result['job_details']['title']}")
            print(f"Requirements: {', '.join(result['requirements']['skills'])}")
            
            print("\nTop Recommendations:")
            for i, rec in enumerate(result["recommendations"]):
                print(f"{i+1}. {rec['name']} (Score: {rec['score']})")
                print(f"   Address: {rec['address']}")
                print(f"   Matching Skills: {', '.join(rec['matching_skills'])}")
                print(f"   Missing Skills: {', '.join(rec['missing_skills'])}")
                print(f"   Comments: {rec['comments']}")
                print("")
            
            # Save results to file
            with open(f"job_{args.job}_recommendations.json", "w") as f:
                json.dump({
                    "job_details": result["job_details"],
                    "requirements": result["requirements"],
                    "recommendations": result["recommendations"]
                }, f, indent=2)
            
            print(f"\nRecommendations saved to job_{args.job}_recommendations.json")
        else:
            print(f"Error processing job: {result.get('error', 'Unknown error')}")
    
    elif args.monitor:
        monitor_jobs(agent)
    
    else:
        parser.print_help()

def monitor_jobs(agent):
    """Monitor for new job creation events"""
    import time
    from web3 import Web3
    
    # Initialize Web3
    rpc_url = os.getenv("ETH_RPC_URL")
    web3 = Web3(Web3.HTTPProvider(rpc_url))
    
    # Load contract
    marketplace_address = os.getenv("JOB_MARKETPLACE_ADDRESS")
    
    # Create event filter for JobCreated events (simplified for MVP)
    # In a real implementation, you'd use the proper event signature
    job_filter = web3.eth.filter({
        'address': marketplace_address,
        'topics': [web3.keccak(text='JobCreated(uint256,address)').hex()]
    })
    
    print("Monitoring for new jobs...")
    
    while True:
        try:
            # Check for new events
            for event in job_filter.get_new_entries():
                # In a real implementation, you'd decode the event data
                # For this MVP, we'll use a simplified approach
                job_id = "0x" + event['data'][:64].lstrip("0")
                print(f"New job detected: {job_id}")
                
                # Process the job
                result = agent.execute_action("recommend-freelancers", job_id=job_id)
                
                if result["success"]:
                    print(f"Successfully processed job {job_id}")
                else:
                    print(f"Failed to process job {job_id}: {result.get('error')}")
            
            # Sleep to avoid excessive polling
            time.sleep(60)
            
        except Exception as e:
            print(f"Error in job monitoring: {str(e)}")
            time.sleep(60)  # Wait before retrying

if __name__ == "__main__":
    main()

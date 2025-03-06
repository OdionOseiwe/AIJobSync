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
    parser = argparse.ArgumentParser(description='Freelancer Matching Agent for Sonic using Allora AI')
    parser.add_argument('--job', type=str, help='Process a specific job ID (bytes32 hex string)')
    parser.add_argument('--verify', type=str, help='Verify Allora proof for a job')
    
    args = parser.parse_args()
    
    # Initialize Zerepy agent
    agent = Agent()
    
    # Load the freelancer agent
    agent.load_agent("freelancer_agent")
    
    # Configure connections
    print("Configuring connections...")
    
    # Configure Allora connection
    allora_api_key = os.getenv("ALLORA_API_KEY")
    if not allora_api_key:
        print("Error: ALLORA_API_KEY not found in environment variables")
        return
    
    agent.connection_manager.configure_connection("allora", {
        "api_key": allora_api_key
    })
    
    # Configure Ethereum connection (for Sonic)
    sonic_rpc_url = os.getenv("SONIC_RPC_URL")
    sonic_private_key = os.getenv("SONIC_PRIVATE_KEY")
    if not sonic_rpc_url or not sonic_private_key:
        print("Error: Sonic blockchain configuration not found in environment variables")
        return
    
    agent.connection_manager.configure_connection("ethereum", {
        "rpc_url": sonic_rpc_url,
        "private_key": sonic_private_key
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
            print(f"Allora proofs saved to job_{args.job}_allora_proofs.json")
        else:
            print(f"Error processing job: {result.get('error', 'Unknown error')}")
    
    elif args.verify:
        print(f"Verifying Allora proof for job: {args.verify}")
        
        # Load the proof file
        try:
            with open(f"job_{args.verify}_allora_proofs.json", "r") as f:
                proofs = json.load(f)
                
            # Verify requirements proof
            req_verify_result = agent.execute_action("verify-allora-proof", proof=proofs["requirements_proof"])
            if req_verify_result["success"] and req_verify_result["verified"]:
                print("✅ Job requirements analysis proof verified")
            else:
                print("❌ Job requirements analysis proof verification failed")
                
            # Verify match proofs
            for i, match_proof in enumerate(proofs["match_proofs"]):
                match_verify_result = agent.execute_action("verify-allora-proof", proof=match_proof)
                if match_verify_result["success"] and match_verify_result["verified"]:
                    print(f"✅ Match proof {i+1} verified")
                else:
                    print(f"❌ Match proof {i+1} verification failed")
                    
            print("\nVerification complete!")
        except FileNotFoundError:
            print(f"Error: Proof file job_{args.verify}_allora_proofs.json not found")
        except Exception as e:
            print(f"Error verifying proofs: {str(e)}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

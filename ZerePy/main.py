import argparse
import json
import os
import logging
from dotenv import load_dotenv
from freelancer_agent import FreelancerAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("main")

load_dotenv()

def main():
    parser = argparse.ArgumentParser(description='Freelancer Matching Agent for Sonic Hackathon')
    parser.add_argument('--job', type=str, help='Job ID from the JobMarketplace contract')
    parser.add_argument('--test', action='store_true', help='Run in test mode with sample data')
    parser.add_argument('--all', action='store_true', help='Process all active jobs')
    
    args = parser.parse_args()
    
    # Initialize agent
    agent = FreelancerAgent(
        sonic_rpc_url=os.getenv("SONIC_RPC_URL", ""),
        sonic_private_key=os.getenv("SONIC_PRIVATE_KEY", ""),
        job_marketplace_address=os.getenv("JOB_MARKETPLACE_ADDRESS", ""),
        ipfs_gateway=os.getenv("IPFS_GATEWAY", "https://ipfs.io/ipfs"),
        allora_api_key=os.getenv("ALLORA_API_KEY", "")
    )
    
    if args.all:
        # Process all active jobs
        logger.info("Processing all active jobs...")
        result = agent.process_all_active_jobs()
        
        if result["success"]:
            logger.info(f"Successfully processed {result['processed_jobs']} jobs")
        else:
            logger.error(f"Error processing jobs: {result.get('error')}")
        
    else:
        # Get job ID
        job_id = "test" if args.test else args.job
        
        if not job_id:
            logger.error("No job ID provided. Use --job <job_id> or --test")
            return
        
        # Process job and get recommendations
        logger.info(f"Processing job ID: {job_id}")
        result = agent.recommend_freelancers(job_id)
        
        if result["success"]:
            print("\nJob processed successfully!")
            print(f"Job Title: {result['job_details']['title']}")
            print(f"Requirements: {', '.join(result['requirements']['skills'])}")
            
            print("\nTop Recommendations:")
            for i, rec in enumerate(result["recommendations"]):
                print(f"{i+1}. {rec['name']} (Match Score: {rec['score']}%)")
                print(f"   Matching Skills: {', '.join(rec['matching_skills'])}")
                print(f"   Missing Skills: {', '.join(rec['missing_skills'])}")
                print(f"   Comments: {rec['comments']}")
                print()
            
            print(f"Recommendations saved to job_{job_id}_recommendations.json")
        else:
            print(f"Error processing job: {result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    main()

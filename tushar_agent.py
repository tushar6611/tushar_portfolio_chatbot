# tushar_agent.py
from typing import Optional
import os
import sys
from tushar.common_tushar_funcs import get_resume_file_id, chatwith_tushar_agent, create_conversation
from tushar.prompt_tushar_agent import prompt_tushar_agent
from tushar.sharepoint_resume_handler import generate_resume_download_link
from common.appLogger import AppLogger
from common.secrets_env import load_secrets_env_variables

def main():
    print("\nTushar Portfolio Assistant Starting...")
    
    # Load secrets (set these in your environment or .env file)
    load_secrets_env_variables()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment!")
        sys.exit(1)

    # Logger setup
    logger_config = {
        "name": "tushar_agent",
        "log_file": "logs/tushar_agent.log",
        "log_level": "INFO",
        "log_to_stdout": True
    }
    logger = AppLogger(logger_config)

    # Agent config
    agent_cfg = {
        "model": "gpt-4o",
        "temperature": 0.3,
        "instructions": prompt_tushar_agent["instructions"],
        "name": prompt_tushar_agent["name"]
    }

    candidate_id = "tushar_001"  # Fixed for personal use
    file_id = get_resume_file_id(candidate_id, api_key, logger)

    print("Tushar: Hi! I'm Tushar, a Full-Stack Developer & AI Engineer.")
    print("Ask me about my skills, education, experience, or type 'resume' to download my CV!\n")

    client = None
    conversation_id = None

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        conversation_id = create_conversation(client, logger)

        while True:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("Tushar: Goodbye! Have a great day!")
                break

            if "resume" in user_input.lower() or "cv" in user_input.lower() or "download" in user_input.lower():
                link = generate_resume_download_link()
                print(f"\nTushar: Here's my latest resume:\n{link}\n")
                continue

            if not conversation_id or not file_id:
                print("Tushar: Sorry, I can't process that right now.")
                continue

            response, ok = chatwith_tushar_agent(
                conversation_id=conversation_id,
                user_input=user_input,
                agent_cfg=agent_cfg,
                file_id=file_id,
                client=client,
                logger=logger
            )

            if ok:
                print(f"Tushar: {response}\n")
            else:
                print(f"Error: {response}")

    except KeyboardInterrupt:
        print("\nTushar: Chat ended. See you later!")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print("Something went wrong. Check logs/tushar_agent.log")

if __name__ == "__main__":
    main()
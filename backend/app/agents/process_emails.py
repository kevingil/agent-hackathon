#!/usr/bin/env python3
"""
Agent workflow for processing test emails in .md format and placing orders.

This script reads test email files in markdown format, parses their content,
and uses the agent framework to process orders based on the email content.
"""
import asyncio
import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from openai import OpenAI

from app.agents.MCP.client import MCPClient
from app.agents.OrchestratorAgent import OrchestratorAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default directories
BASE_DIR = Path(__file__).parent.parent.parent.parent
TEST_EMAILS_DIR = BASE_DIR / 'test_emails'
PROCESSED_EMAILS_FILE = BASE_DIR / 'processed_emails.json'

# System prompt for the agent
SYSTEM_PROMPT = """You are an order processing assistant. Your task is to analyze emails and extract 
order information to create purchase orders. Be precise with quantities, product names, and other details.
When in doubt, ask for clarification."""

async def initialize_agent_service() -> Tuple[OrchestratorAgent, MCPClient]:
    """Initialize and return the OrchestratorAgent with MCP client integration."""
    try:
        logger.info("Initializing MCP client...")
        mcp_client = MCPClient()
        await mcp_client.connect()
        
        logger.info("Getting tools from MCP...")
        tools = await mcp_client.get_tools()
        logger.info(f"Loaded {len(tools)} tools from MCP")
        
        # Log the structure of the first tool for debugging
        if tools:
            logger.info(f"First tool structure: {json.dumps(tools[0], indent=2) if isinstance(tools[0], dict) else str(tools[0])}")
        
        logger.info("Initializing OpenAI client...")
        openai_client = OpenAI()
        
        # Initialize messages with system prompt
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Ensure tools is a list and log its structure
        if not isinstance(tools, list):
            logger.warning(f"Tools is not a list, converting to list. Type: {type(tools)}")
            tools = [tools] if tools is not None else []
            
        logger.info("Initializing OrchestratorAgent...")
        logger.info(f"Number of tools: {len(tools)}")
        if tools:
            logger.info(f"First tool structure: {json.dumps(tools[0], indent=2) if isinstance(tools[0], dict) else str(tools[0])}")
        
        try:
            # Create a copy of tools to avoid modifying the original
            agent_tools = [tool.copy() if hasattr(tool, 'copy') else tool for tool in tools]
            
            agent = OrchestratorAgent(
                dev_prompt=SYSTEM_PROMPT,
                mcp_client=mcp_client,
                llm=openai_client,
                messages=messages.copy(),
                tools=agent_tools,
                model_name="gpt-4.1-mini"
            )
            logger.info("Successfully initialized OrchestratorAgent")
            return agent, mcp_client
            
        except Exception as agent_init_error:
            logger.error(f"Error initializing OrchestratorAgent: {str(agent_init_error)}")
            logger.error(f"Agent initialization error type: {type(agent_init_error).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
            
    except Exception as e:
        logger.error(f"Failed to initialize agent service: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise

def load_processed_emails() -> Dict[str, str]:
    """Load the set of already processed emails."""
    if not PROCESSED_EMAILS_FILE.exists():
        return {}
    
    try:
        with open(PROCESSED_EMAILS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Error loading processed emails: {str(e)}")
        return {}

def mark_email_processed(email_path: str, status: str = "completed") -> None:
    """Mark an email as processed with the given status."""
    processed = load_processed_emails()
    processed[email_path] = {
        "status": status,
        "processed_at": datetime.now(timezone.utc).isoformat()
    }
    
    try:
        with open(PROCESSED_EMAILS_FILE, 'w') as f:
            json.dump(processed, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving processed emails: {str(e)}")

async def process_email_file(agent: OrchestratorAgent, file_path: Path) -> bool:
    """
    Process a single email file and place orders based on its content.
    
    Args:
        agent: Initialized OrchestratorAgent
        file_path: Path to the email file to process
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        logger.info(f"Starting to process email file: {file_path}")
        
        # Read the email content with error handling
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                email_content = f.read()
            logger.info(f"Successfully read email content, length: {len(email_content)} characters")
        except Exception as e:
            logger.error(f"Failed to read email file {file_path}: {str(e)}", exc_info=True)
            mark_email_processed(str(file_path), f"read_error: {str(e)}")
            return False
            
        print(f"\n{'='*80}\nProcessing email: {file_path.name}\n{'='*80}")
        
        try:
            # Process the email with the agent
            result = None
            logger.info("Starting to process email with agent...")
            
            try:
                async for chunk in agent.stream(email_content):
                    if 'content' in chunk and chunk['content']:
                        print(chunk['content'], end='', flush=True)
                    
                    if chunk.get('is_task_complete', False):
                        result = chunk
                        logger.info("Received task completion signal from agent")
                        break
                
                # Log tool execution history if available
                if result:
                    logger.info(f"Agent processing completed. Result keys: {list(result.keys())}")
                    if 'tool_history' in result and result['tool_history']:
                        logger.info(f"Tool history length: {len(result['tool_history'])}")
                        print("\n\nTool execution summary:")
                        print("-" * 40)
                        for i, tool in enumerate(result['tool_history'], 1):
                            status = "✓" if not tool.get('isError', False) else "✗"
                            logger.info(f"Tool {i}: {tool.get('tool', 'unknown')}, Success: {status}")
                            print(f"{status} {tool.get('tool', 'unknown')}({tool.get('arguments', '')})")
                            if tool.get('result'):
                                print(f"   → {tool['result']}")
                    
                    # Check for errors in the result
                    if result.get('error'):
                        logger.error(f"Agent reported an error: {result.get('error')}")
                        mark_email_processed(str(file_path), f"agent_error: {result.get('error')}")
                        return False
                
                # Mark the email as processed
                mark_email_processed(str(file_path), "completed")
                logger.info(f"Successfully processed email: {file_path.name}")
                print(f"\n{'='*80}\nSuccessfully processed: {file_path.name}\n{'='*80}")
                return True
                
            except Exception as stream_error:
                logger.error(f"Error during agent stream processing: {str(stream_error)}", exc_info=True)
                mark_email_processed(str(file_path), f"stream_error: {str(stream_error)}")
                return False
                
        except Exception as process_error:
            logger.error(f"Error in email processing: {str(process_error)}", exc_info=True)
            mark_email_processed(str(file_path), f"process_error: {str(process_error)}")
            return False
            
    except Exception as e:
        logger.critical(f"Unexpected error in process_email_file: {str(e)}", exc_info=True)
        mark_email_processed(str(file_path), f"unexpected_error: {str(e)}")
        return False

async def process_emails(directory: Optional[Path] = None) -> None:
    """
    Process .md files in the specified directory as test emails, one at a time.
    
    Args:
        directory: Directory containing test email files. Defaults to TEST_EMAILS_DIR.
    """
    if directory is None:
        directory = TEST_EMAILS_DIR
    
    # Ensure the directory exists
    if not directory.exists() or not directory.is_dir():
        logger.error(f"Test emails directory not found: {directory}")
        return
    
    # Find all .md files in the directory
    email_files = list(directory.glob('*.md'))
    
    if not email_files:
        logger.warning(f"No .md files found in {directory}")
        return
    
    # Load already processed emails
    processed_emails = load_processed_emails()
    
    # Filter out already processed emails and sort by modification time (oldest first)
    unprocessed_emails = [
        f for f in email_files 
        if str(f) not in processed_emails
    ]
    unprocessed_emails.sort(key=lambda f: f.stat().st_mtime)
    
    if not unprocessed_emails:
        logger.info("No unprocessed emails found.")
        return
    
    logger.info(f"Found {len(unprocessed_emails)} unprocessed email(s).")
    
    # Initialize agent service
    try:
        agent, mcp_client = await initialize_agent_service()
        
        # Process only the oldest unprocessed email
        email_to_process = unprocessed_emails[0]
        logger.info(f"Processing email: {email_to_process.name}")
        
        # Process the email
        success = await process_email_file(agent, email_to_process)
        
        if success:
            logger.info(f"Successfully processed email: {email_to_process.name}")
        else:
            logger.warning(f"Failed to process email: {email_to_process.name}")
        
    except Exception as e:
        logger.error(f"Error in email processing workflow: {str(e)}")
    finally:
        # Clean up
        if 'mcp_client' in locals():
            await mcp_client.disconnect()

if __name__ == "__main__":
    # Create necessary directories if they don't exist
    TEST_EMAILS_DIR.mkdir(exist_ok=True, parents=True)
    
    # Run the async main function
    asyncio.run(process_emails())

#!/usr/bin/env python3
"""
Agent workflow for processing test emails in .md format and placing orders.

This script reads test email files in markdown format, parses their content,
and uses the agent framework to process orders based on the email content.
"""
import os
import logging
from pathlib import Path
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Default directory for test emails
TEST_EMAILS_DIR = Path(__file__).parent.parent.parent.parent / 'test_emails'

def process_email_file(file_path: Path) -> bool:
    """
    Process a single email file and place orders based on its content.
    
    Args:
        file_path: Path to the email file to process
        
    Returns:
        bool: True if processing was successful, False otherwise
    """
    try:
        # Read the email content
        with open(file_path, 'r') as f:
            email_content = f.read()
            
        logger.info(f"Processing email file: {file_path}")
        
        # TODO: Implement email content parsing and order processing
        # This is where you would integrate with your agent framework
        # to process the email content and place orders
        
        # Example of what the processing might look like:
        # from app.agents.OrchestratorAgent import OrchestratorAgent
        # agent = OrchestratorAgent()
        # result = agent.process_email(email_content)
        # return result.success
        
        logger.info(f"Successfully processed email: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing email file {file_path}: {str(e)}")
        return False

def process_emails(directory: Optional[Path] = None) -> None:
    """
    Process all .md files in the specified directory as test emails.
    
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
    
    logger.info(f"Found {len(email_files)} email files to process")
    
    # Process each email file
    success_count = 0
    for email_file in email_files:
        if process_email_file(email_file):
            success_count += 1
    
    logger.info(f"Processing complete. Successfully processed {success_count}/{len(email_files)} files.")

if __name__ == "__main__":
    # Create test_emails directory if it doesn't exist
    TEST_EMAILS_DIR.mkdir(exist_ok=True)
    
    # Process emails
    process_emails()

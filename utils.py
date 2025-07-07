"""
Utility functions for the GitHub Project Uploader.
"""

import logging
import os
from pathlib import Path
from datetime import datetime

def setup_logging():
    """Setup logging configuration."""
    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_filename = logs_dir / f"webapp_launcher_{timestamp}.log"

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("Logging initialized")
    logger.info(f"Log file: {log_filename}")

    return logger

def validate_project_path(path):
    """Validate if the given path is suitable for a project."""
    if not path or not os.path.exists(path):
        return False, "Path does not exist"

    if not os.path.isdir(path):
        return False, "Path is not a directory"

    # Check if directory has any files
    try:
        files = list(os.listdir(path))
        if not files:
            return False, "Directory is empty"
    except PermissionError:
        return False, "Permission denied to access directory"

    return True, "Valid project path"

def clean_repo_name(name):
    """Clean repository name to be GitHub-compatible."""
    if not name:
        return ""

    # Remove invalid characters and replace with hyphens
    import re
    cleaned = re.sub(r'[^a-zA-Z0-9._-]', '-', name)

    # Remove leading/trailing hyphens and dots
    cleaned = cleaned.strip('-.')

    # Ensure it doesn't start with a dot
    if cleaned.startswith('.'):
        cleaned = cleaned[1:]

    # Limit length
    if len(cleaned) > 100:
        cleaned = cleaned[:100]

    return cleaned or "my-project"

def validate_environment():
    """Validate that required tools are available."""
    required_tools = {
        'git': 'Git is required for cloning repositories',
        'python': 'Python is required for running applications',
        'pip': 'pip is required for installing Python dependencies'
    }
    
    missing_tools = []
    
    for tool, description in required_tools.items():
        if not is_tool_available(tool):
            missing_tools.append(f"{tool}: {description}")
    
    return missing_tools

def is_tool_available(tool_name):
    """Check if a command-line tool is available."""
    import subprocess
    try:
        subprocess.run([tool_name, '--version'], 
                      capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def clean_temp_directory(temp_dir):
    """Clean up temporary directory."""
    import shutil
    try:
        if temp_dir and Path(temp_dir).exists():
            shutil.rmtree(temp_dir)
            return True
    except Exception as e:
        logging.error(f"Failed to clean temp directory {temp_dir}: {e}")
        return False

def format_repo_url(url):
    """Format repository URL to ensure it's in the correct format."""
    url = url.strip()
    
    # Add .git extension if not present
    if not url.endswith('.git') and 'github.com' in url:
        url += '.git'
    
    # Ensure https protocol
    if url.startswith('http://'):
        url = url.replace('http://', 'https://')
    elif not url.startswith('https://'):
        url = 'https://' + url
    
    return url

def get_app_version():
    """Get application version information."""
    return {
        'name': 'Universal Web App Launcher - Enhanced',
        'version': '1.0.0',
        'author': 'Generated Application',
        'description': 'A desktop GUI application for launching web applications from GitHub repositories'
    }
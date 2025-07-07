"""
GitHub repository handler and web application launcher.
"""

import requests
import subprocess
import os
import time
import logging
import configparser
from pathlib import Path
import tempfile
import shutil
import threading
from urllib.parse import urlparse
import json

class GitHubLauncher:
    """Handles GitHub repository operations and web application launching."""
    
    def __init__(self, config_file='config.ini'):
        """Initialize the GitHub launcher with configuration."""
        self.config = configparser.ConfigParser()
        self.config.read(config_file)
        
        # Load GitHub credentials
        self.username = self.config.get('GitHub', 'username', fallback='')
        self.password = self.config.get('GitHub', 'password', fallback='')
        self.token = self.config.get('GitHub', 'token', fallback='')
        self.api_base_url = self.config.get('GitHub', 'api_base_url', fallback='https://api.github.com')
        
        # Load application settings
        self.default_branch = self.config.get('Application', 'default_branch', fallback='main')
        self.timeout = self.config.getint('Launch', 'timeout_seconds', fallback=30)
        self.max_retries = self.config.getint('Launch', 'max_retries', fallback=3)
        
        # Session for API requests
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({'Authorization': f'token {self.token}'})
        elif self.username and self.password:
            self.session.auth = (self.username, self.password)
        
        self.logger = logging.getLogger(__name__)
    
    def update_auth(self, username, token):
        """Update authentication credentials for the session."""
        self.username = username
        self.token = token
        
        # Clear any existing authentication
        self.session.auth = None
        self.session.headers.pop('Authorization', None)
        
        # Set new token authentication
        if token:
            self.session.headers['Authorization'] = f'token {token}'
            self.logger.info(f"Updated authentication for user: {username}")
        
    def validate_github_url(self, url):
        """Validate if the provided URL is a valid GitHub repository URL."""
        try:
            parsed = urlparse(url)
            if parsed.netloc not in ['github.com', 'www.github.com']:
                return False, "URL must be a GitHub repository URL"
            
            # Extract owner and repo from path
            path_parts = parsed.path.strip('/').split('/')
            if len(path_parts) < 2:
                return False, "Invalid GitHub repository URL format"
            
            owner, repo = path_parts[0], path_parts[1]
            
            # Remove .git extension if present
            if repo.endswith('.git'):
                repo = repo[:-4]
            
            return True, {'owner': owner, 'repo': repo, 'url': url}
            
        except Exception as e:
            return False, f"Error parsing URL: {str(e)}"
    
    def check_repository_exists(self, owner, repo):
        """Check if the GitHub repository exists and is accessible."""
        try:
            api_url = f"{self.api_base_url}/repos/{owner}/{repo}"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                repo_data = response.json()
                return True, repo_data
            elif response.status_code == 404:
                return False, "Repository not found or not accessible"
            elif response.status_code == 401:
                return False, "Authentication failed - check credentials"
            else:
                return False, f"GitHub API error: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}"
    
    def get_repository_info(self, owner, repo):
        """Get detailed repository information."""
        try:
            api_url = f"{self.api_base_url}/repos/{owner}/{repo}"
            response = self.session.get(api_url, timeout=10)
            
            if response.status_code == 200:
                return True, response.json()
            else:
                return False, f"Failed to fetch repository info: {response.status_code}"
                
        except requests.exceptions.RequestException as e:
            return False, f"Network error: {str(e)}"
    
    def clone_repository(self, repo_url, destination):
        """Clone the repository to a local directory."""
        try:
            # Construct authenticated clone URL if credentials are available
            if self.username and self.password:
                parsed = urlparse(repo_url)
                auth_url = f"https://{self.username}:{self.password}@{parsed.netloc}{parsed.path}"
            elif self.token:
                parsed = urlparse(repo_url)
                auth_url = f"https://{self.token}@{parsed.netloc}{parsed.path}"
            else:
                auth_url = repo_url
            
            # Clone the repository
            cmd = ['git', 'clone', auth_url, destination]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                self.logger.info(f"Repository cloned successfully to {destination}")
                return True, f"Repository cloned to {destination}"
            else:
                error_msg = result.stderr or result.stdout
                self.logger.error(f"Git clone failed: {error_msg}")
                return False, f"Git clone failed: {error_msg}"
                
        except subprocess.TimeoutExpired:
            return False, "Clone operation timed out"
        except FileNotFoundError:
            return False, "Git is not installed or not in PATH"
        except Exception as e:
            return False, f"Clone error: {str(e)}"
    
    def detect_web_app_type(self, repo_path):
        """Detect the type of web application in the repository."""
        repo_path = Path(repo_path)
        
        # Check for common web app indicators
        if (repo_path / 'package.json').exists():
            return 'nodejs'
        elif (repo_path / 'requirements.txt').exists() or (repo_path / 'app.py').exists():
            return 'python'
        elif (repo_path / 'index.html').exists():
            return 'static'
        elif (repo_path / 'Dockerfile').exists():
            return 'docker'
        elif (repo_path / 'pom.xml').exists():
            return 'java'
        else:
            return 'unknown'
    
    def launch_web_app(self, repo_path, app_type, progress_callback=None):
        """Launch the web application based on its type."""
        try:
            repo_path = Path(repo_path)
            
            if progress_callback:
                progress_callback("Detecting application type...")
            
            if app_type == 'nodejs':
                return self._launch_nodejs_app(repo_path, progress_callback)
            elif app_type == 'python':
                return self._launch_python_app(repo_path, progress_callback)
            elif app_type == 'static':
                return self._launch_static_app(repo_path, progress_callback)
            else:
                return False, f"Unsupported application type: {app_type}"
                
        except Exception as e:
            return False, f"Launch error: {str(e)}"
    
    def _launch_nodejs_app(self, repo_path, progress_callback):
        """Launch a Node.js web application."""
        try:
            os.chdir(repo_path)
            
            if progress_callback:
                progress_callback("Installing Node.js dependencies...")
            
            # Install dependencies
            install_result = subprocess.run(['npm', 'install'], 
                                          capture_output=True, text=True, timeout=300)
            
            if install_result.returncode != 0:
                return False, f"npm install failed: {install_result.stderr}"
            
            if progress_callback:
                progress_callback("Starting Node.js application...")
            
            # Start the application
            start_cmd = ['npm', 'start']
            process = subprocess.Popen(start_cmd, stdout=subprocess.PIPE, 
                                     stderr=subprocess.PIPE, text=True)
            
            # Give the app time to start
            time.sleep(3)
            
            if process.poll() is None:
                return True, f"Node.js application started (PID: {process.pid})"
            else:
                stdout, stderr = process.communicate()
                return False, f"Application failed to start: {stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "npm install timed out"
        except FileNotFoundError:
            return False, "Node.js/npm is not installed or not in PATH"
        except Exception as e:
            return False, f"Node.js launch error: {str(e)}"
    
    def _launch_python_app(self, repo_path, progress_callback):
        """Launch a Python web application."""
        try:
            os.chdir(repo_path)
            
            if progress_callback:
                progress_callback("Installing Python dependencies...")
            
            # Install requirements if requirements.txt exists
            if (repo_path / 'requirements.txt').exists():
                install_result = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], 
                                              capture_output=True, text=True, timeout=300)
                
                if install_result.returncode != 0:
                    return False, f"pip install failed: {install_result.stderr}"
            
            if progress_callback:
                progress_callback("Starting Python application...")
            
            # Try to find and run the main Python file
            main_files = ['app.py', 'main.py', 'run.py', 'server.py']
            main_file = None
            
            for file in main_files:
                if (repo_path / file).exists():
                    main_file = file
                    break
            
            if not main_file:
                return False, "No main Python file found (app.py, main.py, run.py, server.py)"
            
            # Start the application
            process = subprocess.Popen(['python', main_file], 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Give the app time to start
            time.sleep(3)
            
            if process.poll() is None:
                return True, f"Python application started (PID: {process.pid})"
            else:
                stdout, stderr = process.communicate()
                return False, f"Application failed to start: {stderr}"
                
        except subprocess.TimeoutExpired:
            return False, "pip install timed out"
        except FileNotFoundError:
            return False, "Python/pip is not installed or not in PATH"
        except Exception as e:
            return False, f"Python launch error: {str(e)}"
    
    def _launch_static_app(self, repo_path, progress_callback):
        """Launch a static HTML application using Python's built-in server."""
        try:
            os.chdir(repo_path)
            
            if progress_callback:
                progress_callback("Starting static web server...")
            
            # Start Python's built-in HTTP server
            process = subprocess.Popen(['python', '-m', 'http.server', '5000'], 
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Give the server time to start
            time.sleep(2)
            
            if process.poll() is None:
                return True, f"Static web server started on port 5000 (PID: {process.pid})"
            else:
                stdout, stderr = process.communicate()
                return False, f"Server failed to start: {stderr}"
                
        except FileNotFoundError:
            return False, "Python is not installed or not in PATH"
        except Exception as e:
            return False, f"Static server launch error: {str(e)}"

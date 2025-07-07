
"""
GUI components for the GitHub Project Uploader.
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import tempfile
import logging
from pathlib import Path
import configparser
import os
import subprocess
import base64

from github_launcher import GitHubLauncher

class MainWindow:
    """Main application window."""
    
    def __init__(self, root):
        """Initialize the main window."""
        self.root = root
        self.launcher = GitHubLauncher()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        
        self.setup_window()
        self.create_widgets()
        
        # Application state
        self.is_uploading = False
        
    def setup_window(self):
        """Setup the main window properties."""
        # Window configuration
        width = self.config.getint('Application', 'window_width', fallback=800)
        height = self.config.getint('Application', 'window_height', fallback=600)
        title = "GitHub Project Uploader"
        
        self.root.title(title)
        self.root.geometry(f"{width}x{height}")
        self.root.resizable(True, True)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Set minimum size
        self.root.minsize(600, 400)
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure colors
        self.style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        self.style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        self.style.configure('Success.TLabel', foreground='green')
        self.style.configure('Error.TLabel', foreground='red')
        
    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights for responsiveness
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="GitHub Project Uploader", 
                               style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # GitHub credentials section
        creds_frame = ttk.LabelFrame(main_frame, text="GitHub Credentials", padding="10")
        creds_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        creds_frame.columnconfigure(1, weight=1)
        
        ttk.Label(creds_frame, text="Username:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.username_var = tk.StringVar()
        self.username_entry = ttk.Entry(creds_frame, textvariable=self.username_var, width=30)
        self.username_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(creds_frame, text="Personal Access Token:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(creds_frame, textvariable=self.password_var, show="*", width=30)
        self.password_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        
        # Add help text and test button
        help_text = ttk.Label(creds_frame, text="Get token at: github.com/settings/tokens", 
                             font=("Arial", 8), foreground="blue")
        help_text.grid(row=2, column=1, sticky=tk.W, padx=(0, 10), pady=(2, 0))
        
        self.test_auth_button = ttk.Button(creds_frame, text="Test Auth", 
                                          command=self.test_authentication)
        self.test_auth_button.grid(row=2, column=2, padx=(5, 5), pady=(2, 0))
        
        self.save_creds_button = ttk.Button(creds_frame, text="Save Credentials", 
                                           command=self.save_credentials)
        self.save_creds_button.grid(row=2, column=3, padx=(0, 10), pady=(2, 0))
        
        # Project upload section
        upload_frame = ttk.LabelFrame(main_frame, text="Project Upload", padding="10")
        upload_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        upload_frame.columnconfigure(1, weight=1)
        
        ttk.Label(upload_frame, text="Project Path:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.project_path_var = tk.StringVar()
        self.project_path_entry = ttk.Entry(upload_frame, textvariable=self.project_path_var, width=50)
        self.project_path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        self.browse_button = ttk.Button(upload_frame, text="Browse", 
                                       command=self.browse_project_folder)
        self.browse_button.grid(row=0, column=2, padx=(0, 10))
        
        ttk.Label(upload_frame, text="Repository Name:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.repo_name_var = tk.StringVar()
        self.repo_name_entry = ttk.Entry(upload_frame, textvariable=self.repo_name_var, width=50)
        self.repo_name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(0, 10), pady=(5, 0))
        
        self.upload_button = ttk.Button(upload_frame, text="Upload to GitHub", 
                                       command=self.upload_to_github)
        self.upload_button.grid(row=1, column=2, padx=(0, 10), pady=(5, 0))
        
        # Progress and status section
        status_frame = ttk.LabelFrame(main_frame, text="Status", padding="10")
        status_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(status_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status message
        self.status_var = tk.StringVar(value="Enter your GitHub credentials and select a project folder")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var)
        self.status_label.grid(row=2, column=0, sticky=tk.W)
        
        # Logs section
        logs_frame = ttk.LabelFrame(main_frame, text="Upload Logs", padding="10")
        logs_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        logs_frame.columnconfigure(0, weight=1)
        logs_frame.rowconfigure(0, weight=1)
        
        self.logs_text = scrolledtext.ScrolledText(logs_frame, height=10, width=70)
        self.logs_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, pady=(10, 0))
        
        self.clear_logs_button = ttk.Button(button_frame, text="Clear Logs", 
                                          command=self.clear_logs)
        self.clear_logs_button.grid(row=0, column=0)
        
        # Configure grid weights for the main sections
        main_frame.rowconfigure(4, weight=1)
        
        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Load saved credentials
        self.load_credentials()
        
        # Create .gitignore to prevent credential exposure
        self.create_gitignore()
        
    def log_message(self, message, level="INFO"):
        """Add a message to the logs display."""
        self.logs_text.config(state='normal')
        self.logs_text.insert(tk.END, f"[{level}] {message}\n")
        self.logs_text.see(tk.END)
        self.logs_text.config(state='disabled')
        
        # Also log to file
        if level == "ERROR":
            self.logger.error(message)
        elif level == "WARNING":
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def clear_logs(self):
        """Clear the logs display."""
        self.logs_text.config(state='normal')
        self.logs_text.delete(1.0, tk.END)
        self.logs_text.config(state='disabled')
    
    def update_progress(self, message):
        """Update the progress message."""
        self.progress_var.set(message)
        self.root.update_idletasks()
    
    def update_status(self, message, style=None):
        """Update the status message."""
        self.status_var.set(message)
        if style:
            self.status_label.config(style=style)
        else:
            self.status_label.config(style='TLabel')
        self.root.update_idletasks()
    
    def browse_project_folder(self):
        """Open file dialog to select project folder."""
        folder_path = filedialog.askdirectory(title="Select Project Folder")
        if folder_path:
            self.project_path_var.set(folder_path)
            self.log_message(f"Selected project folder: {folder_path}")
            
            # Auto-generate repository name from folder name
            folder_name = os.path.basename(folder_path)
            if not self.repo_name_var.get():
                self.repo_name_var.set(folder_name)
    
    def upload_to_github(self):
        """Upload project to GitHub."""
        if self.is_uploading:
            return
            
        # Validate inputs
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()
        project_path = self.project_path_var.get().strip()
        repo_name = self.repo_name_var.get().strip()
        
        if not username:
            messagebox.showerror("Error", "Please enter your GitHub username")
            return
        
        if not password:
            messagebox.showerror("Error", "Please enter your GitHub Personal Access Token")
            return
        
        if not project_path:
            messagebox.showerror("Error", "Please select a project folder")
            return
        
        if not repo_name:
            messagebox.showerror("Error", "Please enter a repository name")
            return
        
        if not os.path.exists(project_path):
            messagebox.showerror("Error", "Selected project folder does not exist")
            return
        
        self.is_uploading = True
        self.log_message(f"Starting upload to GitHub repository: {repo_name}")
        self.update_status("Uploading to GitHub...")
        self.progress_bar.start()
        self.upload_button.config(state='disabled')
        
        def upload_thread():
            try:
                # Update GitHub launcher with credentials
                self.launcher.update_auth(username, password)
                
                # Create repository on GitHub
                self.root.after(0, lambda: self.update_progress("Creating repository on GitHub..."))
                success, message = self.create_github_repository(repo_name)
                
                if not success:
                    self.root.after(0, lambda: self.upload_failed(f"Failed to create repository: {message}"))
                    return
                
                self.root.after(0, lambda: self.log_message(f"Repository created: {message}"))
                
                # Initialize git repository and push files
                self.root.after(0, lambda: self.update_progress("Initializing git repository..."))
                success, message = self.init_and_push_repository(project_path, username, repo_name)
                
                if success:
                    self.root.after(0, lambda: self.upload_succeeded(message))
                else:
                    self.root.after(0, lambda: self.upload_failed(message))
                    
            except Exception as e:
                self.root.after(0, lambda: self.upload_failed(f"Upload error: {str(e)}"))
        
        threading.Thread(target=upload_thread, daemon=True).start()
    
    def create_github_repository(self, repo_name):
        """Create a new repository on GitHub."""
        try:
            api_url = f"{self.launcher.api_base_url}/user/repos"
            repo_data = {
                "name": repo_name,
                "description": f"Project uploaded via GitHub Project Uploader",
                "private": False,
                "auto_init": False
            }
            
            response = self.launcher.session.post(api_url, json=repo_data, timeout=30)
            
            if response.status_code == 201:
                repo_info = response.json()
                return True, f"Repository '{repo_name}' created successfully"
            elif response.status_code == 422:
                error_data = response.json()
                if 'errors' in error_data:
                    for error in error_data['errors']:
                        if error.get('code') == 'already_exists':
                            return False, f"Repository '{repo_name}' already exists"
                return False, f"Repository '{repo_name}' validation failed: {error_data.get('message', 'Unknown error')}"
            elif response.status_code == 401:
                return False, "Authentication failed - check your Personal Access Token permissions (needs 'repo' scope)"
            elif response.status_code == 403:
                return False, "Permission denied - check your Personal Access Token has 'repo' scope enabled"
            else:
                return False, f"GitHub API error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return False, f"Error creating repository: {str(e)}"
    
    def find_git_executable(self):
        """Find Git executable in common Windows locations."""
        common_git_paths = [
            'git',  # Try PATH first
            r'C:\Program Files\Git\bin\git.exe',
            r'C:\Program Files\Git\cmd\git.exe',
            r'C:\Program Files (x86)\Git\bin\git.exe',
            r'C:\Program Files (x86)\Git\cmd\git.exe',
            r'C:\Git\bin\git.exe',
            r'C:\Git\cmd\git.exe'
        ]
        
        for git_path in common_git_paths:
            try:
                result = subprocess.run([git_path, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_message(f"Found Git at: {git_path}")
                    return git_path
            except (FileNotFoundError, subprocess.TimeoutExpired):
                continue
        
        return None

    def init_and_push_repository(self, project_path, username, repo_name):
        """Initialize git repository and push files to GitHub."""
        try:
            # Find Git executable
            git_cmd = self.find_git_executable()
            if not git_cmd:
                return False, "Git is not found. Please install Git from git-scm.com or check if it's in your PATH."
            
            # Change to project directory
            original_dir = os.getcwd()
            os.chdir(project_path)
            
            try:
                # Initialize git repository
                result = subprocess.run([git_cmd, 'init'], check=True, capture_output=True, text=True)
                self.log_message("Git repository initialized")
                
                # Configure git user (required for commits)
                subprocess.run([git_cmd, 'config', 'user.name', username], check=True, capture_output=True)
                subprocess.run([git_cmd, 'config', 'user.email', f'{username}@github.com'], check=True, capture_output=True)
                self.log_message("Git user configured")
                
                # Create a safe .gitignore to prevent token exposure
                gitignore_content = """# GitHub Project Uploader - Prevent credential exposure
config.ini
*.ini
*.log
__pycache__/
*.pyc
.env
"""
                gitignore_path = os.path.join(project_path, '.gitignore')
                if not os.path.exists(gitignore_path):
                    with open(gitignore_path, 'w') as f:
                        f.write(gitignore_content)
                    self.log_message("Created .gitignore to protect credentials")
                
                # Add all files
                result = subprocess.run([git_cmd, 'add', '.'], check=True, capture_output=True, text=True)
                self.log_message("Files added to git")
                
                # Check if there are any files to commit
                result = subprocess.run([git_cmd, 'status', '--porcelain'], capture_output=True, text=True)
                if not result.stdout.strip():
                    return False, "No files found to upload in the selected directory"
                
                # Commit files
                result = subprocess.run([git_cmd, 'commit', '-m', 'Initial commit'], check=True, capture_output=True, text=True)
                self.log_message("Files committed to git")
                
                # Set default branch to main
                subprocess.run([git_cmd, 'branch', '-M', 'main'], check=True, capture_output=True)
                self.log_message("Branch set to main")
                
                # Add remote origin using HTTPS with token authentication
                token = self.password_var.get()
                remote_url = f"https://{username}:{token}@github.com/{username}/{repo_name}.git"
                subprocess.run([git_cmd, 'remote', 'add', 'origin', remote_url], check=True, capture_output=True)
                self.log_message("Remote origin added")
                
                # Push to GitHub
                self.log_message("Pushing to GitHub...")
                env = os.environ.copy()
                env['GIT_TERMINAL_PROMPT'] = '0'  # Disable interactive prompts
                
                result = subprocess.run([git_cmd, 'push', '-u', 'origin', 'main'], 
                                      capture_output=True, text=True, timeout=60, env=env)
                
                if result.returncode != 0:
                    error_output = result.stderr or result.stdout
                    self.log_message(f"Push failed with error: {error_output}", "ERROR")
                    
                    if "authentication failed" in error_output.lower() or "invalid username or password" in error_output.lower():
                        return False, "Git push authentication failed. Please check your Personal Access Token permissions."
                    elif "repository not found" in error_output.lower():
                        return False, "Repository not found. Please check if the repository was created successfully."
                    elif "permission denied" in error_output.lower():
                        return False, "Permission denied. Please check your Personal Access Token has write permissions."
                    elif "remote: Support for password authentication was removed" in error_output:
                        return False, "Password authentication not supported. Please use a Personal Access Token instead of password."
                    else:
                        return False, f"Git push failed: {error_output}"
                
                self.log_message("Successfully pushed to GitHub")
                return True, f"Project successfully uploaded to https://github.com/{username}/{repo_name}"
                
            finally:
                os.chdir(original_dir)
                
        except subprocess.CalledProcessError as e:
            cmd_name = e.cmd[1] if len(e.cmd) > 1 else "unknown"
            error_output = ""
            
            if hasattr(e, 'stderr') and e.stderr:
                error_output = e.stderr
            elif hasattr(e, 'stdout') and e.stdout:
                error_output = e.stdout
            
            self.log_message(f"Git {cmd_name} command failed: {error_output}", "ERROR")
            
            if cmd_name == "commit":
                return False, "Git commit failed. Make sure the selected folder contains files to upload."
            elif cmd_name == "push":
                return False, "Git push failed. This might be due to authentication or network issues. Check your Personal Access Token permissions."
            else:
                return False, f"Git {cmd_name} operation failed: {error_output or str(e)}"
                
        except subprocess.TimeoutExpired:
            return False, "Git operation timed out. This might be due to network issues."
        except Exception as e:
            return False, f"Error during git operations: {str(e)}"
    
    def upload_succeeded(self, message):
        """Handle successful upload."""
        self.is_uploading = False
        self.progress_bar.stop()
        self.update_status("Upload completed successfully", 'Success.TLabel')
        self.log_message(f"Upload successful: {message}")
        self.upload_button.config(state='normal')
        
        messagebox.showinfo("Success", f"Project uploaded successfully!\n\n{message}")
    
    def test_authentication(self):
        """Test GitHub authentication."""
        username = self.username_var.get().strip()
        token = self.password_var.get().strip()
        
        if not username or not token:
            messagebox.showerror("Error", "Please enter both username and Personal Access Token")
            return
        
        self.log_message("Testing GitHub authentication...")
        self.update_status("Testing authentication...")
        self.progress_bar.start()
        self.test_auth_button.config(state='disabled')
        
        def test_thread():
            try:
                import requests
                
                # Test authentication with GitHub API
                headers = {'Authorization': f'token {token}'}
                response = requests.get('https://api.github.com/user', headers=headers, timeout=10)
                
                if response.status_code == 200:
                    user_data = response.json()
                    authenticated_user = user_data.get('login')
                    
                    if authenticated_user.lower() == username.lower():
                        self.root.after(0, lambda: self.auth_test_success(f"Authentication successful! Logged in as: {authenticated_user}"))
                    else:
                        self.root.after(0, lambda: self.auth_test_failed(f"Username mismatch: Token belongs to '{authenticated_user}', not '{username}'"))
                elif response.status_code == 401:
                    self.root.after(0, lambda: self.auth_test_failed("Invalid Personal Access Token"))
                else:
                    self.root.after(0, lambda: self.auth_test_failed(f"Authentication error: {response.status_code} - {response.text}"))
                    
            except Exception as e:
                self.root.after(0, lambda: self.auth_test_failed(f"Test error: {str(e)}"))
        
        threading.Thread(target=test_thread, daemon=True).start()
    
    def auth_test_success(self, message):
        """Handle successful authentication test."""
        self.progress_bar.stop()
        self.update_status("Authentication test passed", 'Success.TLabel')
        self.log_message(f"Auth test successful: {message}")
        self.test_auth_button.config(state='normal')
        messagebox.showinfo("Success", message)
    
    def auth_test_failed(self, error_message):
        """Handle failed authentication test."""
        self.progress_bar.stop()
        self.update_status("Authentication test failed", 'Error.TLabel')
        self.log_message(f"Auth test failed: {error_message}", "ERROR")
        self.test_auth_button.config(state='normal')
        messagebox.showerror("Authentication Failed", f"Authentication test failed:\n\n{error_message}")
    
    def encode_credentials(self, text):
        """Simple encoding for credential storage (NOT for security, just obfuscation)."""
        return base64.b64encode(text.encode()).decode()
    
    def decode_credentials(self, encoded_text):
        """Decode simple encoded credentials."""
        try:
            return base64.b64decode(encoded_text.encode()).decode()
        except:
            return ""
    
    def save_credentials(self):
        """Save credentials to config file."""
        username = self.username_var.get().strip()
        token = self.password_var.get().strip()
        
        if not username or not token:
            messagebox.showerror("Error", "Please enter both username and Personal Access Token before saving")
            return
        
        try:
            # Encode credentials for basic obfuscation
            encoded_username = self.encode_credentials(username)
            encoded_token = self.encode_credentials(token)
            
            # Update config with encoded credentials
            if not self.config.has_section('GitHub'):
                self.config.add_section('GitHub')
            
            self.config.set('GitHub', 'username_encoded', encoded_username)
            self.config.set('GitHub', 'token_encoded', encoded_token)
            
            # Save to file
            with open('config.ini', 'w') as config_file:
                self.config.write(config_file)
            
            self.log_message("Credentials saved successfully")
            messagebox.showinfo("Success", "Credentials saved to config.ini")
            
        except Exception as e:
            self.log_message(f"Failed to save credentials: {str(e)}", "ERROR")
            messagebox.showerror("Error", f"Failed to save credentials: {str(e)}")
    
    def load_credentials(self):
        """Load saved credentials from config file."""
        try:
            encoded_username = self.config.get('GitHub', 'username_encoded', fallback='')
            encoded_token = self.config.get('GitHub', 'token_encoded', fallback='')
            
            if encoded_username and encoded_token:
                username = self.decode_credentials(encoded_username)
                token = self.decode_credentials(encoded_token)
                
                if username and token:
                    self.username_var.set(username)
                    self.password_var.set(token)
                    self.log_message("Loaded saved credentials")
                
        except Exception as e:
            self.log_message(f"Failed to load credentials: {str(e)}", "WARNING")

    def upload_failed(self, error_message):
        """Handle failed upload."""
        self.is_uploading = False
        self.progress_bar.stop()
        self.update_status(f"Upload failed: {error_message}", 'Error.TLabel')
        self.log_message(f"Upload failed: {error_message}", "ERROR")
        self.upload_button.config(state='normal')
        
        messagebox.showerror("Upload Failed", f"Failed to upload project:\n\n{error_message}")
    
    def create_gitignore(self):
        """Create .gitignore file to prevent credential exposure."""
        try:
            gitignore_content = """# Configuration files with credentials
config.ini
*.ini

# Log files
logs/
*.log

# Python cache
__pycache__/
*.pyc
*.pyo

# IDE files
.vscode/
.idea/

# OS files
.DS_Store
Thumbs.db

# Distribution files
*.zip
dist/
build/

# Environment variables
.env
.env.local
"""
            if not os.path.exists('.gitignore'):
                with open('.gitignore', 'w') as f:
                    f.write(gitignore_content)
                self.log_message("Created .gitignore file to protect credentials")
        except Exception as e:
            self.log_message(f"Warning: Could not create .gitignore: {e}", "WARNING")

    def on_closing(self):
        """Handle application closing."""
        try:
            self.logger.info("Application closing")
            self.root.destroy()
        except Exception as e:
            self.logger.error(f"Error during application closing: {e}")
            self.root.destroy()

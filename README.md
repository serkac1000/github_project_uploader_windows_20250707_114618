# GitHub Project Uploader

A desktop GUI application for uploading local projects to GitHub repositories with username/password authentication.

## Overview

This application provides a simple graphical interface to upload your local project folders to GitHub repositories. It automatically creates the repository on GitHub, initializes git, and pushes all your files.

## Features

- **Simple GUI Interface**: Easy-to-use desktop application
- **GitHub Authentication**: Username/password authentication
- **Automatic Repository Creation**: Creates new repositories on GitHub
- **Git Integration**: Automatically initializes git and pushes files
- **Progress Tracking**: Real-time progress updates and logs
- **Cross-Platform**: Works on Windows, macOS, and Linux

## Requirements

### System Requirements
- Python 3.7 or higher
- Git installed and accessible from command line
- Internet connection for GitHub API access

### Python Dependencies
- `requests` - For GitHub API communication
- `tkinter` - For GUI (usually included with Python)

## Installation

### Windows Installation

1. **Install Python**: Download and install Python from [python.org](https://www.python.org/downloads/)
   - Make sure to check "Add Python to PATH" during installation

2. **Install Git**: Download and install Git from [git-scm.com](https://git-scm.com/download/win)

3. **Extract the Project**: Extract the zip file to a folder on your computer

4. **Install Dependencies**: Open Command Prompt in the project folder and run:
   ```cmd
   pip install requests
   ```

## Usage

### Starting the Application

1. Open Command Prompt in the project folder
2. Run the application:
   ```cmd
   python main.py
   ```

### Using the Application

1. **Get GitHub Personal Access Token**:
   - Go to GitHub.com → Settings → Developer settings → Personal access tokens
   - Click "Generate new token" (classic)
   - Select scopes: `repo` (full repository access)
   - Copy the generated token

2. **Enter GitHub Credentials**:
   - Username: Your GitHub username
   - Personal Access Token: Paste the token from step 1

3. **Select Project to Upload**:
   - Click "Browse" to select your project folder
   - Enter a repository name (auto-filled from folder name)

4. **Upload Project**:
   - Click "Upload to GitHub"
   - Monitor progress in the logs section
   - Success message will show the GitHub repository URL

### Important Notes

- **GitHub Authentication**: You MUST use a Personal Access Token (not password)
- **Token Permissions**: Ensure your token has `repo` scope for repository creation
- **Repository Names**: Must be unique in your GitHub account
- **File Exclusions**: The application uploads all files in the selected folder
- **Git Requirements**: Git must be installed and accessible from command line

## Configuration

The application uses `config.ini` for configuration:

```ini
[GitHub]
username = demo_user
password = demo_password
token = 
api_base_url = https://api.github.com

[Application]
window_width = 800
window_height = 600
window_title = GitHub Project Uploader
log_level = INFO
default_branch = main
```

## Troubleshooting

### Common Issues

1. **"Git is not installed"**:
   - Download and install Git from [git-scm.com](https://git-scm.com/download/win)
   - During installation, select "Git from the command line and also from 3rd-party software"
   - Restart your computer after installation
   - Test by opening Command Prompt and typing: `git --version`

2. **"Authentication failed"**:
   - Check your username and Personal Access Token
   - Ensure your token has `repo` scope permissions
   - Generate a new token at github.com/settings/tokens

3. **"Repository already exists"**:
   - Choose a different repository name
   - Or delete the existing repository on GitHub

4. **"Permission denied"**:
   - Check your GitHub account permissions
   - Ensure you have rights to create repositories

### Getting Help

If you encounter issues:
1. Check the logs in the application
2. Verify your GitHub credentials
3. Ensure Git is properly installed
4. Check your internet connection

## File Structure

```
github-project-uploader/
├── main.py              # Application entry point
├── gui_components.py    # GUI interface components
├── github_launcher.py   # GitHub API and Git operations
├── utils.py            # Utility functions
├── config.ini          # Configuration file
├── logs/               # Application logs
├── test_gui.py         # Simple GUI test
└── README.md           # This file
```

## Security Considerations

- **Personal Access Tokens**: Required for GitHub authentication (passwords no longer supported)
- **Credentials**: Never share your GitHub username or Personal Access Token
- **Public Repositories**: By default, repositories are created as public
- **File Content**: Review files before uploading to avoid sharing sensitive information

## Development

### Project Architecture

The application follows a modular design:
- `main.py`: Application bootstrap and initialization
- `gui_components.py`: Tkinter-based GUI interface
- `github_launcher.py`: GitHub API integration and Git operations
- `utils.py`: Logging and utility functions

### Extending the Application

To add new features:
1. Follow the existing code structure
2. Update configuration in `config.ini`
3. Add logging for debugging
4. Test thoroughly before deployment

## License

This project is provided as-is for educational and personal use.

## Version History

- v1.0.0: Initial release with basic upload functionality
- Features: GitHub authentication, repository creation, file upload, progress tracking
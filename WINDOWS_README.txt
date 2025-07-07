# GitHub Project Uploader - Windows Package

## Quick Start

1. **Extract this zip file** to a folder on your computer

2. **Install Python** (if not already installed):
   - Download from: https://www.python.org/downloads/
   - During installation, CHECK "Add Python to PATH"

3. **Install Git** (if not already installed):
   - Download from: https://git-scm.com/download/win
   - During installation, select "Git from the command line and also from 3rd-party software"

4. **Install dependencies**:
   - Open Command Prompt in the extracted folder
   - Run: `pip install requests`

5. **Run the application**:
   - Double-click `run_windows.bat`
   - Or open Command Prompt and run: `python main.py`

## Usage

1. **Get GitHub Personal Access Token**:
   - Go to github.com/settings/tokens
   - Create new token with "repo" permissions
   - Copy the token

2. **Use the application**:
   - Enter your GitHub username and token
   - Click "Test Auth" to verify
   - Select a project folder to upload
   - Click "Upload to GitHub"

## Troubleshooting

- If Git is not found, run `python check_git.py` to test
- Make sure your Personal Access Token has "repo" scope
- Check the logs section for detailed error messages

## Security Note

- Your credentials are stored locally in config.ini
- Never share your Personal Access Token
- The .gitignore file prevents accidental credential upload

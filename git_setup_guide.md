# Git Setup Guide for Windows

## If Git is installed but not working:

### Option 1: Add Git to System PATH
1. Open "Environment Variables" in Windows
2. Edit the "Path" variable in System Variables
3. Add these paths (if they exist):
   - `C:\Program Files\Git\bin`
   - `C:\Program Files\Git\cmd`
4. Restart your computer
5. Test by opening Command Prompt and typing: `git --version`

### Option 2: Using Git Bash (Your Current Setup)
If you have Git Bash at `C:\Program Files\Git\git-bash.exe`, the application will automatically find and use the Git executable.

The application now searches these common locations:
- System PATH
- `C:\Program Files\Git\bin\git.exe`
- `C:\Program Files\Git\cmd\git.exe`
- `C:\Program Files (x86)\Git\bin\git.exe`
- `C:\Program Files (x86)\Git\cmd\git.exe`

## Testing Git Installation
Run `check_git.py` to verify Git is properly detected.

## Common Issues
- **Git Bash vs Git Command**: Git Bash is the terminal, but we need the Git command-line tools
- **PATH Issues**: Git tools need to be in Windows PATH or in standard installation directories
- **Installation Type**: During Git installation, select "Git from the command line and also from 3rd-party software"

## Quick Fix
If Git is installed but not detected:
1. Reinstall Git from https://git-scm.com/download/win
2. During installation, select "Git from the command line and also from 3rd-party software"
3. Restart your computer
4. The application will automatically find Git
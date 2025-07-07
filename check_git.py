#!/usr/bin/env python3
"""
Check if Git is installed and accessible
"""

import subprocess
import sys

def find_git():
    """Find Git executable in common locations."""
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
                return git_path, result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            continue
    
    return None, None

def check_git():
    """Check if Git is installed and accessible."""
    git_path, version = find_git()
    
    if git_path:
        print("✓ Git is installed and accessible")
        print(f"Location: {git_path}")
        print(f"Version: {version}")
        return True
    else:
        print("✗ Git is not found in common locations")
        print("\nSearched locations:")
        print("- System PATH")
        print("- C:\\Program Files\\Git\\")
        print("- C:\\Program Files (x86)\\Git\\")
        print("- C:\\Git\\")
        print("\nTo fix this:")
        print("1. Download Git from: https://git-scm.com/download/win")
        print("2. During installation, select 'Git from the command line and also from 3rd-party software'")
        print("3. Restart your computer after installation")
        print("4. Test again by running this script")
        return False

if __name__ == "__main__":
    print("Checking Git installation...")
    success = check_git()
    
    if not success:
        print("\nGit is required for the GitHub Project Uploader to work properly.")
        input("Press Enter to exit...")
    else:
        print("\nGit is ready! You can now use the GitHub Project Uploader.")
        input("Press Enter to exit...")
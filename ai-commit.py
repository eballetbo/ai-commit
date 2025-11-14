#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
AI-Powered Git Commit Message Generator (git-ai-commit)

Git Custom Command: Install as 'git-ai-commit' in PATH to use as 'git ai-commit'

This script analyzes your staged git changes, learns from your repository's
commit history, and uses the Gemini AI model to generate a suggested
commit message.

**Prerequisites:**
1.  You must have the `google-generativeai` library installed:
    pip install google-generativeai

2.  You need to configure your Gemini API key. The script will prompt you
    to enter it if it's not found in the GOOGLE_API_KEY environment variable.

**How it works:**
1.  Checks for staged changes.
2.  Fetches the last 10 commit messages to learn the project's style.
3.  Gets the `git diff --staged` output, which shows the actual code changes.
4.  Sends the diff and the commit history examples to the Gemini API.
5.  Presents the AI-generated commit message for your approval.
6.  If you approve, it performs the commit.

**Installation as a Git Command:**
  1. chmod +x git-ai-commit
  2. sudo cp git-ai-commit /usr/local/bin/
     (or ~/.local/bin if ~/.local/bin is in PATH)
  3. Then run: git ai-commit
"""

import os
import subprocess
import sys
import getpass
import argparse

try:
    import google.generativeai as genai
except ImportError:
    print("Error: The 'google-generativeai' library is not installed.")
    print("Please install it by running: pip install google-generativeai")
    sys.exit(1)

# --- Configuration ---
# You can get your API key from Google AI Studio: https://aistudio.google.com/app/apikey
API_KEY_ENV_VAR = "GOOGLE_API_KEY"

# --- Helper Functions ---

def run_command(command):
    """Executes a shell command and returns its output."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: `{command}`")
        print(f"Stderr: {e.stderr.strip()}")
        sys.exit(1)

def is_git_repository():
    """Check if the current directory is a git repository."""
    return os.path.isdir('.git')

def get_api_key():
    """Gets the Gemini API key from environment variables or prompts the user."""
    api_key = os.getenv(API_KEY_ENV_VAR)
    if not api_key:
        print("Google API Key for Gemini not found in environment variables.")
        try:
            api_key = getpass.getpass("Please enter your API key: ")
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled by user.")
            sys.exit(1)
    if not api_key:
        print("API Key is required to proceed.")
        sys.exit(1)
    return api_key


def generate_commit_message(diff, history):
    """Generates a commit message using the Gemini AI."""
    print("🤖 Calling the AI to generate a commit message... (this may take a moment)")

    api_key = get_api_key()
    try:
        genai.configure(api_key=api_key)
    except Exception as e:
        print(f"Error configuring Gemini AI: {e}")
        sys.exit(1)

    # For this script, we'll use the gemini-2.5-flash model
    model = genai.GenerativeModel('gemini-2.5-flash')

    prompt = f"""
    You are an expert programmer and git user. Your task is to write a clear, concise, and conventional commit message.

    Analyze the following 'git diff --staged' output and the recent commit history to understand the context and the project's conventions.

    **Recent Commit History (for style reference):**
    ---
    {history}
    ---

    **Staged Changes (git diff):**
    ---
    {diff}
    ---

    **Instructions:**
    1. Write a commit message that accurately summarizes the changes.
    2. Follow the conventional commit format if it seems to be used in the history (e.g., `feat:`, `fix:`, `refactor:`, `docs:`, `chore:`).
    3. The first line (subject) should be 100 characters or less.
    4. After the subject, add a blank line, followed by a more detailed body explaining the 'what' and 'why' of the changes if necessary.
    5. Do not include any introductory text like "Here is the commit message:". Just provide the raw commit message.
    """
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"An error occurred while communicating with the Gemini API: {e}")
        print("Please check your API key and network connection.")
        sys.exit(1)


# --- Main Logic ---

def main():
    """Main function to run the commit message generator."""
    parser = argparse.ArgumentParser(
        description="AI-powered commit message generator for Git",
        add_help=True
    )
    parser.add_argument(
        "--auto-commit",
        action="store_true",
        help="Automatically commit without asking for confirmation"
    )
    parser.add_argument(
        "--no-sign",
        action="store_true",
        help="Don't sign the commit (default is to sign with -s)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Generate message but don't commit"
    )

    args = parser.parse_args()

    print("🚀 Starting AI Commit Assistant...")

    if not is_git_repository():
        print("Error: This is not a git repository.")
        print("Usage: git ai-commit [--auto-commit] [--no-sign] [--dry-run]")
        sys.exit(1)

    # 1. Get the staged diff
    print("🔍 Analyzing staged changes...")
    staged_diff = run_command("git diff --staged")
    if not staged_diff:
        print("⚠️ No staged changes found.")
        print("Stage your changes first with: git add <files>")
        sys.exit(0)

    # 2. Get commit history for context
    print("📚 Learning from recent commit history...")
    try:
        commit_history = run_command("git log -n 10 --pretty=format:'%s'")
    except SystemExit:
        # This can happen in a new repo with no commits yet
        print("Could not retrieve commit history. Assuming this is a new repository.")
        commit_history = "No previous commits found. This is likely the initial commit."

    # 3. Generate the commit message
    suggested_message = generate_commit_message(staged_diff, commit_history)

    print("\n" + "="*60)
    print("✨ AI-Generated Commit Message Suggestion ✨")
    print("="*60)
    print(suggested_message)
    print("="*60)

    # 4. Handle auto-commit or user confirmation
    should_commit = args.auto_commit

    if not args.dry_run and not should_commit:
        try:
            user_approval = input("\nDo you want to commit with this message? (y/n/e to edit): ").lower()
            should_commit = user_approval == 'y'

            if user_approval == 'e':
                print("\n📝 Aborting automatic commit.")
                print("You can now edit the message and commit manually.")
                print("To commit manually, run: git commit")
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            print("\n\nOperation cancelled by user.")
            sys.exit(1)

    if args.dry_run:
        print("\n📋 [DRY RUN] Would commit with the above message")
        sys.exit(0)

    if should_commit:
        print("\n✅ Committing...")
        # Build the git commit command as a list to avoid shell quoting issues.
        commit_cmd = ["git", "commit"]
        if not args.no_sign:
            commit_cmd.append("-s")
        # Use -F - to read the commit message from stdin so that
        # newlines and quotes in the suggested message are preserved
        # and do not get interpreted by the shell.
        commit_cmd.extend(["-F", "-"])
        try:
            proc = subprocess.run(
                commit_cmd,
                input=suggested_message,
                text=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print("\n🎉 Commit successful!")
            print(run_command("git log -n 1 --pretty=oneline"))
        except subprocess.CalledProcessError as e:
            print("Error executing git commit:")
            # Prefer showing stderr for debugging
            print(e.stderr.strip())
            sys.exit(1)
    else:
        print("\n❌ Commit aborted by user.")
        print("Changes are still staged. To unstage, run: `git reset`")


if __name__ == "__main__":
    main()

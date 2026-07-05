#!/usr/bin/env python3
import os
import json
import re
import datetime
import urllib.parse
import subprocess

# Simple terminal styling
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(title):
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {title} ==={Colors.ENDC}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")

def print_warning(msg):
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")

def slugify(text):
    # Convert to lowercase, replace non-alphanumeric with hyphen, strip duplicate/edge hyphens
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def get_github_pages_base():
    try:
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"], 
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        
        # Match git@github.com:username/repo.git or https://github.com/username/repo.git
        match = re.search(r'(?:github\.com[:/])([^/]+)/([^.]+)(?:\.git)?', remote_url)
        if match:
            username = match.group(1)
            repo = match.group(2)
            return f"https://{username}.github.io/{repo}"
    except Exception:
        pass
    return None

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print_warning(f"Failed to parse config.json ({e}). Using defaults.")
    return {}

def run_git_commands(folder_name, app_name):
    # Check if git is initialized
    if not os.path.exists(".git"):
        print_warning("Local git repository not found in current directory. Skipping git operations.")
        return

    try:
        # Check git status
        subprocess.check_call(["git", "status"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        print_error("Git is not fully set up or working in this shell.")
        return

    commit_opt = input(f"\n{Colors.BOLD}Do you want to stage and commit the generated pages? (y/N): {Colors.ENDC}").strip().lower()
    if commit_opt == 'y' or commit_opt == 'yes':
        try:
            subprocess.check_call(["git", "add", folder_name])
            commit_msg = f"Add privacy policy and support page for {app_name}"
            subprocess.check_call(["git", "commit", "-m", commit_msg])
            print_success(f"Committed changes successfully with message: '{commit_msg}'")
            
            # Check for remote
            has_remote = False
            try:
                subprocess.check_call(["git", "remote", "show", "origin"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                has_remote = True
            except:
                pass
            
            if has_remote:
                push_opt = input(f"{Colors.BOLD}Do you want to push to GitHub right now? (y/N): {Colors.ENDC}").strip().lower()
                if push_opt == 'y' or push_opt == 'yes':
                    print("Pushing to remote origin...")
                    # Get current branch
                    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
                    subprocess.check_call(["git", "push", "origin", branch])
                    print_success("Pushed to GitHub!")
            else:
                print_warning("No Git remote 'origin' configured. Push to GitHub manually once configured.")
        except Exception as e:
            print_error(f"Git execution failed: {e}")

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config = load_config()

    print_header("iOS Page Generator for GitHub Pages")

    # 1. Ask for App Name
    while True:
        app_name = input(f"{Colors.BOLD}Enter the iOS App Name (e.g. Bolt Pro: Browser and Docs): {Colors.ENDC}").strip()
        if app_name:
            break
        print_error("App Name cannot be empty.")

    app_slug = slugify(app_name)
    app_initial = app_name[0].upper() if app_name else "A"

    # 2. Setup default configurations
    default_dev_name = config.get("developer_name", "Wathek")
    default_email = config.get("developer_email", "mer.wathek@gmail.com")
    default_features = config.get("default_features", [
        "Bug reports",
        "Feature requests",
        "General feedback"
    ])

    # 3. Interactive confirmations/overrides
    dev_name = input(f"Developer Name [{default_dev_name}]: ").strip() or default_dev_name
    dev_email = input(f"Developer Email [{default_email}]: ").strip() or default_email
    
    # Date formatting
    today_date = datetime.date.today().strftime("%B %d, %Y")
    current_year = str(datetime.date.today().year)
    last_updated = input(f"Last Updated [{today_date}]: ").strip() or today_date

    # Features / Support Topics input
    print(f"\nDefault support topics:")
    for f in default_features:
        print(f"  - {f}")
    custom_topics_opt = input(f"\nUse these default support topics? (Y/n): ").strip().lower()
    
    topics = []
    if custom_topics_opt == 'n' or custom_topics_opt == 'no':
        print("Enter support topics one by one (press Enter on empty line to finish):")
        while True:
            t = input("> ").strip()
            if not t:
                break
            topics.append(t)
        if not topics:
            topics = default_features
    else:
        topics = default_features

    # Render topics to HTML list tags
    topics_html_list = []
    for t in topics:
        topics_html_list.append(f'<div class="topic-tag">{t}</div>')
    topics_html = "\n                ".join(topics_html_list)

    # 4. Read templates
    privacy_template_path = os.path.join(script_dir, 'templates', 'privacy_template.html')
    support_template_path = os.path.join(script_dir, 'templates', 'support_template.html')

    if not os.path.exists(privacy_template_path) or not os.path.exists(support_template_path):
        print_error("HTML templates directory or templates not found. Ensure templates/ exists and contains templates.")
        return

    with open(privacy_template_path, 'r') as f:
        privacy_template = f.read()

    with open(support_template_path, 'r') as f:
        support_template = f.read()

    # 5. Replace placeholders
    email_subject = urllib.parse.quote(f"Support Request: {app_name}")

    privacy_html = privacy_template\
        .replace("{{APP_NAME}}", app_name)\
        .replace("{{APP_INITIAL}}", app_initial)\
        .replace("{{DEVELOPER_NAME}}", dev_name)\
        .replace("{{DEVELOPER_EMAIL}}", dev_email)\
        .replace("{{LAST_UPDATED}}", last_updated)\
        .replace("{{YEAR}}", current_year)

    support_html = support_template\
        .replace("{{APP_NAME}}", app_name)\
        .replace("{{APP_INITIAL}}", app_initial)\
        .replace("{{DEVELOPER_NAME}}", dev_name)\
        .replace("{{DEVELOPER_EMAIL}}", dev_email)\
        .replace("{{LAST_UPDATED}}", last_updated)\
        .replace("{{YEAR}}", current_year)\
        .replace("{{SUPPORT_TOPICS}}", topics_html)\
        .replace("{{EMAIL_SUBJECT}}", email_subject)

    # 6. Create app directory
    target_dir = os.path.join(script_dir, app_slug)
    os.makedirs(target_dir, exist_ok=True)

    # Write files
    privacy_out_path = os.path.join(target_dir, 'privacy.html')
    support_out_path = os.path.join(target_dir, 'support.html')

    with open(privacy_out_path, 'w') as f:
        f.write(privacy_html)

    with open(support_out_path, 'w') as f:
        f.write(support_html)

    print_success(f"Generated Privacy Policy: {privacy_out_path}")
    print_success(f"Generated Support Page: {support_out_path}")

    # 7. Print expected URLs
    base_url = get_github_pages_base()
    if base_url:
        print(f"\n{Colors.CYAN}{Colors.BOLD}Expected live URLs (once pushed to GitHub):{Colors.ENDC}")
        print(f"Privacy Policy: {Colors.UNDERLINE}{base_url}/{app_slug}/privacy.html{Colors.ENDC}")
        print(f"Support Page:   {Colors.UNDERLINE}{base_url}/{app_slug}/support.html{Colors.ENDC}")
    else:
        print(f"\n{Colors.WARNING}GitHub pages base URL could not be auto-detected. Once remote is set up, they will look like:{Colors.ENDC}")
        print(f"Privacy: https://<username>.github.io/<repo-name>/{app_slug}/privacy.html")
        print(f"Support: https://<username>.github.io/<repo-name>/{app_slug}/support.html")

    # 8. Git automation
    run_git_commands(app_slug, app_name)

if __name__ == "__main__":
    main()

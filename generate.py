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
    UNDERLINE = '\033[4m'

def print_header(title):
    print(f"\n{Colors.HEADER}{Colors.BOLD}=== {title} ==={Colors.ENDC}\n")

def print_success(msg):
    try:
        print(f"{Colors.GREEN}✓ {msg}{Colors.ENDC}")
    except UnicodeEncodeError:
        print(f"{Colors.GREEN}[OK] {msg}{Colors.ENDC}")

def print_warning(msg):
    try:
        print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")
    except UnicodeEncodeError:
        print(f"{Colors.WARNING}[WARN] {msg}{Colors.ENDC}")

def print_error(msg):
    try:
        print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")
    except UnicodeEncodeError:
        print(f"{Colors.FAIL}[ERROR] {msg}{Colors.ENDC}")

def slugify(text):
    # Convert to lowercase, replace non-alphanumeric with hyphen, strip duplicate/edge hyphens
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def get_github_repo_info():
    """Extract username and repo name from git remote origin to build jsDelivr & Pages URLs."""
    try:
        remote_url = subprocess.check_output(
            ["git", "config", "--get", "remote.origin.url"], 
            stderr=subprocess.DEVNULL
        ).decode("utf-8").strip()
        
        # Match git@github.com:username/repo.git or https://github.com/username/repo.git
        match = re.search(r'(?:github\.com[:/])([^/]+)/([^.]+)(?:\.git)?', remote_url)
        if match:
            return match.group(1), match.group(2)
    except Exception:
        pass
    return "City-Shadow", "apps-pages"

def get_jsdelivr_url(username, repo, branch, path):
    """Generate high-speed, rate-limit-free jsDelivr CDN URL for raw files."""
    return f"https://cdn.jsdelivr.net/gh/{username}/{repo}@{branch}/{path}"

def ensure_nojekyll(script_dir):
    nojekyll_path = os.path.join(script_dir, '.nojekyll')
    if not os.path.exists(nojekyll_path):
        with open(nojekyll_path, 'w', encoding='utf-8') as f:
            f.write('')
        print_success("Created root .nojekyll file for fast static asset & JSON delivery.")

def update_app_ads_txt(script_dir, publisher_id):
    if not publisher_id:
        return
    clean_pub = publisher_id.strip()
    if not clean_pub.startswith("pub-"):
        clean_pub = f"pub-{clean_pub}"
    
    admob_line = f"google.com, {clean_pub}, DIRECT, f08c47fec0942fa0\n"
    app_ads_path = os.path.join(script_dir, 'app-ads.txt')
    
    existing_lines = []
    if os.path.exists(app_ads_path):
        with open(app_ads_path, 'r', encoding='utf-8') as f:
            existing_lines = f.readlines()
            
    if admob_line not in existing_lines:
        with open(app_ads_path, 'a', encoding='utf-8') as f:
            if not existing_lines:
                f.write("# Google Mobile Ads app-ads.txt\n")
            f.write(admob_line)
        print_success(f"Added publisher {clean_pub} to root app-ads.txt")

def generate_remote_configs(script_dir, app_slug, config, services, selected_account):
    if not services.get("admob", False):
        return None, None

    test_units = config.get("admob_test_units", {})
    android_test = test_units.get("android", {})
    ios_test = test_units.get("ios", {})

    dev_template_path = os.path.join(script_dir, 'templates', 'app_config_dev_template.json')
    prod_template_path = os.path.join(script_dir, 'templates', 'app_config_prod_template.json')

    if not os.path.exists(dev_template_path) or not os.path.exists(prod_template_path):
        print_warning("app_config templates not found. Skipping remote config generation.")
        return None, None

    with open(dev_template_path, 'r', encoding='utf-8') as f:
        dev_json = f.read()

    with open(prod_template_path, 'r', encoding='utf-8') as f:
        prod_json = f.read()

    # Populate dev.json with official test IDs
    dev_json = dev_json\
        .replace("{{ANDROID_TEST_APP_OPEN_ID}}", android_test.get("app_open", "ca-app-pub-3940256099942544/9257395921"))\
        .replace("{{ANDROID_TEST_INTERSTITIAL_ID}}", android_test.get("interstitial", "ca-app-pub-3940256099942544/1033173712"))\
        .replace("{{ANDROID_TEST_REWARDED_ID}}", android_test.get("rewarded", "ca-app-pub-3940256099942544/5224354917"))\
        .replace("{{IOS_TEST_APP_OPEN_ID}}", ios_test.get("app_open", "ca-app-pub-3940256099942544/5575463023"))\
        .replace("{{IOS_TEST_INTERSTITIAL_ID}}", ios_test.get("interstitial", "ca-app-pub-3940256099942544/4411468910"))\
        .replace("{{IOS_TEST_REWARDED_ID}}", ios_test.get("rewarded", "ca-app-pub-3940256099942544/1712485313"))

    print(f"\n{Colors.BOLD}AdMob Configuration:{Colors.ENDC}")
    has_live_units = input("Do you have live AdMob unit IDs to enter now? (y/N): ").strip().lower() in ['y', 'yes']

    def prompt_id(label, default_val):
        if not has_live_units:
            return default_val
        val = input(f"Enter {label} [{default_val}]: ").strip()
        return val if val else default_val

    primary_ad_type = input("Default Primary Action Ad Type ('rewarded' or 'interstitial') [rewarded]: ").strip().lower()
    if primary_ad_type not in ["rewarded", "interstitial"]:
        primary_ad_type = "rewarded"

    # Populate prod.json
    prod_json = prod_json\
        .replace("{{PROD_PRIMARY_AD_TYPE}}", primary_ad_type)\
        .replace("{{PROD_SECONDARY_AD_TYPE}}", "rewarded")\
        .replace("{{ANDROID_PROD_APP_OPEN_ID}}", prompt_id("Android Prod App Open ID", "ca-app-pub-3940256099942544/9257395921"))\
        .replace("{{ANDROID_PROD_PRIMARY_ACTION_ID}}", prompt_id("Android Prod Primary Interstitial/Rewarded ID", "ca-app-pub-3940256099942544/1033173712"))\
        .replace("{{ANDROID_PROD_SECONDARY_ACTION_ID}}", prompt_id("Android Prod Secondary Interstitial ID", "ca-app-pub-3940256099942544/1033173712"))\
        .replace("{{ANDROID_PROD_DETAIL_ACTION_ID}}", prompt_id("Android Prod Detail Interstitial ID", "ca-app-pub-3940256099942544/1033173712"))\
        .replace("{{ANDROID_PROD_REWARDED_ID}}", prompt_id("Android Prod Rewarded Unlock ID", "ca-app-pub-3940256099942544/5224354917"))\
        .replace("{{IOS_PROD_APP_OPEN_ID}}", prompt_id("iOS Prod App Open ID", "ca-app-pub-3940256099942544/5575463023"))\
        .replace("{{IOS_PROD_PRIMARY_ACTION_ID}}", prompt_id("iOS Prod Primary Interstitial/Rewarded ID", "ca-app-pub-3940256099942544/4411468910"))\
        .replace("{{IOS_PROD_SECONDARY_ACTION_ID}}", prompt_id("iOS Prod Secondary Interstitial ID", "ca-app-pub-3940256099942544/4411468910"))\
        .replace("{{IOS_PROD_DETAIL_ACTION_ID}}", prompt_id("iOS Prod Detail Interstitial ID", "ca-app-pub-3940256099942544/4411468910"))\
        .replace("{{IOS_PROD_REWARDED_ID}}", prompt_id("iOS Prod Rewarded Unlock ID", "ca-app-pub-3940256099942544/1712485313"))

    target_dir = os.path.join(script_dir, app_slug)
    os.makedirs(target_dir, exist_ok=True)

    dev_path = os.path.join(target_dir, 'dev.json')
    prod_path = os.path.join(target_dir, 'prod.json')

    with open(dev_path, 'w', encoding='utf-8') as f:
        f.write(dev_json)

    with open(prod_path, 'w', encoding='utf-8') as f:
        f.write(prod_json)

    print_success(f"Generated Dev Config: {dev_path}")
    print_success(f"Generated Prod Config: {prod_path}")

    pub_id = selected_account.get("admob_publisher_id")
    if pub_id:
        update_app_ads_txt(script_dir, pub_id)

    return dev_path, prod_path

def load_config():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, 'config.json')
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
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

    commit_opt = input(f"\n{Colors.BOLD}Do you want to stage and commit the generated pages and configs? (y/N): {Colors.ENDC}").strip().lower()
    if commit_opt in ['y', 'yes']:
        try:
            subprocess.check_call(["git", "add", folder_name])
            if os.path.exists("apps.md"):
                subprocess.check_call(["git", "add", "apps.md"])
            if os.path.exists("app-ads.txt"):
                subprocess.check_call(["git", "add", "app-ads.txt"])
            if os.path.exists(".nojekyll"):
                subprocess.check_call(["git", "add", ".nojekyll"])

            commit_msg = f"Add privacy, support, and remote ad configs for {app_name}"
            subprocess.check_call(["git", "commit", "-m", commit_msg])
            print_success(f"Committed changes successfully with message: '{commit_msg}'")
            
            # Check for remote
            has_remote = False
            try:
                subprocess.check_call(["git", "remote", "show", "origin"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                has_remote = True
            except Exception:
                pass
            
            if has_remote:
                push_opt = input(f"{Colors.BOLD}Do you want to push to GitHub right now? (y/N): {Colors.ENDC}").strip().lower()
                if push_opt in ['y', 'yes']:
                    print("Pushing to remote origin...")
                    branch = subprocess.check_output(["git", "rev-parse", "--abbrev-ref", "HEAD"]).decode("utf-8").strip()
                    subprocess.check_call(["git", "push", "origin", branch])
                    print_success("Pushed to GitHub! jsDelivr CDN is live immediately.")
            else:
                print_warning("No Git remote 'origin' configured. Push to GitHub manually.")
        except Exception as e:
            print_error(f"Git execution failed: {e}")

def append_to_apps_list(app_name, app_slug, username, repo, branch, folder_exists, has_ads=True):
    if folder_exists:
        print_warning("Skipped appending to apps.md because the folder already exists.")
        return

    script_dir = os.path.dirname(os.path.abspath(__file__))
    apps_md_path = os.path.join(script_dir, 'apps.md')

    pages_domain = f"https://{username}.github.io/{repo}"
    privacy_url = f"{pages_domain}/{app_slug}/privacy.html"
    support_url = f"{pages_domain}/{app_slug}/support.html"

    # jsDelivr CDN URLs for remote JSON
    dev_config_url = f"https://cdn.jsdelivr.net/gh/{username}/{repo}@{branch}/{app_slug}/dev.json"
    prod_config_url = f"https://cdn.jsdelivr.net/gh/{username}/{repo}@{branch}/{app_slug}/prod.json"

    file_exists = os.path.exists(apps_md_path)

    try:
        with open(apps_md_path, 'a', encoding='utf-8') as f:
            if not file_exists:
                f.write("# Generated App Pages & Configs\n\n")
            f.write(f"## {app_name}\n")
            f.write(f"- **Privacy Policy:** {privacy_url}\n")
            f.write(f"- **Support Page:**   {support_url}\n")
            if has_ads:
                f.write(f"- **Dev Remote Config (jsDelivr CDN):**  {dev_config_url}\n")
                f.write(f"- **Prod Remote Config (jsDelivr CDN):** {prod_config_url}\n")
            f.write("\n")
        print_success(f"Appended URLs to {os.path.basename(apps_md_path)}")
    except Exception as e:
        print_warning(f"Could not append to apps.md: {e}")

def prompt_accounts(config):
    """Prompt the user to pick a developer account (name + email pair)."""
    accounts = config.get("accounts")
    if not accounts:
        accounts = [
            {"name": config.get("developer_name", "Akram"), "email": config.get("developer_email", "mer.wathek@gmail.com"), "admob_publisher_id": "pub-3588263773495662"},
            {"name": "Hanine", "email": "HanineMeraghni2002@icloud.com", "admob_publisher_id": ""},
            {"name": "Islam", "email": "islambelhardi12@gmail.com", "admob_publisher_id": ""}
        ]
    print(f"\n{Colors.BOLD}Choose developer account:{Colors.ENDC}")
    for i, acc in enumerate(accounts, 1):
        pub_info = f" (AdMob: {acc['admob_publisher_id']})" if acc.get('admob_publisher_id') else ""
        print(f"  {i}) {acc['name']} / {acc['email']}{pub_info}")
    default_idx = 1
    while True:
        choice = input(f"Enter choice [{default_idx}]: ").strip()
        if not choice:
            idx = default_idx - 1
            break
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(accounts):
                break
            print_error(f"Please enter a number between 1 and {len(accounts)}.")
        except ValueError:
            print_error("Invalid input. Please enter a number.")
    acc = accounts[idx]
    print_success(f"Using account: {acc['name']} / {acc['email']}")
    return acc

def prompt_services(config):
    """Prompt the user to select which third-party services to declare."""
    service_options = [
        ("admob", "Google AdMob (Mobile Ads)"),
        ("iap", "Apple App Store / Google Play (In-App Purchases)"),
        ("supabase", "Supabase (Cloud Database)"),
    ]
    default_services = config.get("default_services", ["admob", "iap", "supabase"])
    default_indices = [i + 1 for i, (key, _) in enumerate(service_options) if key in default_services]

    print(f"\n{Colors.BOLD}Select third-party services to declare in the Privacy Policy:{Colors.ENDC}")
    for i, (_, label) in enumerate(service_options, 1):
        print(f"  {i}) {label}")
    hint = ",".join(str(i) for i in default_indices) if default_indices else "none"
    sel = input(f"Enter numbers (comma/space separated), 'none', or Enter for default [{hint}]: ").strip()

    if sel.lower() == "none":
        selected = []
    elif not sel:
        selected = default_indices
    else:
        selected = []
        for part in re.split(r"[,\s]+", sel):
            part = part.strip()
            if not part:
                continue
            try:
                n = int(part)
                if 1 <= n <= len(service_options):
                    selected.append(n)
            except ValueError:
                pass
        selected = list(dict.fromkeys(selected))

    keys = {i + 1: k for i, (k, _) in enumerate(service_options)}
    enabled = {k: False for k, _ in service_options}
    for n in selected:
        enabled[keys[n]] = True

    chosen_labels = [service_options[n - 1][1] for n in selected]
    if chosen_labels:
        print_success(f"Services selected: {', '.join(chosen_labels)}")
    else:
        print_warning("No third-party services will be declared.")
    return enabled

def apply_conditional_blocks(html, services):
    """Remove or keep conditional template blocks based on selected services."""
    ads = services.get("admob", False)
    iap = services.get("iap", False)
    supabase = services.get("supabase", False)
    blocks = [
        ("ADS_BLOCK", ads),
        ("IAP_BLOCK", iap),
        ("SUPABASE_BLOCK", supabase),
        ("MONETIZATION_BLOCK", ads or iap),
        ("ANY_SERVICE_BLOCK", ads or iap or supabase),
        ("FAQ_BLOCK", ads or iap),
    ]
    for name, enabled in blocks:
        start = "{{" + name + "_START}}"
        end = "{{" + name + "_END}}"
        if enabled:
            html = html.replace(start, "").replace(end, "")
        else:
            pattern = re.compile(re.escape(start) + ".*?" + re.escape(end), re.DOTALL)
            html = pattern.sub("", html)
    return html

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config = load_config()

    # Ensure root .nojekyll file exists
    ensure_nojekyll(script_dir)

    print_header("iOS & Mobile App Hub Generator (Pages + jsDelivr CDN)")

    # 1. Ask for App Name
    while True:
        app_name = input(f"{Colors.BOLD}Enter the App Name (e.g. Bolt Pro: Browser and Docs): {Colors.ENDC}").strip()
        if app_name:
            break
        print_error("App Name cannot be empty.")

    app_slug = slugify(app_name)
    app_initial = app_name[0].upper() if app_name else "A"

    # 2. Setup default configurations
    default_features = config.get("default_features", [
        "In-App purchases, billing, and restoring premium features",
        "Ad playback and reward issues",
        "App features and functionality",
        "Performance or crash reports",
        "Settings, backup, and customization",
        "Bug reports and feature requests",
        "General feedback"
    ])

    # 3. Choose developer account (numbered) and third-party services
    acc = prompt_accounts(config)
    dev_name = acc["name"]
    dev_email = acc["email"]

    # Third-party services to declare (AdMob, IAP, Supabase)
    services = prompt_services(config)

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

    with open(privacy_template_path, 'r', encoding='utf-8') as f:
        privacy_template = f.read()

    with open(support_template_path, 'r', encoding='utf-8') as f:
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

    # Apply conditional service blocks (AdMob / IAP / Supabase / FAQ)
    privacy_html = apply_conditional_blocks(privacy_html, services)
    support_html = apply_conditional_blocks(support_html, services)

    # 6. Create app directory
    target_dir = os.path.join(script_dir, app_slug)
    folder_exists = os.path.exists(target_dir)
    if folder_exists:
        print_warning(f"Folder '{app_slug}' already exists. Overwriting files inside.")
    os.makedirs(target_dir, exist_ok=True)

    # Write files
    privacy_out_path = os.path.join(target_dir, 'privacy.html')
    support_out_path = os.path.join(target_dir, 'support.html')

    with open(privacy_out_path, 'w', encoding='utf-8') as f:
        f.write(privacy_html)

    with open(support_out_path, 'w', encoding='utf-8') as f:
        f.write(support_html)

    print_success(f"Generated Privacy Policy: {privacy_out_path}")
    print_success(f"Generated Support Page: {support_out_path}")

    # Generate remote configs
    generate_remote_configs(script_dir, app_slug, config, services, acc)

    # 7. Print expected URLs & jsDelivr links
    username, repo = get_github_repo_info()
    branch = config.get("cdn_branch", "main")
    pages_domain = f"https://{username}.github.io/{repo}"

    print(f"\n{Colors.CYAN}{Colors.BOLD}Expected live Pages URLs (once pushed to GitHub):{Colors.ENDC}")
    print(f"Privacy Policy: {Colors.UNDERLINE}{pages_domain}/{app_slug}/privacy.html{Colors.ENDC}")
    print(f"Support Page:   {Colors.UNDERLINE}{pages_domain}/{app_slug}/support.html{Colors.ENDC}")

    jsdelivr_dev = get_jsdelivr_url(username, repo, branch, f"{app_slug}/dev.json")
    jsdelivr_prod = get_jsdelivr_url(username, repo, branch, f"{app_slug}/prod.json")

    if services.get("admob", False):
        try:
            print(f"\n{Colors.GREEN}{Colors.BOLD}📋 Copy into your Flutter ConfigService (lib/core/config/config_service.dart):{Colors.ENDC}")
        except UnicodeEncodeError:
            print(f"\n{Colors.GREEN}{Colors.BOLD}== Copy into your Flutter ConfigService (lib/core/config/config_service.dart): =={Colors.ENDC}")
        print(f"{Colors.CYAN}static const String devConfigUrl = '{jsdelivr_dev}';{Colors.ENDC}")
        print(f"{Colors.CYAN}static const String prodConfigUrl = '{jsdelivr_prod}';{Colors.ENDC}\n")

    append_to_apps_list(app_name, app_slug, username, repo, branch, folder_exists, services.get("admob", False))

    # 8. Git automation
    run_git_commands(app_slug, app_name)

if __name__ == "__main__":
    main()

# Specification: Adding Remote Ad Configs & app-ads.txt Automation to apps-pages (with jsDelivr CDN)

**Target Repository:** `https://github.com/City-Shadow/apps-pages`  
**Purpose:** Instructions for a coding agent to upgrade `apps-pages` from generating only Privacy and Support pages into a complete **Legal & Monetization Hub** for all mobile apps, using **jsDelivr CDN** for zero-latency, rate-limit-free remote configuration delivery.

---

## 1. Objective

Upgrade the existing `generate.py` and repository structure in `City-Shadow/apps-pages` so that running `python generate.py` automatically:
1. Generates `privacy.html` and `support.html` (existing functionality, hosted on GitHub Pages).
2. Generates **`dev.json`** and **`prod.json`** remote ad configs matching the Flutter `ConfigService` 3-tier architecture.
3. Automatically serves all remote JSON configs via **jsDelivr CDN** (`https://cdn.jsdelivr.net/gh/<username>/<repo>@main/<app-slug>/...`) for:
   - Zero GitHub Pages build propagation delay (instantly available as soon as Git pushes to `main`).
   - Unlimited bandwidth and edge-cached responses worldwide (backed by Cloudflare & Fastly).
   - Zero rate limits, zero CORS issues, and automatic JSON headers.
4. Creates and maintains a single, centralized **`app-ads.txt`** at the repository root with the developer's AdMob publisher ID (`google.com, pub-..., DIRECT, f08c47fec0942fa0`).
5. Adds an empty **`.nojekyll`** file at the root to prevent GitHub Pages from filtering JSON or dotfiles.
6. Updates **`apps.md`** to log the direct URLs for Privacy, Support, and the jsDelivr Dev/Prod Configs.
7. Prints copy-pasteable Dart constants directly into the terminal using jsDelivr CDN URLs:
   ```dart
   static const String devConfigUrl = 'https://cdn.jsdelivr.net/gh/City-Shadow/apps-pages@main/<app-slug>/dev.json';
   static const String prodConfigUrl = 'https://cdn.jsdelivr.net/gh/City-Shadow/apps-pages@main/<app-slug>/prod.json';
   ```
8. Stages, commits, and pushes all newly generated files (`dev.json`, `prod.json`, `app-ads.txt`, `.nojekyll`, `apps.md`, etc.) via Git.

---

## 2. Target Repository Structure

```text
City-Shadow/apps-pages/
├── .gitignore
├── .nojekyll                          <-- NEW: Guarantees raw JSON & static assets served cleanly
├── app-ads.txt                        <-- NEW: Root AdMob verification file for ALL apps
├── apps.md                            <-- UPDATED: Includes jsDelivr dev/prod config URLs
├── config.json                        <-- UPDATED: Adds accounts' AdMob publisher IDs & test IDs
├── generate.py                        <-- UPDATED: Orchestrates jsDelivr configs and ads.txt
├── README.md                          <-- UPDATED: Documents jsDelivr remote config & app-ads.txt
├── templates/
│   ├── privacy_template.html          (existing)
│   ├── support_template.html          (existing)
│   ├── app_config_dev_template.json   <-- NEW: Dev config template with Google test ad units
│   └── app_config_prod_template.json  <-- NEW: Prod config template with live ad unit slots
└── <app-slug>/
    ├── privacy.html                   (existing)
    ├── support.html                   (existing)
    ├── dev.json                       <-- NEW: Remote dev config (served via jsDelivr CDN)
    └── prod.json                      <-- NEW: Remote prod config (served via jsDelivr CDN)
```

---

## 3. Step-by-Step Changes

### Step 1: Create `.nojekyll`
Create an empty file named `.nojekyll` at the root of the repository.  
**Rationale:** Ensures GitHub Pages bypasses Jekyll build processing.

---

### Step 2: Update `config.json`
Extend `config.json` to associate an AdMob Publisher ID (`pub-xxxxxxxxxxxxxxxx`) with each developer account and supply default Google AdMob test IDs for quick fallback:

```json
{
  "developer_name": "Akram",
  "developer_email": "mer.wathek@gmail.com",
  "cdn_branch": "main",
  "accounts": [
    {
      "name": "Akram",
      "email": "mer.wathek@gmail.com",
      "admob_publisher_id": "pub-3588263773495662"
    },
    {
      "name": "Hanine",
      "email": "HanineMeraghni2002@icloud.com",
      "admob_publisher_id": ""
    },
    {
      "name": "Islam",
      "email": "islambelhardi12@gmail.com",
      "admob_publisher_id": ""
    }
  ],
  "default_services": ["admob", "iap", "supabase"],
  "default_features": [
    "In-App purchases, billing, and restoring premium features",
    "Ad playback and reward issues",
    "App features and functionality",
    "Performance or crash reports",
    "Settings, backup, and customization",
    "Bug reports and feature requests",
    "General feedback"
  ],
  "admob_test_units": {
    "android": {
      "app_open": "ca-app-pub-3940256099942544/9257395921",
      "interstitial": "ca-app-pub-3940256099942544/1033173712",
      "rewarded": "ca-app-pub-3940256099942544/5224354917"
    },
    "ios": {
      "app_open": "ca-app-pub-3940256099942544/5575463023",
      "interstitial": "ca-app-pub-3940256099942544/4411468910",
      "rewarded": "ca-app-pub-3940256099942544/1712485313"
    }
  }
}
```

---

### Step 3: Create `templates/app_config_dev_template.json`
Save this file into `templates/app_config_dev_template.json`. It uses Google's standard test AdMob unit IDs so that development builds never trigger account bans or policy strikes:

```json
{
  "config": {
    "promotions": {
      "enabled": true,
      "interstitial_enabled": true,
      "rewarded_enabled": true,
      "debug_mode": true,

      "app_open_ad_enabled": true,
      "first_open_ad_enabled": true,
      "app_open_ad_interval": 1,
      "app_open_ad_max_per_day": 10,
      "app_open_ad_max_total": 0,

      "primary_action_ad_enabled": true,
      "primary_action_ad_interval": 1,
      "primary_action_ad_type": "interstitial",

      "secondary_action_ad_enabled": true,
      "secondary_action_ad_interval": 1,
      "secondary_action_ad_type": "interstitial",

      "detail_action_ad_enabled": true,
      "detail_action_ad_interval": 1,
      "detail_action_ad_type": "interstitial",

      "interstitial_min_interval_seconds": 15,
      "interstitial_max_per_session": 15,
      "interstitial_max_per_day": 50,
      "interstitial_load_retry_seconds": 5,

      "promo_units": {
        "ios": {
          "interstitial_app_open_id": "{{IOS_TEST_APP_OPEN_ID}}",
          "interstitial_primary_action_id": "{{IOS_TEST_INTERSTITIAL_ID}}",
          "interstitial_secondary_action_id": "{{IOS_TEST_INTERSTITIAL_ID}}",
          "interstitial_detail_action_id": "{{IOS_TEST_INTERSTITIAL_ID}}",
          "rewarded_unlock_id": "{{IOS_TEST_REWARDED_ID}}"
        },
        "android": {
          "interstitial_app_open_id": "{{ANDROID_TEST_APP_OPEN_ID}}",
          "interstitial_primary_action_id": "{{ANDROID_TEST_INTERSTITIAL_ID}}",
          "interstitial_secondary_action_id": "{{ANDROID_TEST_INTERSTITIAL_ID}}",
          "interstitial_detail_action_id": "{{ANDROID_TEST_INTERSTITIAL_ID}}",
          "rewarded_unlock_id": "{{ANDROID_TEST_REWARDED_ID}}"
        }
      }
    }
  }
}
```

---

### Step 4: Create `templates/app_config_prod_template.json`
Save this file into `templates/app_config_prod_template.json`. It defines production throttling, frequency capping, and placeholders for real AdMob unit IDs:

```json
{
  "config": {
    "promotions": {
      "enabled": true,
      "interstitial_enabled": true,
      "rewarded_enabled": true,
      "debug_mode": false,

      "app_open_ad_enabled": true,
      "first_open_ad_enabled": true,
      "app_open_ad_interval": 1,
      "app_open_ad_max_per_day": 7,
      "app_open_ad_max_total": 0,

      "primary_action_ad_enabled": true,
      "primary_action_ad_interval": 1,
      "primary_action_ad_type": "{{PROD_PRIMARY_AD_TYPE}}",

      "secondary_action_ad_enabled": true,
      "secondary_action_ad_interval": 1,
      "secondary_action_ad_type": "{{PROD_SECONDARY_AD_TYPE}}",

      "detail_action_ad_enabled": true,
      "detail_action_ad_interval": 1,
      "detail_action_ad_type": "interstitial",

      "interstitial_min_interval_seconds": 30,
      "interstitial_max_per_session": 8,
      "interstitial_max_per_day": 20,
      "interstitial_load_retry_seconds": 5,

      "promo_units": {
        "ios": {
          "interstitial_app_open_id": "{{IOS_PROD_APP_OPEN_ID}}",
          "interstitial_primary_action_id": "{{IOS_PROD_PRIMARY_ACTION_ID}}",
          "interstitial_secondary_action_id": "{{IOS_PROD_SECONDARY_ACTION_ID}}",
          "interstitial_detail_action_id": "{{IOS_PROD_DETAIL_ACTION_ID}}",
          "rewarded_unlock_id": "{{IOS_PROD_REWARDED_ID}}"
        },
        "android": {
          "interstitial_app_open_id": "{{ANDROID_PROD_APP_OPEN_ID}}",
          "interstitial_primary_action_id": "{{ANDROID_PROD_PRIMARY_ACTION_ID}}",
          "interstitial_secondary_action_id": "{{ANDROID_PROD_SECONDARY_ACTION_ID}}",
          "interstitial_detail_action_id": "{{ANDROID_PROD_DETAIL_ACTION_ID}}",
          "rewarded_unlock_id": "{{ANDROID_PROD_REWARDED_ID}}"
        }
      }
    }
  }
}
```

---

### Step 5: Update `generate.py`

Modify `generate.py` to add functions for:
1. Detecting GitHub Repository coordinates (`username` and `repo`).
2. Constructing **jsDelivr CDN URLs** for `dev.json` and `prod.json`.
3. Ensuring `.nojekyll` exists at repo root.
4. Managing the root `app-ads.txt` file.
5. Generating `dev.json` and `prod.json` inside the `<app-slug>/` directory.
6. Updating `apps.md` with jsDelivr config links.
7. Printing copy-pasteable Dart constants with jsDelivr CDN URLs.

Here is the exact code to integrate into `generate.py`:

#### 1. Helper: Get GitHub Repo Info & jsDelivr Base
```python
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
```

#### 2. Helper: Ensure `.nojekyll` Exists
```python
def ensure_nojekyll(script_dir):
    nojekyll_path = os.path.join(script_dir, '.nojekyll')
    if not os.path.exists(nojekyll_path):
        with open(nojekyll_path, 'w') as f:
            f.write('')
        print_success("Created root .nojekyll file for fast static asset & JSON delivery.")
```

#### 3. Helper: Update Root `app-ads.txt`
```python
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
```

#### 4. Helper: Generate Dev and Prod JSON Configs
```python
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
        .replace("{{PROD_SECONDARY_AD_TYPE}}", "interstitial")\
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
```

#### 5. Update `append_to_apps_list()`
Include jsDelivr CDN URLs in `apps.md`:
```python
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
```

#### 6. Update `run_git_commands()`
Stage `app-ads.txt` and `.nojekyll` alongside the app folder:
```python
def run_git_commands(folder_name, app_name):
    if not os.path.exists(".git"):
        print_warning("Local git repository not found in current directory. Skipping git operations.")
        return

    try:
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
```

#### 7. Update `main()` Execution Flow
In `main()`:
1. Ensure `.nojekyll` exists at startup:
   ```python
   ensure_nojekyll(script_dir)
   ```
2. Prompt account and services as normal. Keep the chosen account object `acc` to access `acc.get("admob_publisher_id")`.
3. Get repo info and branch:
   ```python
   username, repo = get_github_repo_info()
   branch = config.get("cdn_branch", "main")
   ```
4. Generate the `dev.json` and `prod.json` configs:
   ```python
   generate_remote_configs(script_dir, app_slug, config, services, acc)
   ```
5. Print the live URLs and copy-pasteable Dart snippet using **jsDelivr**:
   ```python
   jsdelivr_dev = get_jsdelivr_url(username, repo, branch, f"{app_slug}/dev.json")
   jsdelivr_prod = get_jsdelivr_url(username, repo, branch, f"{app_slug}/prod.json")

   if services.get("admob", False):
       print(f"\n{Colors.GREEN}{Colors.BOLD}📋 Copy into your Flutter ConfigService (lib/core/config/config_service.dart):{Colors.ENDC}")
       print(f"{Colors.CYAN}static const String devConfigUrl = '{jsdelivr_dev}';{Colors.ENDC}")
       print(f"{Colors.CYAN}static const String prodConfigUrl = '{jsdelivr_prod}';{Colors.ENDC}\n")

   append_to_apps_list(app_name, app_slug, username, repo, branch, folder_exists, services.get("admob", False))
   run_git_commands(app_slug, app_name)
   ```

---

### Step 6: Update `README.md`
Add a section in `README.md` documenting:
- **Fast jsDelivr CDN:** Explaining why `dev.json` and `prod.json` use `cdn.jsdelivr.net/gh/...` (instant propagation, zero build delays, no rate limits, global edge caching).
- **AdMob `app-ads.txt`:** Explaining where the file is hosted (`https://<username>.github.io/<repo-name>/app-ads.txt`) and how it automatically covers every app pushed to the repo.

---

## 4. Acceptance Criteria for Coding Agent

- [ ] Running `python generate.py` creates `privacy.html`, `support.html`, `dev.json`, and `prod.json` inside `<app-slug>/`.
- [ ] Root `.nojekyll` is created and committed.
- [ ] Root `app-ads.txt` is updated with `google.com, pub-..., DIRECT, f08c47fec0942fa0`.
- [ ] The terminal output explicitly prints **jsDelivr CDN** links for `devConfigUrl` and `prodConfigUrl`.
- [ ] `apps.md` lists the jsDelivr CDN URLs for Dev & Prod config.
- [ ] Git commit automatically stages `app-ads.txt`, `.nojekyll`, `apps.md`, and the `<app-slug>` folder.

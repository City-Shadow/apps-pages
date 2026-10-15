# Legal & Monetization Hub for Mobile Apps (Pages + jsDelivr CDN)

A unified local automation tool to generate beautiful, responsive **Privacy Policy** and **Support** pages (hosted via **GitHub Pages**) and zero-latency **Remote Ad Configurations** (`dev.json` and `prod.json`) served globally via **jsDelivr CDN**, plus an automated root **`app-ads.txt`** for AdMob publisher verification.

---

## ✨ Features

- 📱 **Apple & Google Review Ready**: Generates high-quality, fully responsive static HTML pages that look spectacular on both mobile and desktop.
- ⚡ **Zero-Latency Remote Configs (jsDelivr CDN)**: Serves `dev.json` and `prod.json` via jsDelivr CDN edge caching (Cloudflare + Fastly) with instant propagation on push, unlimited bandwidth, and zero rate limits.
- 🎯 **AdMob `app-ads.txt` Automation**: Automatically creates and appends your AdMob publisher ID to the root `app-ads.txt` file, covering all apps under your developer domain.
- 🚀 **Flutter `ConfigService` Ready**: Terminal outputs copy-pasteable Dart constants pointing directly to jsDelivr CDN endpoints.
- 🚫 **GitHub Pages `.nojekyll` Guarantee**: Ensures raw JSON configs and static assets bypass Jekyll processing.
- 🌓 **Automatic Dark Mode**: Built-in native support for light/dark system themes using CSS variables.
- 🎨 **Premium Modern Design**: Uses elegant Google fonts (*Outfit* and *Inter*), smooth gradients, soft card shadows, and micro-interactions.
- 📁 **Multi-App Folders**: Keeps each app's documents and configs organized in their own folders (e.g. `<app-slug>/privacy.html`, `<app-slug>/dev.json`, `<app-slug>/prod.json`).
- 🤖 **Interactive CLI**: Prompts for app details and live AdMob unit IDs while falling back to Google official test IDs for safe development.
- 🐙 **Git Automation**: Stages, commits, and pushes your pages, configs, `app-ads.txt`, and `.nojekyll` to GitHub directly from the command line.

---

## ⚙️ Configuration (`config.json`)

Customize your default profiles in `config.json` so you do not have to re-type them for every app:

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

- **`accounts`**: Developer profiles paired with their AdMob Publisher IDs (`pub-xxxxxxxxxxxxxxxx`).
- **`cdn_branch`**: Branch used to construct jsDelivr URLs (defaults to `main`).
- **`default_services`**: Preselected third-party services (`admob`, `iap`, `supabase`).
- **`admob_test_units`**: Standard Google test IDs used automatically for `dev.json`.

---

## 🚀 How to Generate Pages & Remote Configs

1. Open your terminal in this repository and run:
   ```bash
   python generate.py
   ```
2. Enter the **App Name** (e.g., `Bolt Pro: Browser and Docs`).
3. **Choose developer account** (numbered choice from `config.json`) — auto-selects publisher ID for `app-ads.txt`.
4. **Select services** (Google AdMob, In-App Purchases, Supabase).
5. If AdMob is enabled:
   - Choose whether you have live production AdMob ad unit IDs to input now or use placeholders.
   - Choose default primary action ad type (`rewarded` or `interstitial`).
6. Confirm date and support topics.
7. The CLI will:
   - Create `<app-slug>/privacy.html` & `<app-slug>/support.html`.
   - Create `<app-slug>/dev.json` & `<app-slug>/prod.json`.
   - Update `app-ads.txt` at the root with your developer publisher ID.
   - Ensure `.nojekyll` exists at the root.
   - Append all URLs to `apps.md`.
   - Print copy-pasteable Dart constants for your Flutter app:
     ```dart
     static const String devConfigUrl = 'https://cdn.jsdelivr.net/gh/City-Shadow/apps-pages@main/<app-slug>/dev.json';
     static const String prodConfigUrl = 'https://cdn.jsdelivr.net/gh/City-Shadow/apps-pages@main/<app-slug>/prod.json';
     ```
8. Select `y` to stage, commit, and push directly to GitHub!

---

## 🌐 Fast jsDelivr CDN Remote Configs

Remote configs are served via **jsDelivr CDN** rather than standard raw GitHub or GitHub Pages URLs:
- **Instant Availability**: As soon as `git push` lands on GitHub, files are live worldwide through `cdn.jsdelivr.net/gh/<user>/<repo>@main/<app-slug>/dev.json`.
- **Zero Propagation Delay**: No waiting for GitHub Pages build actions to finish.
- **Global Edge Caching**: Backed by multi-CDN routing (Cloudflare, Fastly) for maximum reliability and uptime.
- **No Rate Limits / Zero CORS**: Safe for high-frequency client app downloads and in-app updates.

---

## 📋 AdMob `app-ads.txt` Verification

Google requires an `app-ads.txt` file at the root of your developer website URL listed in Google Play and the Apple App Store.

- Hosted automatically at: `https://<username>.github.io/<repo>/app-ads.txt`
- Format:
  ```text
  google.com, pub-3588263773495662, DIRECT, f08c47fec0942fa0
  ```
- Whenever you generate pages for an app under an account with an `admob_publisher_id`, `generate.py` ensures that publisher ID is recorded in `app-ads.txt`.

---

## 🌐 GitHub Pages Deployment (One-Time Setup)

Once pushed to GitHub:
1. Go to repository **Settings** > **Pages**.
2. Under **Build and deployment**:
   - **Source**: `Deploy from a branch`.
   - **Branch**: `main`, folder `/ (root)`.
3. Click **Save**.

Live URLs:
- **Privacy Policy**: `https://<username>.github.io/<repo>/<app-slug>/privacy.html`
- **Support Page**: `https://<username>.github.io/<repo>/<app-slug>/support.html`
- **Root app-ads.txt**: `https://<username>.github.io/<repo>/app-ads.txt`
- **Remote Config (Dev)**: `https://cdn.jsdelivr.net/gh/<username>/<repo>@main/<app-slug>/dev.json`
- **Remote Config (Prod)**: `https://cdn.jsdelivr.net/gh/<username>/<repo>@main/<app-slug>/prod.json`

# iOS App Pages Generator (GitHub Pages)

A simple, local automation tool to generate beautiful, responsive **Privacy Policy** and **Support** pages for all of your iOS apps and host them for free using **GitHub Pages**.

---

## ✨ Features

- 📱 **Apple Review Ready**: Generates high-quality, fully responsive static HTML pages that look spectacular on both mobile and desktop.
- 🌓 **Automatic Dark Mode**: Built-in native support for light/dark system themes using CSS variables.
- 🎨 **Premium Modern Design**: Uses elegant Google fonts (*Outfit* and *Inter*), smooth gradients, soft card shadows, and micro-interactions.
- 📁 **Multi-App Folders**: Keeps each app's documents organized in their own folders (e.g. `bolt-pro-browser-and-docs/privacy.html`).
- 🤖 **Interactive CLI**: Prompts you for configuration overrides but falls back to your saved profile configurations to minimize typing.
- 🔗 **Smart URL Detection**: Detects your GitHub remote origin URL to show you your exact public live URLs immediately after generation.
- 🐙 **Git Automation**: Stages, commits, and pushes your pages to GitHub directly from the command line.

---

## ⚙️ Configuration (`config.json`)

Customize your default profile in `config.json` so you do not have to re-type them for every app:

```json
{
  "developer_name": "Wathek",
  "developer_email": "mer.wathek@gmail.com",
  "default_features": [
    "Web browsing issues",
    "Document viewing and management",
    "Downloads and file handling",
    "Search and navigation",
    "Performance and stability",
    "Bug reports",
    "Feature requests",
    "General feedback"
  ]
}
```

---

## 🚀 How to Generate Pages

1. Open your terminal in this directory and execute the generator script:
   ```bash
   ./generate.py
   ```
2. Enter the **iOS App Name** (e.g., `Bolt Pro: Browser and Docs`).
3. Press **Enter** to accept default developer name, email, and date, or override them.
4. Choose whether to use default support topics or enter a customized list.
5. The folder and pages will be created. Select `y` to commit them immediately.

---

## 🌐 Deploying to GitHub Pages (One-Time Setup)

Once you commit your files, you need to push them to GitHub and activate Pages to get public URLs:

### 1. Push to GitHub
Create a new **public** repository on GitHub (e.g. name it `apps-pages`) and run these commands to link and upload your files:
```bash
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/YOUR_REPO_NAME.git
git branch -M main
git push -u origin main
```

### 2. Configure GitHub Pages
1. Go to your repository on **GitHub.com**.
2. Click the **Settings** tab (gear icon at the top).
3. In the left sidebar, click **Pages** (under the "Code and automation" section).
4. Under **Build and deployment**:
   - **Source**: Select `Deploy from a branch`.
   - **Branch**: Choose `main` (or whichever branch you are using) and leave the folder set to `/ (root)`.
5. Click **Save**.

Within ~30 seconds, your site will be live at:
- **Privacy Policy**: `https://<YOUR_USERNAME>.github.io/<YOUR_REPO_NAME>/<app-slug>/privacy.html`
- **Support Page**: `https://<YOUR_USERNAME>.github.io/<YOUR_REPO_NAME>/<app-slug>/support.html`

*(Once you have configured the git remote, `generate.py` will automatically detect it and print these URLs for you!)*

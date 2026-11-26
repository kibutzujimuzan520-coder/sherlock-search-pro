# Sherlock Search Pro — Mobile-only deployment guide

This is a phone-friendly web app. It includes a Python standard-library backend, responsive UI, PWA files, local search history, and CSV/JSON export. Checks are best-effort public URL responses, not definitive profile existence or identity confirmation.

## Publish without a computer (phone only)

### Option: GitHub + Render
1. In Chrome on your phone, open GitHub and sign in or create an account.
2. Create a **new public repository** named `sherlock-search-pro`.
3. On the repository page, choose **Add file → Upload files**. Use your phone's file picker to select the extracted files in this folder (`server.py`, `index.html`, `manifest.json`, `icon.svg`, `sw.js`, and `render.yaml`). Do not upload the ZIP itself. Commit the files.
4. Open Render's website and sign in using GitHub.
5. Choose **New → Blueprint** (or **New Web Service** if Blueprint is not shown), select the `sherlock-search-pro` repo, and confirm deploy using the `render.yaml` settings.
6. Wait for the service to finish deploying. Open its `https://...onrender.com` URL on your phone.
7. In Chrome, use **⋮ → Add to Home screen** or **Install app**.

Render free web services may sleep when idle and take a little time to wake up. For continuous uptime, use a paid hosting plan.


## Alternative: Deploy from an archive
If the hosting provider supports importing a ZIP, upload this folder's files (not the ZIP) and set the start command to `python server.py`.

## Responsible use
Search only usernames you own or have permission to check. The app checks public profile URLs and does not log in, scrape profile details, bypass CAPTCHA, or evade site access controls. Platform responses can be misleading, blocked, or rate-limited; use **Unknown** as inconclusive and manually open any possible match.

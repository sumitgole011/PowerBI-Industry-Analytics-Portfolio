# Publish this repository to GitHub

The archive is **ready for upload**; it does not create a GitHub repository or publish itself.

## Recommended automated path (macOS terminal)

1. Install GitHub CLI if needed: `brew install gh`
2. Authenticate securely in browser: `gh auth login` (select GitHub.com and HTTPS)
3. Open Terminal in the extracted `PowerBI_Industry_Analytics_GitHub_Ready` folder
4. Run:

```bash
bash publish_to_github.sh
```

The script creates a public repository called `PowerBI-Industry-Analytics-Portfolio` in your authenticated GitHub account and pushes all included files. It also handles the case where an empty remote repository already exists. Check the code first if you want to change the visibility/name.

If you prefer GitHub website: first create a **public empty repository** on [github.com/new](https://github.com/new) named `PowerBI-Industry-Analytics-Portfolio` (do not initialize with README, license or .gitignore). Then run the same script.

## GitHub Pages (optional)

From GitHub, navigate to repository Settings → Pages. Configure the branch to `main`, folder to `/docs`, then save. This hosts the static HTML demo only. Actual Power BI reports still require authoring in Power BI.

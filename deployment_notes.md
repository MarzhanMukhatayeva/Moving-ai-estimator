# GitHub Upload Checklist

## Before upload
1. Replace all real API keys with placeholders
2. Remove Azure function code query key from any URLs
3. Remove customer emails and production data
4. Rename sensitive files to sample versions if needed
5. Keep only portfolio-safe screenshots and PDFs

## Suggested first commit message
Initial commit: AI-powered moving estimator with Google Forms, Apps Script, Azure Functions, Google Routes API, and OpenAI integration

## Git commands
git init
git add .
git commit -m "Initial commit: AI-powered moving estimator"
git branch -M main
git remote add origin YOUR_GITHUB_REPO_URL
git push -u origin main

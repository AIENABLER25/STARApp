# GitHub Actions Deployment Setup

This repository includes automated deployment workflows for both Vercel and Netlify.

## Quick Deployment Options

### Option 1: Manual Deployment (Quickest)

#### Vercel (Recommended)
```bash
cd auguste-archive
npm install -g vercel
vercel login
vercel --prod
```

#### Netlify
```bash
cd auguste-archive
npm install -g netlify-cli
netlify login
netlify deploy --prod
```

---

## Option 2: Automated GitHub Actions Deployment

Automated workflows are configured in `.github/workflows/` and will deploy on every push to main/master branch.

### Setup for Vercel Deployment

1. **Create a Vercel account** at https://vercel.com

2. **Install Vercel CLI and create project:**
   ```bash
   npm install -g vercel
   cd auguste-archive
   vercel
   ```
   Follow the prompts to create a new project.

3. **Get your Vercel credentials:**
   ```bash
   # Get your token
   vercel token create

   # Get your Org ID and Project ID from .vercel/project.json
   cat .vercel/project.json
   ```

4. **Add GitHub Secrets:**
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - Add these secrets:
     - `VERCEL_TOKEN` - Your Vercel token
     - `VERCEL_ORG_ID` - Your organization ID
     - `VERCEL_PROJECT_ID` - Your project ID

5. **Enable the workflow:**
   - Push to main/master branch
   - Or manually trigger from Actions tab → "Deploy to Vercel Production" → "Run workflow"

### Setup for Netlify Deployment

1. **Create a Netlify account** at https://netlify.com

2. **Install Netlify CLI and create site:**
   ```bash
   npm install -g netlify-cli
   cd auguste-archive
   netlify init
   ```

3. **Get your Netlify credentials:**
   - Auth Token: Go to https://app.netlify.com/user/applications → Personal access tokens → Create new token
   - Site ID: Run `netlify status` or find it in Site Settings → General → Site details

4. **Add GitHub Secrets:**
   - Go to your GitHub repository
   - Settings → Secrets and variables → Actions
   - Add these secrets:
     - `NETLIFY_AUTH_TOKEN` - Your Netlify personal access token
     - `NETLIFY_SITE_ID` - Your site ID

5. **Enable the workflow:**
   - Push to main/master branch
   - Or manually trigger from Actions tab

---

## Workflow Features

Both workflows include:
- ✅ Automatic triggering on push to main/master
- ✅ Manual workflow dispatch
- ✅ Only triggers when auguste-archive files change
- ✅ Caches dependencies for faster builds
- ✅ Runs tests and builds before deployment
- ✅ Production-ready optimizations

## Monitoring Deployments

### View Deployment Status
- Go to your repository's "Actions" tab
- Click on the latest workflow run
- View logs and deployment status

### Deployment URLs
- **Vercel**: Automatically provided in workflow logs and Vercel dashboard
- **Netlify**: Automatically provided in workflow logs and pull request comments

## Troubleshooting

**Workflow fails with "secret not found":**
- Verify all required secrets are added in repository settings
- Check secret names match exactly (case-sensitive)

**Build fails:**
- Check the build logs in Actions tab
- Ensure package.json and dependencies are correct
- Test locally with `npm run build`

**Deployment fails:**
- Verify Vercel/Netlify tokens are valid
- Check if project/site IDs are correct
- Ensure you have deployment permissions

## Manual Override

To disable automated deployments:
1. Rename or delete the workflow file
2. Or add `[skip ci]` to your commit message

## Local Testing

Before pushing, test locally:
```bash
cd auguste-archive
npm install
npm run build
npm run preview
```

Visit http://localhost:4173 to test the production build.

---

**Note:** Choose either Vercel OR Netlify workflow. You don't need both, but having both configured gives you flexibility.

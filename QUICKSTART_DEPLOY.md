# Quick Deploy - Auguste Archive

## Fastest Way to Deploy (3 Steps)

### Option 1: Vercel (Recommended - 2 minutes)

1. **Install Vercel CLI:**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel:**
   ```bash
   vercel login
   ```
   This will open a browser - click "Confirm" to authenticate.

3. **Deploy:**
   ```bash
   cd auguste-archive
   vercel --prod
   ```

   Follow the prompts:
   - Set up and deploy: **Yes**
   - Which scope: Select your account
   - Link to existing project: **No**
   - What's your project's name: **auguste-archive** (or press Enter)
   - In which directory: **./** (press Enter)
   - Want to modify settings: **No** (press Enter)

   **Done!** You'll get a production URL like: `https://auguste-archive.vercel.app`

---

### Option 2: Netlify (Alternative - 2 minutes)

1. **Install Netlify CLI:**
   ```bash
   npm install -g netlify-cli
   ```

2. **Login to Netlify:**
   ```bash
   netlify login
   ```

3. **Deploy:**
   ```bash
   cd auguste-archive
   netlify deploy --prod
   ```

   Follow the prompts:
   - Create & configure a new site: **Yes**
   - Team: Select your team
   - Site name: **auguste-archive** (or your preferred name)
   - Publish directory: **dist**

   **Done!** You'll get a production URL.

---

## Already Have an Account?

If you've previously deployed to Vercel/Netlify:

**Vercel:**
```bash
cd auguste-archive
vercel --prod
```

**Netlify:**
```bash
cd auguste-archive
netlify deploy --prod --dir=dist
```

---

## Automated Deployment (GitHub Actions)

Set up once, deploy automatically on every push:

1. Choose Vercel or Netlify
2. Follow setup in `.github/DEPLOYMENT_AUTOMATION.md`
3. Push to main branch - deployment happens automatically!

---

## Need Help?

- Vercel docs: https://vercel.com/docs
- Netlify docs: https://docs.netlify.com
- Detailed guide: See `auguste-archive/DEPLOYMENT.md`

---

## Production URL Structure

**Vercel:** `https://[project-name].vercel.app`
**Netlify:** `https://[site-name].netlify.app`

You can add a custom domain later in the platform settings.

---

**Current Status:** ✅ Build ready, configuration complete, ready to deploy!

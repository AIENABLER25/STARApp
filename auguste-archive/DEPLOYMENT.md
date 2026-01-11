# Deployment Guide - Dr. Byron Auguste Archive

This guide provides instructions for deploying the Auguste Archive application to production.

## Deployment Options

The application can be deployed to any static hosting service. Below are instructions for the most popular options.

---

## Option 1: Vercel (Recommended)

Vercel provides seamless deployment for Vite applications with zero configuration.

### Deploy via Vercel CLI

1. **Install Vercel CLI (if not already installed)**
   ```bash
   npm install -g vercel
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy from the project directory**
   ```bash
   cd auguste-archive
   vercel
   ```

4. **Follow the prompts:**
   - Set up and deploy: Yes
   - Which scope: Select your account
   - Link to existing project: No
   - Project name: auguste-archive (or your preferred name)
   - Directory: ./
   - Override settings: No

5. **Deploy to production**
   ```bash
   vercel --prod
   ```

### Deploy via Vercel Dashboard

1. Visit [vercel.com](https://vercel.com)
2. Click "Add New Project"
3. Import your Git repository
4. Vercel will auto-detect Vite settings
5. Click "Deploy"

**Configuration:** The `vercel.json` file is already configured with optimal settings.

---

## Option 2: Netlify

### Deploy via Netlify CLI

1. **Install Netlify CLI**
   ```bash
   npm install -g netlify-cli
   ```

2. **Login to Netlify**
   ```bash
   netlify login
   ```

3. **Deploy from the project directory**
   ```bash
   cd auguste-archive
   netlify deploy
   ```

4. **Follow the prompts:**
   - Create & configure a new site
   - Team: Select your team
   - Site name: auguste-archive (or your preferred name)
   - Publish directory: dist

5. **Deploy to production**
   ```bash
   netlify deploy --prod
   ```

### Deploy via Netlify Dashboard

1. Visit [netlify.com](https://netlify.com)
2. Click "Add new site" → "Import an existing project"
3. Connect your Git repository
4. Build settings (auto-detected):
   - Build command: `npm run build`
   - Publish directory: `dist`
5. Click "Deploy site"

**Configuration:** The `netlify.toml` file is already configured.

---

## Option 3: GitHub Pages

### Deploy via gh-pages package

1. **Install gh-pages**
   ```bash
   npm install --save-dev gh-pages
   ```

2. **Add to package.json scripts:**
   ```json
   {
     "scripts": {
       "predeploy": "npm run build",
       "deploy": "gh-pages -d dist"
     }
   }
   ```

3. **Update vite.config.js with base path:**
   ```javascript
   export default defineConfig({
     plugins: [react()],
     base: '/STARApp/'  // Replace with your repo name
   })
   ```

4. **Deploy**
   ```bash
   npm run deploy
   ```

5. **Configure GitHub Pages:**
   - Go to repository Settings → Pages
   - Source: Deploy from branch
   - Branch: gh-pages
   - Save

Your site will be available at: `https://[username].github.io/[repo-name]/`

---

## Option 4: Other Static Hosts

The application can be deployed to any static hosting service:

### Build the application:
```bash
npm run build
```

The production-ready files will be in the `dist/` directory.

### Popular alternatives:
- **Cloudflare Pages**: Zero configuration, excellent performance
- **AWS S3 + CloudFront**: Scalable, enterprise-grade
- **Azure Static Web Apps**: Microsoft cloud integration
- **Firebase Hosting**: Google cloud integration
- **Render**: Simple static site hosting

---

## Environment Variables

This application currently uses no environment variables. All data is statically defined in `src/data/augusteContent.js`.

If you need to add environment variables in the future:

**Vercel:**
- Add in Project Settings → Environment Variables
- Prefix with `VITE_` to expose to client

**Netlify:**
- Add in Site Settings → Environment Variables
- Prefix with `VITE_` to expose to client

**Example:**
```bash
VITE_API_URL=https://api.example.com
```

Access in code:
```javascript
const apiUrl = import.meta.env.VITE_API_URL
```

---

## Custom Domain

### Vercel
1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS configuration instructions

### Netlify
1. Go to Site Settings → Domain Management
2. Add custom domain
3. Update DNS records as instructed

---

## Continuous Deployment

Both Vercel and Netlify offer automatic deployments:

1. Connect your Git repository
2. Every push to the main branch triggers a deployment
3. Pull requests get preview deployments
4. Zero configuration needed

---

## Monitoring and Analytics

### Add Analytics (Optional)

**Vercel Analytics:**
```bash
npm install @vercel/analytics
```

In `src/main.jsx`:
```javascript
import { inject } from '@vercel/analytics'
inject()
```

**Google Analytics:**
Add to `index.html` before `</head>`:
```html
<script async src="https://www.googletagmanager.com/gtag/js?id=YOUR-GA-ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'YOUR-GA-ID');
</script>
```

---

## Performance Optimization

The application is already optimized with:
- ✅ Vite's built-in code splitting
- ✅ Minified production builds
- ✅ Tailwind CSS purging unused styles
- ✅ React production mode

### Additional optimizations:
- Enable compression on your hosting platform (usually automatic)
- Configure CDN caching headers
- Add image optimization if adding images in the future

---

## Troubleshooting

**Build fails with "command not found":**
- Ensure Node.js 18+ is installed
- Run `npm install` first

**404 errors on page refresh:**
- Ensure SPA redirects are configured (see vercel.json/netlify.toml)

**Styles not loading:**
- Check build output includes CSS files
- Clear browser cache

**Need help?**
- Check hosting provider documentation
- Review build logs for errors

---

## Production Checklist

Before deploying to production:

- [ ] Test the build locally: `npm run build && npm run preview`
- [ ] Verify all links work
- [ ] Test search functionality
- [ ] Test on mobile devices
- [ ] Check browser console for errors
- [ ] Update content in `src/data/augusteContent.js` if needed
- [ ] Configure custom domain (if applicable)
- [ ] Set up analytics (if desired)
- [ ] Configure environment variables (if needed)

---

## Quick Deploy Commands

**Vercel:**
```bash
cd auguste-archive
npm run build
vercel --prod
```

**Netlify:**
```bash
cd auguste-archive
npm run build
netlify deploy --prod
```

**Preview locally:**
```bash
npm run build
npm run preview
```

---

**Deployment Status:** Ready for production deployment ✅

**Recommended Platform:** Vercel or Netlify (both offer free tier for static sites)

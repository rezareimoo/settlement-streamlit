# Deployment Guide - Settlement 360

This guide covers deploying the Settlement 360 Next.js application to production.

## Recommended Deployment: Vercel

Vercel is the recommended platform as it's created by the Next.js team and offers seamless integration.

### Prerequisites
- GitHub/GitLab/Bitbucket repository with your code
- Vercel account (free tier available)

### Steps

1. **Push code to Git repository:**
   ```bash
   cd /workspace/settlement-nextjs
   git init
   git add .
   git commit -m "Initial Next.js migration"
   git remote add origin YOUR_REPO_URL
   git push -u origin main
   ```

2. **Connect to Vercel:**
   - Go to [vercel.com](https://vercel.com)
   - Click "Import Project"
   - Select your repository
   - Vercel will auto-detect Next.js settings

3. **Configure Environment Variables:**
   In Vercel dashboard, add these environment variables:
   ```
   DB_HOST=settlementanalyticsdb.postgres.database.azure.com
   DB_NAME=Settlement
   DB_USER=settlementAdmin71125
   DB_PASSWORD=SideHustle2025!
   DB_PORT=5432
   ```

4. **Deploy:**
   - Click "Deploy"
   - Vercel will build and deploy your app
   - You'll get a live URL (e.g., settlement-360.vercel.app)

### Vercel Configuration

Create `vercel.json` if you need custom settings:

```json
{
  "buildCommand": "npm run build",
  "devCommand": "npm run dev",
  "installCommand": "npm install --legacy-peer-deps",
  "framework": "nextjs",
  "regions": ["iad1"]
}
```

## Alternative: Docker Deployment

If you prefer Docker:

1. **Create Dockerfile:**
   ```dockerfile
   FROM node:18-alpine AS base

   # Install dependencies only when needed
   FROM base AS deps
   RUN apk add --no-cache libc6-compat
   WORKDIR /app

   COPY package*.json ./
   RUN npm ci --legacy-peer-deps

   # Rebuild the source code only when needed
   FROM base AS builder
   WORKDIR /app
   COPY --from=deps /app/node_modules ./node_modules
   COPY . .

   ENV NEXT_TELEMETRY_DISABLED 1

   RUN npm run build

   # Production image
   FROM base AS runner
   WORKDIR /app

   ENV NODE_ENV production
   ENV NEXT_TELEMETRY_DISABLED 1

   RUN addgroup --system --gid 1001 nodejs
   RUN adduser --system --uid 1001 nextjs

   COPY --from=builder /app/public ./public
   COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
   COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

   USER nextjs

   EXPOSE 3000

   ENV PORT 3000

   CMD ["node", "server.js"]
   ```

2. **Build and run:**
   ```bash
   docker build -t settlement-360 .
   docker run -p 3000:3000 \
     -e DB_HOST=settlementanalyticsdb.postgres.database.azure.com \
     -e DB_NAME=Settlement \
     -e DB_USER=settlementAdmin71125 \
     -e DB_PASSWORD=SideHustle2025! \
     -e DB_PORT=5432 \
     settlement-360
   ```

## Alternative: Traditional VPS/Server

For deployment on a VPS (AWS, DigitalOcean, etc.):

1. **Install Node.js 18+:**
   ```bash
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   ```

2. **Clone and setup:**
   ```bash
   git clone YOUR_REPO_URL
   cd settlement-nextjs
   npm install --legacy-peer-deps
   ```

3. **Create .env.local:**
   ```bash
   cat > .env.local << EOF
   DB_HOST=settlementanalyticsdb.postgres.database.azure.com
   DB_NAME=Settlement
   DB_USER=settlementAdmin71125
   DB_PASSWORD=SideHustle2025!
   DB_PORT=5432
   EOF
   ```

4. **Build:**
   ```bash
   npm run build
   ```

5. **Run with PM2:**
   ```bash
   npm install -g pm2
   pm2 start npm --name "settlement-360" -- start
   pm2 save
   pm2 startup
   ```

6. **Setup Nginx reverse proxy:**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://localhost:3000;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection 'upgrade';
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

## Environment Variables

Required environment variables for production:

| Variable | Description | Example |
|----------|-------------|---------|
| DB_HOST | PostgreSQL host | settlementanalyticsdb.postgres.database.azure.com |
| DB_NAME | Database name | Settlement |
| DB_USER | Database user | settlementAdmin71125 |
| DB_PASSWORD | Database password | [secure password] |
| DB_PORT | Database port | 5432 |

Optional variables:

| Variable | Description | Default |
|----------|-------------|---------|
| NODE_ENV | Environment | production |
| PORT | Server port | 3000 |
| NEXT_TELEMETRY_DISABLED | Disable telemetry | 1 |

## Post-Deployment Checklist

- [ ] Verify all API routes are working
- [ ] Test database connectivity
- [ ] Check all tabs load correctly
- [ ] Verify data displays properly
- [ ] Test filtering functionality
- [ ] Check mobile responsiveness
- [ ] Review error logs
- [ ] Set up monitoring (optional)
- [ ] Configure SSL certificate
- [ ] Set up backup procedures

## Monitoring & Maintenance

### Vercel Dashboard
- View deployment logs
- Monitor performance metrics
- Track API usage
- Set up alerts

### Database Connection Pool
The app uses a connection pool with:
- Max 20 connections
- 30s idle timeout
- 10s connection timeout

Monitor your PostgreSQL database for:
- Connection count
- Query performance
- Error rates

### Recommended Tools
- **Monitoring:** Vercel Analytics, Sentry
- **Logging:** Vercel Logs, LogRocket
- **Performance:** Lighthouse, Web Vitals
- **Uptime:** UptimeRobot, Pingdom

## Troubleshooting

### Build Failures
```bash
# Clear cache and rebuild
rm -rf .next node_modules
npm install --legacy-peer-deps
npm run build
```

### Database Connection Issues
- Verify environment variables are set correctly
- Check database firewall allows your server IP
- Ensure SSL is enabled
- Test connection with psql client

### Memory Issues
- Increase Node.js memory limit:
  ```bash
  NODE_OPTIONS="--max-old-space-size=4096" npm run build
  ```

### Port Already in Use
```bash
# Kill process on port 3000
lsof -ti:3000 | xargs kill -9
```

## Security Considerations

1. **Environment Variables:** Never commit .env.local to git
2. **Database:** Use read-only credentials if possible
3. **API Routes:** Add rate limiting
4. **SSL:** Always use HTTPS in production
5. **Updates:** Keep dependencies updated
6. **Monitoring:** Set up error tracking

## Performance Optimization

1. **Enable caching:** Configure CDN
2. **Optimize images:** Use Next.js Image component
3. **Database indexes:** Ensure proper indexing
4. **Connection pooling:** Already configured
5. **Static generation:** Use when possible

## Rollback Procedure

### Vercel
- Go to deployment history
- Click on previous successful deployment
- Click "Promote to Production"

### PM2
```bash
pm2 stop settlement-360
git checkout previous-commit-hash
npm run build
pm2 restart settlement-360
```

## Support

For deployment issues:
1. Check Vercel docs: https://vercel.com/docs
2. Review Next.js deployment guide: https://nextjs.org/docs/deployment
3. Contact DevOps team

---

**Ready to deploy!** Follow the steps above for your chosen platform.

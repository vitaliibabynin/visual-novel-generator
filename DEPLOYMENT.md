# Deployment Guide

This guide covers multiple hosting options for the Visual Novel Generator.

## 🚀 Option 1: Render.com (Easiest - Free Tier Available)

### Setup (5 minutes)

1. **Push your code to GitHub** (already done!)

2. **Sign up at [render.com](https://render.com)**

3. **Create New Web Service:**
   - Click "New +" → "Web Service"
   - Connect your GitHub repo: `vitaliibabynin/visual-novel-generator`
   - Select branch: `claude/visual-novel-generator-011CUzhr8sik4QYQLoGQ1xjF`

4. **Configure:**
   - **Name**: visual-novel-generator
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python app.py`
   - **Plan**: Free (or Starter $7/month for better performance)

5. **Add Environment Variables:**
   - `OPENAI_API_KEY` = your_openai_key
   - `IMAGE_PROVIDER` = openai
   - `FLASK_ENV` = production

6. **Add Persistent Disk (Important!):**
   - Under "Disks" → Add Disk
   - Name: `story-data`
   - Mount Path: `/opt/render/project/src/stories`
   - Size: 1 GB

   - Add another disk:
   - Name: `image-data`
   - Mount Path: `/opt/render/project/src/static/images`
   - Size: 2 GB

7. **Deploy!** (takes ~2-3 minutes)

**Your app will be live at:** `https://visual-novel-generator.onrender.com`

### Pros:
- Free tier available
- Auto-deploys on git push
- Persistent storage included
- SSL/HTTPS automatic

### Cons:
- Free tier spins down after 15 min inactivity (30 sec cold start)
- Limited to 750 hours/month on free tier

---

## 🚄 Option 2: Railway.app (Fastest Deploy)

### Setup (5 minutes)

1. **Sign up at [railway.app](https://railway.app)**

2. **Install Railway CLI:**
```bash
npm install -g @railway/cli
# or
brew install railway
```

3. **Deploy:**
```bash
cd visual-novel-generator
railway login
railway init
railway up
```

4. **Add Environment Variables:**
```bash
railway variables set OPENAI_API_KEY=your_key_here
railway variables set IMAGE_PROVIDER=openai
railway variables set FLASK_ENV=production
```

5. **Generate Domain:**
```bash
railway domain
```

**Your app will be live at:** Railway-generated URL

### Pricing:
- $5 free credit (good for testing)
- ~$5-10/month after
- Pay-as-you-go

### Pros:
- Super fast deployment
- No cold starts
- Persistent storage by default
- Great developer experience

### Cons:
- No free tier (after credit runs out)

---

## 🐳 Option 3: Fly.io (Best Free Tier)

### Setup (10 minutes)

1. **Install Fly CLI:**
```bash
curl -L https://fly.io/install.sh | sh
# or
brew install flyctl
```

2. **Login and Launch:**
```bash
cd visual-novel-generator
flyctl auth login
flyctl launch
```

3. **Follow prompts:**
   - App name: visual-novel-generator
   - Region: Choose closest to you
   - Postgres? No
   - Deploy now? No (we need to set secrets first)

4. **Create Volumes (for persistent storage):**
```bash
flyctl volumes create story_data --size 1 --region iad
flyctl volumes create image_data --size 2 --region iad
```

5. **Set Secrets:**
```bash
flyctl secrets set OPENAI_API_KEY=your_key_here
flyctl secrets set IMAGE_PROVIDER=openai
flyctl secrets set FLASK_ENV=production
```

6. **Deploy:**
```bash
flyctl deploy
```

**Your app will be live at:** `https://visual-novel-generator.fly.dev`

### Pricing:
- Free: 3 shared-cpu-1x 256mb VMs + 3GB persistent storage
- Perfect for this app!

### Pros:
- Best free tier
- Fast global CDN
- Persistent storage
- Auto-scaling

### Cons:
- Slightly more complex setup
- CLI required

---

## 🌊 Option 4: DigitalOcean App Platform

### Setup (10 minutes)

1. **Sign up at [digitalocean.com](https://digitalocean.com)**

2. **Create App:**
   - Apps → Create App
   - Connect GitHub repo
   - Select branch

3. **Configure:**
   - **Name**: visual-novel-generator
   - **Type**: Web Service
   - **Build Command**: `pip install -r requirements.txt`
   - **Run Command**: `python app.py`
   - **HTTP Port**: 5000

4. **Add Environment Variables:**
   - OPENAI_API_KEY
   - IMAGE_PROVIDER=openai
   - FLASK_ENV=production

5. **Deploy**

### Pricing:
- Basic: $5/month
- Professional: $12/month

### Pros:
- Simple interface
- Managed platform
- Good performance

### Cons:
- No free tier
- File storage requires workarounds

---

## 🖥️ Option 5: VPS (DigitalOcean Droplet)

For full control and predictable costs.

### Setup (20 minutes)

1. **Create Droplet:**
   - Size: Basic $6/month (1GB RAM)
   - Image: Ubuntu 22.04
   - Add SSH key

2. **SSH into server:**
```bash
ssh root@your_droplet_ip
```

3. **Install dependencies:**
```bash
# Update system
apt update && apt upgrade -y

# Install Python
apt install python3 python3-pip python3-venv nginx -y

# Create user
adduser vngen
usermod -aG sudo vngen
su - vngen
```

4. **Deploy app:**
```bash
# Clone repo
git clone https://github.com/vitaliibabynin/visual-novel-generator.git
cd visual-novel-generator
git checkout claude/visual-novel-generator-011CUzhr8sik4QYQLoGQ1xjF

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
nano .env
# Add your API keys

# Install gunicorn for production
pip install gunicorn
```

5. **Create systemd service:**
```bash
sudo nano /etc/systemd/system/vngen.service
```

```ini
[Unit]
Description=Visual Novel Generator
After=network.target

[Service]
User=vngen
WorkingDirectory=/home/vngen/visual-novel-generator
Environment="PATH=/home/vngen/visual-novel-generator/venv/bin"
ExecStart=/home/vngen/visual-novel-generator/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app

[Install]
WantedBy=multi-user.target
```

6. **Configure Nginx:**
```bash
sudo nano /etc/nginx/sites-available/vngen
```

```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/vngen /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

7. **Start service:**
```bash
sudo systemctl start vngen
sudo systemctl enable vngen
```

### Pricing:
- $6/month for basic droplet
- Predictable, no surprises

### Pros:
- Full control
- Persistent storage
- No cold starts
- Cheapest for 24/7 operation

### Cons:
- Manual setup
- You manage updates/security
- No auto-scaling

---

## 📊 Comparison Table

| Platform | Free Tier | Monthly Cost | Setup Time | Best For |
|----------|-----------|--------------|------------|----------|
| **Render.com** | ✅ Yes (limited) | $0-7 | 5 min | MVP/Testing |
| **Railway** | ❌ ($5 credit) | $5-10 | 5 min | Quick launch |
| **Fly.io** | ✅ Yes (generous) | $0-5 | 10 min | Free production |
| **DO App Platform** | ❌ | $5-12 | 10 min | Managed ease |
| **VPS (DigitalOcean)** | ❌ | $6 | 20 min | Full control |
| **Heroku** | ❌ | $7+ | 10 min | Legacy choice |

---

## 🎯 Recommendations

### For Your Use Case:

1. **Just testing/MVP?** → **Render.com (Free)** or **Fly.io (Free)**
2. **Ready for users?** → **Railway ($5)** or **Fly.io (Free tier)**
3. **High volume expected?** → **DigitalOcean VPS ($6)**
4. **Want ComfyUI integration?** → **VPS** (so ComfyUI and app are close)

---

## ⚠️ Important: File Storage Considerations

### The Problem:
Your app stores generated stories and images on disk. Many platforms have **ephemeral filesystems** (files reset on deploy).

### Solutions:

**Option A: Use Persistent Disks** (Render, Fly.io)
- Configure as shown above
- Files persist across deploys

**Option B: Use Cloud Storage** (S3, Cloudflare R2, DigitalOcean Spaces)
- Modify `storage.py` and `image_generator.py` to use S3
- Better for scaling
- Small additional cost (~$0.02/GB/month)

**Option C: Database for metadata + Cloud for images**
- Store story JSON in PostgreSQL
- Images in S3/Cloudflare R2
- Most scalable

For MVP, **Option A (persistent disks) is simplest**.

---

## 🔐 Security Checklist

Before deploying:

- [ ] Use environment variables for API keys (never commit `.env`)
- [ ] Set `FLASK_ENV=production`
- [ ] Add rate limiting if expecting public traffic
- [ ] Consider adding user authentication for story generation
- [ ] Set up monitoring (UptimeRobot, etc.)
- [ ] Enable HTTPS (automatic on all platforms above)

---

## 📈 Scaling Considerations

If your app gets popular:

1. **Add Redis** for caching
2. **Move to S3** for image storage
3. **Add PostgreSQL** for story metadata
4. **Use CDN** for serving images (Cloudflare)
5. **Queue system** for generation (Celery + Redis)
6. **Multiple workers** for parallel generation

---

## 🚀 Quick Start: Render.com Free Tier

This is the fastest way to get live:

1. Push code to GitHub ✅ (already done)
2. Go to https://render.com
3. New Web Service → Connect GitHub
4. Select your repo and branch
5. Configure as shown above
6. Deploy!

**Time to live: ~5 minutes**

---

## Need Help?

- Render docs: https://render.com/docs
- Railway docs: https://docs.railway.app
- Fly.io docs: https://fly.io/docs
- DigitalOcean docs: https://docs.digitalocean.com

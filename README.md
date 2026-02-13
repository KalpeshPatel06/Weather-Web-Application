# 🌤️ Weather App - Vercel Deployment

A modern weather application built with Python serverless functions and vanilla JavaScript, optimized for Vercel deployment.

## ✨ Features

- 🔍 Real-time weather search by city name
- 🌡️ Display temperature, humidity, wind speed, and conditions
- 🎨 Beautiful, responsive UI
- ⚡ Fast serverless API with Python
- 🚀 Optimized for Vercel deployment
- 📱 Mobile-friendly design

## 📋 Prerequisites

1. **GitHub Account** (to push your code)
2. **Vercel Account** (free - sign up at https://vercel.com)
3. **OpenWeatherMap API Key** (free - get at https://openweathermap.org/api)

## 🚀 Quick Deployment Guide

### Step 1: Get Your API Key

1. Visit https://openweathermap.org/api
2. Click "Sign Up" and create a free account
3. Verify your email
4. Go to "API Keys" section in your dashboard
5. Copy your API key
6. ⚠️ **Wait 10-15 minutes** for the API key to activate

### Step 2: Prepare Your Project

#### Option A: Using the ZIP file

1. **Extract the ZIP file** you downloaded:
   ```bash
   # On Windows: Right-click → Extract All
   # On Mac: Double-click the ZIP file
   # On Linux: 
   unzip weather-app-vercel.zip
   cd weather-app-vercel
   ```

2. **Initialize Git repository**:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   ```

3. **Push to GitHub**:
   ```bash
   # Create a new repository on GitHub.com first
   # Then run these commands:
   git remote add origin https://github.com/YOUR_USERNAME/weather-app.git
   git branch -M main
   git push -u origin main
   ```

#### Option B: Clone from GitHub (if already pushed)

```bash
git clone https://github.com/YOUR_USERNAME/weather-app.git
cd weather-app
```

### Step 3: Deploy to Vercel

#### Method 1: Deploy via Vercel Dashboard (Easiest) ⭐

1. **Go to Vercel**
   - Visit https://vercel.com
   - Click "Sign Up" or "Log In"
   - Choose "Continue with GitHub"

2. **Import Your Project**
   - Click "Add New..." → "Project"
   - Select "Import Git Repository"
   - Find and select your `weather-app` repository
   - Click "Import"

3. **Configure Project**
   - **Project Name**: Choose a name (e.g., `my-weather-app`)
   - **Framework Preset**: Select "Other"
   - **Root Directory**: Leave as `./`
   - **Build Command**: Leave empty (Vercel auto-detects)
   - **Output Directory**: Leave as default

4. **Add Environment Variable**
   - Click "Environment Variables"
   - Add variable:
     - **Name**: `OPENWEATHER_API_KEY`
     - **Value**: Your actual API key (paste it here)
   - Click "Add"

5. **Deploy**
   - Click "Deploy"
   - Wait 1-2 minutes
   - ✅ Your app is live!

6. **Visit Your App**
   - Click the deployment URL (e.g., `https://my-weather-app.vercel.app`)
   - Test the weather search

#### Method 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts:
# - Set up and deploy? Y
# - Which scope? [Select your account]
# - Link to existing project? N
# - Project name? weather-app
# - In which directory is your code? ./
# - Want to modify settings? N

# Add environment variable
vercel env add OPENWEATHER_API_KEY
# Paste your API key when prompted
# Select: Production, Preview, Development (all)

# Deploy to production
vercel --prod
```

### Step 4: Verify Deployment

1. **Test the homepage**: Visit your Vercel URL
2. **Test weather search**: Search for "London", "Paris", or "Tokyo"
3. **Check API health**: Visit `https://your-app.vercel.app/api/health`

## 📁 Project Structure

```
weather-app-vercel/
├── api/
│   └── index.py              # Python serverless function
├── public/
│   └── index.html            # Frontend HTML/CSS/JS
├── .env.example              # Environment variables template
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
├── vercel.json              # Vercel configuration
└── README.md                # This file
```

## 🔧 API Endpoints

### Health Check
```
GET /api/health
Response: {"status": "healthy", "service": "weather-app"}
```

### Weather Search
```
POST /api/weather
Content-Type: application/json
Body: {"city": "London"}

Success Response:
{
  "success": true,
  "city": "London",
  "country": "GB",
  "temperature": 15.5,
  "feels_like": 14.2,
  "humidity": 72,
  "condition": "Partly Cloudy",
  "icon": "02d",
  "wind_speed": 3.5
}

Error Response:
{
  "error": "City 'InvalidCity' not found"
}
```

## 🛠️ Local Development

If you want to test locally before deploying:

### Using Vercel CLI (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Start local development server
vercel dev

# Open http://localhost:3000
```

### Using Python directly

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your API key

# You'll need to run a local server for the HTML
python -m http.server 8000

# Note: API endpoints won't work without Vercel CLI
```

## 🔄 Updating Your App

After making changes:

```bash
# Commit changes
git add .
git commit -m "Update feature"
git push origin main

# Vercel automatically deploys on push!
# Check deployment status at https://vercel.com
```

## 🎨 Customization

### Change Colors

Edit `public/index.html`, find the CSS section:

```css
/* Change gradient colors */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Change to your colors, for example: */
background: linear-gradient(135deg, #FF6B6B 0%, #4ECDC4 100%);
```

### Add Features

Edit `api/index.py` to add more weather data or new endpoints.

## ⚙️ Environment Variables

You can manage environment variables in Vercel:

1. Go to your project in Vercel dashboard
2. Click "Settings" → "Environment Variables"
3. Add/Edit variables
4. Redeploy for changes to take effect

**Available in all environments:**
- `OPENWEATHER_API_KEY` - Your OpenWeatherMap API key

## 🔒 Security Best Practices

- ✅ Never commit `.env` file
- ✅ Never share your API key publicly
- ✅ Use Vercel's environment variables
- ✅ API key is server-side only (not exposed to browser)

## 🐛 Troubleshooting

### "API key not set" error
- Check environment variable is set in Vercel dashboard
- Variable name must be exactly: `OPENWEATHER_API_KEY`
- Redeploy after adding variables

### "City not found" error
- Check spelling of city name
- Try major cities: London, Paris, Tokyo, New York
- API key might still be activating (wait 15 minutes)

### Deployment fails
- Check Vercel deployment logs
- Verify `requirements.txt` has correct dependencies
- Ensure `vercel.json` is not modified

### API returns 401 error
- API key needs 10-15 minutes to activate after creation
- Verify API key is correct in Vercel environment variables
- Check you haven't exceeded free tier limits (60 calls/minute)

### "Failed to fetch" error in browser
- Check browser console for errors
- Verify API endpoint URL is correct
- Check CORS isn't blocking requests

## 📊 Usage Limits

**OpenWeatherMap Free Tier:**
- 60 calls per minute
- 1,000,000 calls per month
- Current weather data only

**Vercel Free Tier:**
- 100 GB bandwidth per month
- Unlimited deployments
- Serverless function execution: 100 GB-hours

## 🔗 Custom Domain (Optional)

To use your own domain:

1. Go to Vercel dashboard
2. Select your project
3. Go to "Settings" → "Domains"
4. Click "Add Domain"
5. Follow the DNS configuration instructions

## 📝 Common Commands

```bash
# Deploy to production
vercel --prod

# Check deployment status
vercel ls

# View logs
vercel logs

# Remove deployment
vercel rm [deployment-url]

# Add environment variable
vercel env add OPENWEATHER_API_KEY

# Pull environment variables locally
vercel env pull
```

## 🎯 Next Steps

- ✅ Deploy successfully
- ✅ Test with different cities
- ✅ Share with friends
- ✅ Add to your portfolio
- ✅ Customize the design
- ⭐ Star the repo on GitHub

## 📞 Support

**If you encounter issues:**

1. Check the troubleshooting section above
2. Review Vercel deployment logs
3. Verify API key is active and correct
4. Check OpenWeatherMap API status

**Common Resources:**
- Vercel Docs: https://vercel.com/docs
- OpenWeatherMap Docs: https://openweathermap.org/api
- Python Vercel Guide: https://vercel.com/docs/functions/serverless-functions/runtimes/python

## 🎉 Success Checklist

Your app is working when:
- ✅ Homepage loads at your Vercel URL
- ✅ Search form is visible and responsive
- ✅ Searching for "London" shows weather data
- ✅ Temperature, humidity, and wind speed display
- ✅ Weather icon appears
- ✅ Error messages show for invalid cities
- ✅ `/api/health` returns healthy status

## 🚀 Advanced Features to Add

- [ ] 5-day weather forecast
- [ ] Geolocation support
- [ ] Save favorite cities
- [ ] Weather alerts
- [ ] Temperature unit toggle (°C/°F)
- [ ] Dark mode
- [ ] PWA support
- [ ] Weather charts

---

**Built with Python, JavaScript, and deployed on Vercel** ⚡

Need help? Check Vercel docs or create an issue on GitHub!

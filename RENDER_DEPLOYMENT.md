# Late Comers Management System - Render Deployment

## Deployed Application

This Flask application combines both student and teacher portals into a single app for easy deployment on Render.

## Features

- **Student Portal**: Submit late entry forms
- **Teacher Portal**: View and manage late entries by subject
- **Single Database**: SQLite database for persistent storage
- **Health Check**: `/health` endpoint for monitoring

## Routes

### Student Routes
- `/` or `/student` - Student form
- `/submit` - Submit late entry (POST)

### Teacher Routes
- `/teacher` - Teacher home (faculty list)
- `/teacher/<faculty>` - View entries for a faculty
- `/teacher/update/<faculty>/<id>` - Mark entry as "Noted"

### System Routes
- `/health` - Health check endpoint

## Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Access at http://localhost:10000
```

## Render Deployment

### Step 1: Push to GitHub

```bash
git add .
git commit -m "Prepare for Render deployment"
git push origin main
```

### Step 2: Create Web Service on Render

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository
4. Configure the service:

**Basic Settings:**
- **Name**: `late-comers-management-system`
- **Region**: Choose closest to your location
- **Branch**: `main`
- **Root Directory**: Leave empty (or specify if in subdirectory)
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Advanced Settings:**
- **Instance Type**: Free (or paid for better performance)
- **Environment Variables**: None required
- **Auto-Deploy**: Yes (recommended)

### Step 3: Deploy

Click "Create Web Service" and wait for deployment to complete (usually 2-5 minutes).

### Step 4: Access Your App

Once deployed, Render will provide a URL like:
```
https://late-comers-management-system.onrender.com
```

## Environment Variables (Optional)

You can set these in Render dashboard if needed:

- `PORT` - Automatically set by Render (default: 10000)
- `FLASK_ENV` - Set to `production` (optional)

## Database

The app uses SQLite with persistent storage. The database file (`latecomers.db`) is created automatically on first run.

**Note**: On Render's free tier, the filesystem is ephemeral, meaning the database will reset when the service restarts. For persistent storage, consider:
- Upgrading to a paid plan with persistent disk
- Using an external database (PostgreSQL, MySQL)
- Migrating to use Render's PostgreSQL database

## Troubleshooting

### Database Resets on Restart
- **Issue**: Render free tier has ephemeral storage
- **Solution**: Upgrade to paid plan or use external database

### Application Fails to Start
- Check build logs in Render dashboard
- Verify `requirements.txt` has all dependencies
- Ensure `Procfile` is correct

### Connection Timeout
- Render services sleep after 15 minutes of inactivity on free tier
- First request after sleep takes 30-60 seconds to wake up

### Check Logs
```bash
# View logs in Render dashboard
# Or use Render CLI:
render logs -s late-comers-management-system
```

## Migrating to PostgreSQL (Recommended for Production)

To use persistent PostgreSQL instead of SQLite:

1. Add PostgreSQL to `requirements.txt`:
```
psycopg2-binary==2.9.9
```

2. Update `app.py` to use PostgreSQL:
```python
import os
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL:
    # Use PostgreSQL
    result = urlparse(DATABASE_URL)
    conn = psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )
else:
    # Use SQLite (local development)
    import sqlite3
    conn = sqlite3.connect('latecomers.db')
```

3. Create PostgreSQL database on Render
4. Add `DATABASE_URL` environment variable

## Performance Tips

1. **Enable Auto-Deploy**: Automatically deploy on git push
2. **Use CDN**: For static assets if you add more CSS/JS
3. **Monitoring**: Use Render's built-in monitoring
4. **Upgrade Plan**: For better performance and persistent storage

## Support

For issues with Render deployment:
- [Render Documentation](https://render.com/docs)
- [Render Community Forum](https://community.render.com/)

## License

MIT License

# Media File Upload Configuration for Production

## Problem
After deployment, uploaded images/media files don't persist or display. This is because:
- Deployment environments (like Render) have ephemeral filesystems
- Uploaded files are lost when the app restarts
- Gunicorn doesn't serve local media files in production

## Solution: Use AWS S3 (or Compatible Service)

### Option 1: AWS S3 (Recommended)

#### Step 1: Create AWS S3 Bucket
1. Go to [AWS S3](https://s3.amazonaws.com)
2. Create a new bucket (e.g., `my-elearn-media`)
3. Make it **publicly readable** (for public course thumbnails)
4. Enable CORS:
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
       "AllowedOrigins": ["https://yourdomain.com"],
       "ExposeHeaders": ["ETag"],
       "MaxAgeSeconds": 3000
     }
   ]
   ```

#### Step 3: Create IAM User with S3 Access
1. Go to AWS IAM → Users
2. Create new user (e.g., `elearn-app`)
3. Attach policy (Inline Policy):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:*"
         ],
         "Resource": [
           "arn:aws:s3:::my-elearn-media",
           "arn:aws:s3:::my-elearn-media/*"
         ]
       }
     ]
   }
   ```
4. Generate Access Key ID and Secret Access Key

#### Step 4: Set Environment Variables on Render

1. Go to your Render service dashboard
2. Click **"Environment"** tab on the left
3. Add these environment variables:
   - `AWS_ACCESS_KEY_ID` = your_access_key
   - `AWS_SECRET_ACCESS_KEY` = your_secret_key
   - `AWS_STORAGE_BUCKET_NAME` = my-elearn-media
   - `AWS_S3_REGION_NAME` = us-east-1
   - `AWS_S3_CUSTOM_DOMAIN` = my-elearn-media.s3.us-east-1.amazonaws.com
   - `USE_S3` = true

4. Click **"Save"** - Render will automatically redeploy with these settings

#### Step 5: Deploy
```bash
git add requirements.txt core/settings.py core/urls.py
git commit -m "Add S3 media storage support"
git push
```

Your deployment will automatically:
- Install `django-storages` and `boto3`
- Use S3 for all media uploads
- Serve images from S3 CDN

---

### Option 2: Cloudinary (Easiest Setup - Recommended)

Cloudinary is easier to set up than AWS S3 and has a generous free tier!

#### Step 1: Create Cloudinary Account
1. Go to [Cloudinary.com](https://cloudinary.com) and sign up (free)
2. Go to your **Dashboard** - note your:
   - Cloud Name
   - API Key
   - API Secret

#### Step 2: Install Cloudinary Package
Update [requirements.txt](requirements.txt) (already done, just verify):
```
cloudinary==1.40.0
django-cloudinary-storage==0.3.10
```

#### Step 3: Update Settings
Add to your [core/settings.py](core/settings.py):

```python
# At the top of settings.py, add after imports:
import cloudinary
import cloudinary.api

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

# Later in settings.py, find STORAGES and update:
if os.environ.get('USE_CLOUDINARY'):
    INSTALLED_APPS.insert(0, 'cloudinary_storage')
    INSTALLED_APPS.insert(1, 'cloudinary')
    
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.environ.get('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.environ.get('CLOUDINARY_API_KEY'),
        'API_SECRET': os.environ.get('CLOUDINARY_API_SECRET'),
    }
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = '/media/'
```

#### Step 4: Add Render Environment Variables
1. Go to your Render dashboard → Environment
2. Add these variables:
   - `CLOUDINARY_CLOUD_NAME` = your_cloud_name
   - `CLOUDINARY_API_KEY` = your_api_key
   - `CLOUDINARY_API_SECRET` = your_api_secret
   - `USE_CLOUDINARY` = true

3. Click **Save** - Render auto-redeploys

#### Step 5: Deploy
```bash
git add requirements.txt core/settings.py
git commit -m "Add Cloudinary media storage"
git push
```

**That's it!** All image uploads go to Cloudinary automatically.

---

---

### Option 3: AWS S3

#### Step 1: Create AWS S3 Bucket
1. Go to [AWS S3](https://s3.amazonaws.com)
2. Create a new bucket (e.g., `my-elearn-media`)
3. Make it **publicly readable** (for public course thumbnails)
4. Enable CORS:
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "PUT", "POST", "DELETE", "HEAD"],
       "AllowedOrigins": ["https://yourdomain.com"],
       "ExposeHeaders": ["ETag"],
       "MaxAgeSeconds": 3000
     }
   ]
   ```

#### Step 2: Create IAM User with S3 Access
1. Go to AWS IAM → Users
2. Create new user (e.g., `elearn-app`)
3. Attach policy (Inline Policy):
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "s3:*"
         ],
         "Resource": [
           "arn:aws:s3:::my-elearn-media",
           "arn:aws:s3:::my-elearn-media/*"
         ]
       }
     ]
   }
   ```
4. Generate Access Key ID and Secret Access Key

#### Step 3: Create AWS S3 Bucket
Already covered above - same as Option 3 Step 1

#### Step 4: Set Environment Variables on Render

1. Go to your Render service dashboard
2. Click **"Environment"** tab on the left
3. Add these environment variables:
   - `AWS_ACCESS_KEY_ID` = your_access_key
   - `AWS_SECRET_ACCESS_KEY` = your_secret_key
   - `AWS_STORAGE_BUCKET_NAME` = my-elearn-media
   - `AWS_S3_REGION_NAME` = us-east-1
   - `AWS_S3_CUSTOM_DOMAIN` = my-elearn-media.s3.us-east-1.amazonaws.com
   - `USE_S3` = true

4. Click **"Save"** - Render will automatically redeploy with these settings

#### Step 5: Deploy
```bash
git add requirements.txt core/settings.py core/urls.py
git commit -m "Add S3 media storage support"
git push
```

Your deployment will automatically:
- Install `django-storages` and `boto3`
- Use S3 for all media uploads
- Serve images from S3 CDN

---

### Option 4: Local Storage (Development Only)
Spaces is S3-compatible and cheaper. Just change:
```
AWS_S3_ENDPOINT_URL=https://nyc3.digitaloceanspaces.com
AWS_S3_REGION_NAME=nyc3
AWS_STORAGE_BUCKET_NAME=my-space-name
```

---

## Troubleshooting

### Images still not showing after deployment?
1. Check env vars are set: `USE_S3=true`
2. Verify S3 bucket is public or has correct permissions
3. Check S3 bucket name and region match your AWS setup
4. Ensure IAM user has S3 permissions

### Test S3 Connection
```bash
python manage.py shell
from django.core.files.storage import default_storage
default_storage.exists('test.txt')  # Should return True if S3 is connected
```

### Upload new image from admin
1. Go to Admin → Courses (or any model with image)
2. Upload an image
3. Save
4. Check your S3 bucket - file should appear there
5. Image URL should be like: `https://bucket-name.s3.region.amazonaws.com/media/path/to/image.jpg`

---

## What Changed
- **requirements.txt**: Added `django-storages` and `boto3`
- **settings.py**: Added S3 configuration that activates when `USE_S3=true`
- **urls.py**: Modified to skip local media serving when using S3

When `USE_S3=false` (default in development), your app works as before with local `/media/` files.
When `USE_S3=true` (production), all uploads go to S3 and are served from S3.

No code changes needed in your views or models - Django handles it automatically!

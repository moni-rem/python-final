# Media File Upload Configuration for Production (Render)

## Problem
After deployment, uploaded images/media files don't persist or display. This is because:
- Render has an ephemeral filesystem - files are lost when the app restarts
- Gunicorn doesn't serve local media files in production
- You need cloud storage (S3, Cloudinary, etc.)

## Solution: Choose Your Storage Option

### **Option 1: Cloudinary (⭐ Easiest - Recommended for Beginners)**

Cloudinary has a **generous free tier** and takes 5 minutes to set up!

#### Step 1: Create Cloudinary Account
1. Go to [Cloudinary.com](https://cloudinary.com) → **Sign Up** (free)
2. Verify email
3. Go to your **Dashboard** and note:
   - **Cloud Name**
   - **API Key**
   - **API Secret**

#### Step 2: Update Core Settings
Edit [core/settings.py](core/settings.py) - add this code at the **bottom**:

```python
# Cloudinary Configuration
if os.environ.get('USE_CLOUDINARY') == 'true':
    INSTALLED_APPS.insert(0, 'cloudinary_storage')
    INSTALLED_APPS.insert(1, 'cloudinary')
    
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
    MEDIA_URL = '/media/'
```

#### Step 3: Add Render Environment Variables
1. Go to Render Dashboard → Your Service → **Environment** tab
2. Add these 4 variables:
   - `CLOUDINARY_CLOUD_NAME` = (your cloud name from Step 1)
   - `CLOUDINARY_API_KEY` = (your API key)
   - `CLOUDINARY_API_SECRET` = (your API secret)
   - `USE_CLOUDINARY` = `true`
3. Click **Save** (Render auto-redeploys)

#### Step 4: Deploy
```bash
# No need to update requirements.txt - already has cloudinary packages
git add core/settings.py
git commit -m "Add Cloudinary media storage"
git push
```

**Done!** Upload images from admin → they'll appear in Cloudinary automatically.

---

### **Option 2: AWS S3 (Most Reliable)**

More complex setup but industry standard.

#### Step 1: Create S3 Bucket
1. Go to [AWS Console](https://console.aws.amazon.com) → S3
2. **Create Bucket** (name: `my-elearn-media` or similar)
3. Make it **Publicly Readable**:
   - Permissions → Block public access → Uncheck all boxes
   - Add Bucket Policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Sid": "PublicRead",
         "Effect": "Allow",
         "Principal": "*",
         "Action": "s3:GetObject",
         "Resource": "arn:aws:s3:::my-elearn-media/*"
       }
     ]
   }
   ```
4. Enable CORS:
   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
       "AllowedOrigins": ["https://yourdomain.com"],
       "MaxAgeSeconds": 3000
     }
   ]
   ```

#### Step 2: Create IAM User
1. Go to AWS → IAM → **Users** → **Create User** (name: `elearn-app`)
2. Attach inline policy:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": "s3:*",
         "Resource": [
           "arn:aws:s3:::my-elearn-media",
           "arn:aws:s3:::my-elearn-media/*"
         ]
       }
     ]
   }
   ```
3. Generate **Access Key** → Save both:
   - Access Key ID
   - Secret Access Key

#### Step 3: Update Django Settings
Edit [core/settings.py](core/settings.py) - code already in place, just activate with env vars.

#### Step 4: Add Render Environment Variables
1. Render Dashboard → Environment tab
2. Add these:
   - `AWS_ACCESS_KEY_ID` = (from IAM)
   - `AWS_SECRET_ACCESS_KEY` = (from IAM)
   - `AWS_STORAGE_BUCKET_NAME` = `my-elearn-media`
   - `AWS_S3_REGION_NAME` = `us-east-1`
   - `AWS_S3_CUSTOM_DOMAIN` = `my-elearn-media.s3.us-east-1.amazonaws.com`
   - `USE_S3` = `true`
3. Click **Save**

#### Step 5: Deploy
```bash
git add requirements.txt core/settings.py
git commit -m "Add S3 media storage"
git push
```

---

### **Option 3: Local Storage (Development Only)**
```bash
# Don't set USE_CLOUDINARY or USE_S3
python manage.py runserver
# Files stored in /media/ locally
```

---

## Testing

### Test Cloudinary Setup
```bash
python manage.py shell
>>> from django.core.files.storage import default_storage
>>> default_storage.exists('test.txt')
# Should return True if connected
```

### Test from Admin
1. Admin → Courses (or any model with image)
2. Upload an image
3. Save
4. Open your S3 bucket or Cloudinary dashboard
5. Image should appear there

---

## Troubleshooting

**Images still not showing?**
- ✅ Check env vars are set (`USE_CLOUDINARY=true` or `USE_S3=true`)
- ✅ Check Cloudinary/S3 bucket for uploaded file
- ✅ Check file permissions (S3 bucket must be public for images)
- ✅ Verify API keys are correct in environment

**CLOUDINARY_CLOUD_NAME not set error?**
- Add `USE_CLOUDINARY=true` to Render environment

**Access Denied to S3?**
- Check IAM policy allows your bucket
- Verify Access Key ID and Secret are correct

---

## Which Option to Choose?

| Feature | Cloudinary | AWS S3 |
|---------|-----------|--------|
| **Setup Time** | 5 min | 15 min |
| **Free Tier** | 25GB | ❌ (paid) |
| **Cost** | Free-$99/mo | $0.023/GB |
| **CDN** | ✅ Built-in | ✅ CloudFront (extra) |
| **For Beginners** | ⭐ Recommended | More complex |

**Choose Cloudinary** if: First time, want free tier, want simplicity
**Choose S3** if: Need more control, using other AWS services, expecting high volume

---

## Code Changes Summary

### requirements.txt
- Added `cloudinary` and `django-cloudinary-storage`
- Already had `boto3` and `django-storages`

### core/settings.py
- Added Cloudinary config (activates when `USE_CLOUDINARY=true`)
- S3 config already in place (activates when `USE_S3=true`)

### core/urls.py
- Modified to skip local media serving when using cloud storage

**Your Django code needs NO changes** - automatically uses cloud storage!

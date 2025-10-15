# Supabase Setup Guide for PaperTrail

This guide explains how to set up Supabase for file storage in the PaperTrail project.

## Prerequisites

- A Supabase account (https://supabase.com)
- Python environment with required packages installed

## Step 1: Create Supabase Project

1. Go to https://supabase.com and sign in
2. Click "New Project"
3. Fill in project details:
   - Name: PaperTrail
   - Database Password: (choose a strong password)
   - Region: (choose closest to your users)

## Step 2: Create Storage Bucket

1. In your Supabase dashboard, go to **Storage**
2. Click "Create a new bucket"
3. Settings:
   - Name: `papertrail-storage`
   - Public bucket: **Yes** (to allow public file access)
4. Click "Create bucket"

## Step 3: Set Bucket Policies

1. Click on your bucket name
2. Go to "Policies" tab
3. Add these policies:

### Policy 1: Allow Public Read Access
```sql
CREATE POLICY "Public Access"
ON storage.objects FOR SELECT
USING ( bucket_id = 'papertrail-storage' );
```

### Policy 2: Allow Authenticated Uploads
```sql
CREATE POLICY "Authenticated users can upload"
ON storage.objects FOR INSERT
WITH CHECK ( bucket_id = 'papertrail-storage' AND auth.role() = 'authenticated' );
```

### Policy 3: Allow Users to Update Their Own Files
```sql
CREATE POLICY "Users can update own files"
ON storage.objects FOR UPDATE
USING ( bucket_id = 'papertrail-storage' AND auth.uid() = owner );
```

### Policy 4: Allow Users to Delete Their Own Files
```sql
CREATE POLICY "Users can delete own files"
ON storage.objects FOR DELETE
USING ( bucket_id = 'papertrail-storage' AND auth.uid() = owner );
```

## Step 4: Get Your Credentials

1. Go to **Settings** > **API**
2. Copy the following:
   - **Project URL**: `https://[your-project-ref].supabase.co`
   - **Service Role Key** (anon public): The `service_role` key

## Step 5: Update Environment Variables

Update your `.env` file with the credentials:

```env
SUPABASE_URL=https://rhkmdnwrdbvicxpanhnz.supabase.co
SUPABASE_SERVICE_KEY=your_service_role_key_here
SUPABASE_BUCKET=papertrail-storage
```

**Important**: Never commit the `.env` file to git. It's already in `.gitignore`.

## Step 6: Verify Setup

Run this Django management command to test the connection:

```bash
python manage.py shell
```

Then in the shell:

```python
from resources.supabase_storage import supabase_storage

# Test listing files
files = supabase_storage.list_files()
print(f"Connection successful! Found {len(files)} files.")
```

## Folder Structure in Supabase

The project uses the following folder structure in the bucket:

```
papertrail-storage/
├── resources/          # User-uploaded resource files
│   ├── [uuid].pdf
│   ├── [uuid].pptx
│   └── [uuid].docx
└── profiles/           # User profile pictures (future)
    └── [uuid].jpg
```

## File Upload Process

1. User uploads file through Django form
2. File is sent to `supabase_storage.upload_file()`
3. File is uploaded to Supabase with unique UUID filename
4. Public URL is returned and saved to database
5. Users can access file via the public URL

## Security Considerations

- Files are stored with UUID filenames to prevent filename conflicts
- Public bucket allows read access to all files
- Write access requires authentication (handled by service key)
- Sensitive files should not be uploaded to public bucket

## Troubleshooting

### Error: "Invalid API key"
- Check that `SUPABASE_SERVICE_KEY` is correctly copied
- Make sure you're using the `service_role` key, not the `anon` key

### Error: "Bucket not found"
- Verify the bucket name is exactly `papertrail-storage`
- Check that the bucket exists in your Supabase dashboard

### Error: "Permission denied"
- Ensure bucket policies are correctly set
- Verify the bucket is marked as public

## Additional Resources

- [Supabase Storage Documentation](https://supabase.com/docs/guides/storage)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)
- [Storage Policies Guide](https://supabase.com/docs/guides/storage/security/access-control)

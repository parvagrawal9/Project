# How to Create .env File

Since `.env` files contain sensitive information, you need to create it manually.

## Steps:

1. **Create the file**: In the `backend` directory, create a new file named `.env` (with the dot at the beginning)

2. **Add the following content**:

```env
# Supabase Configuration
# Get these from your Supabase project: Settings → API
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Webhook Configuration (optional)
# Set this if you want to receive notifications when food assistance requests are created
FULFILLMENT_WEBHOOK_URL=https://your-webhook-url.com/api/fulfillment

# CORS Configuration
# Add your frontend URLs here (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

3. **Replace the placeholder values**:
   - `SUPABASE_URL`: Your Supabase project URL (e.g., `https://xxxxx.supabase.co`)
   - `SUPABASE_KEY`: Your Supabase anon/public key
   - `FULFILLMENT_WEBHOOK_URL`: (Optional) Your webhook endpoint URL
   - `CORS_ORIGINS`: Your frontend URLs (default is already set)

## Quick Method (Windows PowerShell):

```powershell
cd backend
@"
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Webhook Configuration (optional)
FULFILLMENT_WEBHOOK_URL=https://your-webhook-url.com/api/fulfillment

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
"@ | Out-File -FilePath .env -Encoding utf8
```

## Quick Method (Linux/Mac):

```bash
cd backend
cat > .env << 'EOF'
# Supabase Configuration
SUPABASE_URL=your_supabase_project_url_here
SUPABASE_KEY=your_supabase_anon_key_here

# Webhook Configuration (optional)
FULFILLMENT_WEBHOOK_URL=https://your-webhook-url.com/api/fulfillment

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
EOF
```

## Important Notes:

- ✅ The `.env` file is already in `.gitignore`, so it won't be committed to GitHub
- ✅ Never share your `.env` file or commit it to version control
- ✅ Replace all placeholder values with your actual credentials
- ✅ After creating the file, restart your backend server for changes to take effect

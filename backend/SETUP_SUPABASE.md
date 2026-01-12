# Supabase Setup Guide

## Prerequisites
1. A Supabase account (sign up at https://supabase.com)
2. A Supabase project created

## Setup Steps

### 1. Create the Database Table

Run the SQL script in your Supabase SQL Editor:

1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the contents of `supabase_schema.sql`
4. Click **Run** to execute the script

This will create the `food_assistance_requests` table with all necessary columns, indexes, and views.

### 2. Get Your Supabase Credentials

1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **API**
3. Copy the following:
   - **Project URL** (this is your `SUPABASE_URL`)
   - **anon/public key** (this is your `SUPABASE_KEY`)

### 3. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# Webhook Configuration (optional)
FULFILLMENT_WEBHOOK_URL=https://your-webhook-url.com/api/fulfillment

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 4. Verify Connection

Start your backend server:
```bash
cd backend
uvicorn main:app --reload
```

You should see:
- ✅ `Supabase client initialized successfully` (if credentials are correct)
- ⚠️ `Warning: SUPABASE_URL and SUPABASE_KEY not set` (if missing)

### 5. Test the Integration

1. Start a chat conversation
2. Complete the food assistance form (name, age, location, food requirement)
3. Check your Supabase dashboard → **Table Editor** → `food_assistance_requests`
4. You should see the new record with all the data

## Webhook Setup (Optional)

If you want to receive notifications when a food assistance request is created:

1. Set up a webhook endpoint that accepts POST requests
2. Add the URL to `FULFILLMENT_WEBHOOK_URL` in your `.env` file
3. The webhook will receive a JSON payload with:
   ```json
   {
     "person_name": "John Doe",
     "age": 30,
     "location": "New York",
     "food_request": "Vegetarian meal",
     "assistance_type": "immediate"
   }
   ```

## Troubleshooting

### Data not saving to Supabase
- Check that `SUPABASE_URL` and `SUPABASE_KEY` are set correctly
- Verify the table `food_assistance_requests` exists in your Supabase project
- Check the backend console for error messages
- Ensure Row Level Security (RLS) policies allow inserts (see `supabase_schema.sql`)

### Webhook not working
- Verify `FULFILLMENT_WEBHOOK_URL` is set in `.env`
- Check that your webhook endpoint is accessible
- Check backend console for webhook error messages

## GitHub Integration

To connect your project to GitHub:

1. Initialize git (if not already done):
   ```bash
   git init
   ```

2. Create a `.gitignore` file (if not exists):
   ```
   .env
   venv/
   __pycache__/
   *.pyc
   .DS_Store
   ```

3. Add and commit your code:
   ```bash
   git add .
   git commit -m "Initial commit"
   ```

4. Create a new repository on GitHub

5. Connect and push:
   ```bash
   git remote add origin https://github.com/yourusername/your-repo.git
   git branch -M main
   git push -u origin main
   ```

**Important**: Never commit your `.env` file with real credentials. Use `.env.example` for documentation.

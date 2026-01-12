# Environment Variables Structure

This document explains the structure and purpose of each environment variable in the `.env` file.

## File Structure

Your `.env` file should be located at: `backend/.env`

## Required Variables

### 1. Supabase Configuration

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key-here
```

**Purpose**: Connect to your Supabase database to store food assistance requests.

**How to get**:
1. Go to [Supabase Dashboard](https://app.supabase.com)
2. Select your project
3. Navigate to **Settings** → **API**
4. Copy:
   - **Project URL** → `SUPABASE_URL`
   - **anon public** key → `SUPABASE_KEY`

**Example**:
```env
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYxNjIzOTAyMiwiZXhwIjoxOTMxODE1MDIyfQ.example
```

---

### 2. CORS Configuration

```env
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

**Purpose**: Allow your frontend to make requests to the backend API.

**Format**: Comma-separated list of URLs (no spaces after commas)

**Examples**:
```env
# Development
CORS_ORIGINS=http://localhost:3000,http://localhost:8000

# Production (add your production URLs)
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# Multiple environments
CORS_ORIGINS=http://localhost:3000,https://staging.yourdomain.com,https://yourdomain.com
```

---

## Optional Variables

### 3. Webhook Configuration

```env
FULFILLMENT_WEBHOOK_URL=https://your-webhook-url.com/api/fulfillment
```

**Purpose**: Send notifications to an external service when a food assistance request is created.

**When to use**: If you want to integrate with:
- Notification services (SMS, Email)
- Third-party APIs
- Custom fulfillment systems
- NGO partner systems

**Webhook Payload**:
```json
{
  "person_name": "John Doe",
  "age": 30,
  "location": "New York",
  "food_request": "Vegetarian meal for 2 people",
  "assistance_type": "immediate"
}
```

**Leave empty** if you don't need webhook notifications:
```env
# FULFILLMENT_WEBHOOK_URL=
```

---

## Complete Example

Here's a complete `.env` file example:

```env
# Supabase Configuration
SUPABASE_URL=https://abcdefghijklmnop.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFiY2RlZmdoaWprbG1ub3AiLCJyb2xlIjoiYW5vbiIsImlhdCI6MTYxNjIzOTAyMiwiZXhwIjoxOTMxODE1MDIyfQ.example

# Webhook Configuration (Optional)
FULFILLMENT_WEBHOOK_URL=https://api.example.com/webhook/fulfillment

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8000,https://yourdomain.com
```

---

## Quick Setup Steps

1. **Copy the template**:
   ```bash
   cd backend
   cp .env.example .env
   ```

2. **Edit `.env`** and replace placeholder values with your actual credentials

3. **Verify**:
   - No spaces around `=` signs
   - URLs don't have trailing slashes
   - Keys are in quotes only if they contain special characters

4. **Test**:
   ```bash
   # Start the server
   uvicorn main:app --reload
   
   # Check console for:
   # ✅ "Supabase client initialized successfully"
   # ❌ "Warning: SUPABASE_URL and SUPABASE_KEY not set"
   ```

---

## Security Notes

⚠️ **IMPORTANT**:
- Never commit `.env` to git
- Never share your `.env` file
- Use `.env.example` for documentation
- Rotate keys if accidentally exposed
- Use different keys for development and production

---

## Troubleshooting

### "Supabase not configured" warning
- Check that `SUPABASE_URL` and `SUPABASE_KEY` are set
- Verify no extra spaces or quotes
- Restart the server after changing `.env`

### CORS errors
- Add your frontend URL to `CORS_ORIGINS`
- Ensure URLs match exactly (including http/https)
- Restart the server after changes

### Webhook not working
- Verify `FULFILLMENT_WEBHOOK_URL` is a valid URL
- Check that your webhook endpoint accepts POST requests
- Check server logs for webhook errors

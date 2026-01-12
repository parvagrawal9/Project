# Zero Hunger Platform - LangGraph Setup Guide

## Overview
This guide will help you set up the AI-powered food assistance platform with LangGraph workflow.

## Prerequisites
- Python 3.8+
- Node.js 16+ (for React frontend)
- Supabase account (free tier works)

## Backend Setup

### 1. Install Python Dependencies
```bash
cd backend
pip install -r ../requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file in the project root:

```env
# Database (Supabase)
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

# Optional: Fulfillment Webhook
FULFILLMENT_WEBHOOK_URL=https://your-webhook-url.com/fulfillment

# CORS (for frontend)
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### 3. Set Up Supabase Database

1. Go to your Supabase project dashboard
2. Navigate to SQL Editor
3. Run the following SQL to create the `food_assistance_requests` table:

```sql
CREATE TABLE IF NOT EXISTS food_assistance_requests (
    id BIGSERIAL PRIMARY KEY,
    person_name TEXT NOT NULL,
    age INTEGER NOT NULL,
    location TEXT NOT NULL,
    food_request TEXT NOT NULL,
    assistance_type TEXT NOT NULL CHECK (assistance_type IN ('immediate', 'scheduled', 'ngo_referral')),
    session_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending' CHECK (status IN ('pending', 'confirmed', 'delivered', 'cancelled')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create index for faster queries
CREATE INDEX IF NOT EXISTS idx_food_assistance_session ON food_assistance_requests(session_id);
CREATE INDEX IF NOT EXISTS idx_food_assistance_status ON food_assistance_requests(status);
CREATE INDEX IF NOT EXISTS idx_food_assistance_created ON food_assistance_requests(created_at);
```

### 4. Run Backend Server
```bash
cd backend
uvicorn main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`
API docs at `http://localhost:8000/docs`

## Frontend Setup

### 1. Install Node Dependencies
```bash
cd frontend
npm install
```

### 2. Configure Environment (Optional)
Create a `.env` file in the `frontend` directory:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Run Development Server
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## Testing the System

### 1. Test Chat Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "I need food urgently"}'
```

### 2. Test in Browser
1. Open `http://localhost:3000`
2. Type a message like "I'm hungry and need food now"
3. Follow the conversation flow
4. Provide: Name, Age, Location, Food Requirement
5. System will trigger fulfillment when all data is collected

## Conversation Flow

1. **User sends message** → `start_node`
2. **Intent classification** → `router_node`
   - Urgent keywords → `immediate_food`
   - Scheduled keywords → `scheduled_food`
   - NGO keywords → `ngo_referral`
3. **Data collection** → Assistance node
   - Asks for Name
   - Asks for Age
   - Asks for Location
   - Asks for Food Requirement
4. **Fulfillment trigger** → When all data collected
   - Stores in Supabase
   - Sends notification (if webhook configured)

## API Endpoints

- `POST /chat` - Main chat endpoint
- `POST /api/ai/chat` - Alternative chat endpoint (same functionality)
- `GET /health` - Health check
- `GET /docs` - API documentation

## Troubleshooting

### Supabase Connection Issues
- Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
- Check Supabase project is active
- Ensure table `food_assistance_requests` exists

### LangGraph Import Errors
- Ensure all dependencies are installed: `pip install langgraph langchain langchain-core`
- Check Python version: `python --version` (should be 3.8+)

### Frontend Connection Issues
- Verify backend is running on port 8000
- Check CORS settings in `backend/main.py`
- Verify `VITE_API_URL` in frontend `.env`

## Production Deployment

1. **Backend**: Deploy to services like Railway, Render, or AWS
2. **Frontend**: Build and deploy to Vercel, Netlify, or similar
3. **Database**: Use Supabase production instance
4. **Environment**: Set production environment variables

## Security Notes

- Never commit `.env` files
- Use environment variables for all secrets
- Enable Supabase Row Level Security (RLS) for production
- Use HTTPS in production
- Implement rate limiting for API endpoints

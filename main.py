from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from models.db_models import Base
from services.utils import engine
from routers import auth, events, upload, notification, user, company
from services.scheduler import start_scheduler
from services.telegram_bot import ScheduleBotWebhook
import os

app = FastAPI(title="Schedule Management API", version="1.0.0")

# CORS middleware
# Use explicit allowed origins when allow_credentials=True to ensure the
# Access-Control-Allow-Origin header is included for browser requests.
# You can override defaults via env var:
#   CORS_ALLOW_ORIGINS="https://formskartscheduler.bolt.host,https://new-chat-ulhd.bolt.host"
origins_env = os.getenv("CORS_ALLOW_ORIGINS", "")
if origins_env.strip():
    allowed_origins = [o.strip() for o in origins_env.split(",") if o.strip()]
else:
    allowed_origins = [
        "https://formskartscheduler.bolt.host",
        "https://new-chat-ulhd.bolt.host",
        # Render frontend
        "https://scheduler-formskart.onrender.com",
        # Optional: local dev
        "http://localhost",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=[
        "Authorization",
        "Content-Type",
        "Accept",
        "Origin",
        "X-Requested-With",
    ],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Include routers
app.include_router(auth.router)
app.include_router(events.router)
app.include_router(upload.router)
app.include_router(notification.router)
app.include_router(company.router)
app.include_router(user.router)

# Health check
@app.get("/health")
async def health_check():
    from datetime import datetime
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Telegram webhook
webhook_bot = ScheduleBotWebhook()

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    body = await request.body()
    result = await webhook_bot.webhook_handler(body.decode())
    return result

# Start scheduler
start_scheduler()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from models.db_models import Base
from services.utils import engine
from routers import auth, events, upload, notification, user, company
from services.scheduler import start_scheduler
from services.telegram_bot import ScheduleBotWebhook

app = FastAPI(title="Schedule Management API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

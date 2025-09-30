# routers/upload.py
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session
from services.text_extraction import extract_text_from_pdf, extract_text_from_docx
from services.gemini_ai import extract_events_with_gemini
from services.utils import get_current_user, get_database
from models.db_models import Event, User
from datetime import datetime

router = APIRouter(tags=["upload"])

@router.post("/upload-schedule")
async def upload_schedule(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_database)
):
    if file.content_type not in ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
        raise HTTPException(status_code=400, detail="Only PDF and DOCX files are supported")
    file_content = await file.read()
    if file.content_type == "application/pdf":
        extracted_text = extract_text_from_pdf(file_content)
    else:
        extracted_text = extract_text_from_docx(file_content)
    if not extracted_text.strip():
        raise HTTPException(status_code=400, detail="No text could be extracted from the file")
    events_data = await extract_events_with_gemini(extracted_text)
    saved_events = []
    for event_data in events_data:
        try:
            event_datetime = datetime.strptime(f"{event_data['date']} {event_data['time']}", "%Y-%m-%d %H:%M")
            db_event = Event(
                user_id=current_user.id,
                title=event_data['title'],
                description=event_data.get('description', ''),
                event_date=event_datetime,
                event_time=event_data['time'],
                source_file=file.filename
            )
            db.add(db_event)
            saved_events.append(event_data)
        except (ValueError, KeyError) as e:
            print(f"Error parsing event: {e}")
            continue
    db.commit()
    return {
        "message": f"Successfully processed {len(saved_events)} events from {file.filename}",
        "events": saved_events
    }


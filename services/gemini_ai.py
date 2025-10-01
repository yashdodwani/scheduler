from fastapi import HTTPException
import google.generativeai as genai
import json
from typing import List
from config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

async def extract_events_with_gemini(text: str) -> List[dict]:
    try:
        model = genai.GenerativeModel('models/gemini-2.5-flash')
        prompt = f"""
        Extract all events, dates, and times from the following text. Return the result as a JSON array of objects with the following structure:
        [
            {{
                "title": "Event title",
                "description": "Brief description of the event",
                "date": "YYYY-MM-DD",
                "time": "HH:MM" (24-hour format, use "00:00" if no time specified),
                "details": "Any additional details"
            }}
        ]
        Text to analyze:
        {text}
        Please ensure:
        1. All dates are in YYYY-MM-DD format
        2. All times are in HH:MM format (24-hour)
        3. Extract all scheduled events, deadlines, meetings, etc.
        4. If year is not mentioned, assume 2025
        5. Return only valid JSON, no additional text
        """
        response = model.generate_content(prompt)
        try:
            events_data = json.loads(response.text.strip())
            return events_data
        except json.JSONDecodeError:
            text = response.text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.endswith("```"):
                text = text[:-3]
            events_data = json.loads(text.strip())
            return events_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing with Gemini: {str(e)}")

import os
import httpx

CHAT_API_URL = "http://localhost:8000/chat"
OCR_API_URL = "http://localhost:8000/analyze-image"

async def get_chat_response_async(query: str) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.post(CHAT_API_URL, json={"query": query})
        r.raise_for_status()
        return r.json()["text"]

import os
import base64
import aiohttp
import sqlite3
from typing import List, Dict, Union

CAPTION_API_URL = "http://localhost:8000/analyze-image"
FIXED_PROMPT = (
    "дай список только незачтенных предметов, если есть, список преподавателей по ним, "
    "количество баллов в формате предмет|балл|преподаватели через запятую, разные предметы на разных строках"
)

async def get_ocr_response_async(image_path: str, prompt: str = FIXED_PROMPT) -> str:
    """
    Отправляет изображение на OCR-сервер и получает распознанный текст.
    """
    if not os.path.isfile(image_path):
        raise FileNotFoundError(f"Файл не найден: {image_path}")
    with open(image_path, "rb") as f:
        image_bytes = f.read()
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    payload = {
        "image_base64": image_base64,
        "prompt": prompt,
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(CAPTION_API_URL, json=payload) as resp:
            resp.raise_for_status()
            resp_json = await resp.json()
            return resp_json.get("text", "")

def process_text(text: str, db_path: str = "../schedule.db") -> Union[str, List[Dict]]:
    """
    Парсит текст по шаблону и вытаскивает данные из базы.
    Поддерживает несколько преподавателей через запятую.
    """
    lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
    # Проверяем, есть ли валидные строки с двумя разделителями
    for line in lines:
        if line.count('|') != 2:
            return "По данному предмету у тебя нет задолженности 🤩"

    result = []
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    for line in lines:
        subject, score_str, teachers_str = [part.strip() for part in line.split('|')]
        # Обработка балла
        try:
            score = float(score_str.replace(",", "."))
        except ValueError:
            score = 0.0
        reason = "недобор баллов" if score < 40 and score != 0.0 else "провален экзамен"

        # Разбор списка преподавателей
        teachers = [t.strip() for t in teachers_str.split(',') if t.strip()]
        # Сбор информации о встречах для каждого преподавателя
        meetings = []
        for teacher in teachers:
            cursor.execute(
                """
                SELECT day_of_week, time_range, room, contact 
                FROM schedule 
                WHERE full_name = ?
                """,
                (teacher,)
            )
            row = cursor.fetchone()
            if row:
                day_of_week, time_range, room, contact = row
                meeting_info = {
                    "день недели": day_of_week,
                    "время": time_range,
                    "аудитория": room,
                    "контакт": contact
                }
            else:
                meeting_info = {
                    "день недели": "нет данных",
                    "время": "нет данных",
                    "аудитория": "нет данных",
                    "контакт": "нет данных"
                }
            meetings.append({teacher: meeting_info})

        entry = {
            "предмет": subject,
            "балл": score,
            "причина": reason,
            "преподаватели": teachers,
            "места встречи": meetings
        }
        result.append(entry)

    conn.close()
    return result

def format_for_telegram(entries: Union[str, List[Dict]]) -> str:
    """
    Формирует красивый HTML-текст для Telegram на основе данных.
    """
    if isinstance(entries, str):
        return entries  # например, "все хорошо"

    message_lines = []

    for entry in entries:
        lines = [
            f"🎓 <b>{entry['предмет']}</b>",
            f"🏅 <b>Балл: {entry['балл']}</b>",
            f"{'❗️' if entry['причина'] == 'недобор баллов' else '❌'} <i>Причина: {entry['причина']}</i>",
        ]

        for meeting in entry.get('места встречи', []):
            for teacher, details in meeting.items():
                lines.extend([
                    f"👤 Преподаватель: {teacher}",
                    f"📍 <u>Место встречи</u>:",
                    f"   📆 День недели: {details['день недели']}",
                    f"   ⏰ Время: {details['время']}",
                    f"   🚪 Аудитория: {details['аудитория']}",
                    f"   ✉️ Контакт: {details['контакт']}",
                    "────────────"
                ])
        message_lines.append('\n'.join(lines))

    return "\n\n".join(message_lines)

async def analyze_image_and_format(image_path: str, db_path: str = "schedule.db") -> str:
    """
    Главная функция — для вызова из хендлера:
    1. OCR, 2. Парсинг, 3. БД, 4. Форматирование под Telegram
    """
    text = await get_ocr_response_async(image_path)
    if not text:
        return "❌ Текст не распознан"
    entries = process_text(text, db_path)
    print(entries)
    return format_for_telegram(entries)

import os
import httpx

CHAT_API_URL = "http://localhost:8000/chat"
OCR_API_URL = "http://localhost:8000/ocr"

async def get_chat_response_async(query: str) -> str:
    async with httpx.AsyncClient() as client:
        r = await client.post(CHAT_API_URL, json={"query": query})
        r.raise_for_status()
        return r.json()["text"]

async def get_ocr_response_async(image_path: str) -> dict:
    async with httpx.AsyncClient() as client:
        with open(image_path, "rb") as f:
            files = {"file": (os.path.basename(image_path), f, "image/jpeg")}
            r = await client.post(OCR_API_URL, files=files)
        r.raise_for_status()
        return r.json()

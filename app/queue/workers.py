import asyncio
import base64
import os

from ..db.collections.files import files_collection
from bson import ObjectId
from pdf2image import convert_from_path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def process_file(id: str, file_path: str):
    asyncio.run(process_file_async(id, file_path))


async def process_file_async(id: str, file_path: str):
    object_id = ObjectId(id)

    try:
        await files_collection.update_one({"_id": object_id}, {
            "$set": {
                "status": "processing"
            }
        })

        # Step-1: Convert PDF to images
        pages = convert_from_path(file_path)
        images = []

        for i, page in enumerate(pages):
            image_save_path = f"/mnt/uploads/images/{id}/image-{i}.jpg"
            os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
            page.save(image_save_path, 'JPEG')
            images.append(image_save_path)

        await files_collection.update_one({"_id": object_id}, {
            "$set": {
                "status": "image_conversion_succeeded"
            }
        })

        api_key = os.getenv("OPENAI_API_KEY", "")
        if not api_key or api_key.startswith("placeholder_"):
            raise RuntimeError("OPENAI_API_KEY is not configured")

        client = OpenAI(api_key=api_key)
        images_base64 = [encode_image(img) for img in images]
        content = [
            {
                "type": "text",
                "text": (
                    "Analyze this PDF document. Summarize the content, extract key "
                    "points, and call out important details from every page."
                )
            }
        ]

        for image_base64 in images_base64:
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_base64}"
                }
            })

        result = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ]
        )

        await files_collection.update_one({"_id": object_id}, {
            "$set": {
                "status": "processed",
                "result": result.choices[0].message.content
            }
        })
    except Exception as exc:
        await files_collection.update_one({"_id": object_id}, {
            "$set": {
                "status": "failed",
                "result": str(exc)
            }
        })
        raise

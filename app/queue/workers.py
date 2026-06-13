# rq worker --with-scheduler --url redis://valkey:6379
# for starting the worker
from ..db.collections.files import files_collection
from bson import ObjectId
from pdf2image import convert_from_path
import os
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


def encode_image(image_path):
    with open(image_path, 'rb') as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


async def process_file(id: str, file_path: str):
    await files_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "processing"
        }
    })

    # Step-1: Convert PDF to image
    pages = convert_from_path(file_path)
    images = []

    for i, page in enumerate(pages):
        image_save_path = f"/mnt/uploads/images/{id}/image-{i}.jpg"
        os.makedirs(os.path.dirname(image_save_path), exist_ok=True)
        page.save(image_save_path, 'JPEG')
        images.append(image_save_path)

    await files_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "Image conversion succeeded."
        }
    })

    images_base64 = [encode_image(img) for img in images]

    result = client.chat.completions.create(
        model="gpt-4.1",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Based on the resume below, Roast this resume"
                    },
                    {
                        "type": "image_url",
                        # flake8: noqa
                        "image_url": {"url": f"data:image/jpeg;base64,{images_base64}"}
                    }
                ]
            }
        ]
    )

    await files_collection.update_one({"_id": ObjectId(id)}, {
        "$set": {
            "status": "processed",
            "result": result.choices[0].message.content
        }
    })

import os
import requests

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"


def generate_description_from_title(title):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3001",   # optional
        "X-OpenRouter-Title": "AI Blog Platform",  # optional
    }

    payload = {
        "model": "openrouter/free",
        "messages": [
            {
                "role": "system",
                "content": "You are a helpful blog writing assistant."
            },
            {
                "role": "user",
                "content": f"""
Generate a blog description for the title: "{title}"

Requirements:
- 120 to 180 words
- simple and engaging
- 1 paragraph only
- no headings
- no bullet points
- plain text only
"""
            }
        ],
        "temperature": 0.7
    }

    response = requests.post(
        OPENROUTER_URL,
        headers=headers,
        json=payload,
        timeout=60
    )

    try:
        data = response.json()
    except Exception:
        data = {"raw": response.text}

    if response.status_code != 200:
        error_message = data.get("error", {}).get("message") if isinstance(data, dict) else None
        raise Exception(error_message or data)

    return data["choices"][0]["message"]["content"].strip()


@api_view(["POST"])
@permission_classes([AllowAny])
def generate_description(request):
    title = request.data.get("title", "").strip()

    if not title:
        return Response(
            {"error": "Title is required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    if not OPENROUTER_API_KEY:
        return Response(
            {"error": "OPENROUTER_API_KEY is not set in environment"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    try:
        description = generate_description_from_title(title)
        return Response(
            {"description": description},
            status=status.HTTP_200_OK
        )

    except Exception as e:
        return Response(
            {"error": str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
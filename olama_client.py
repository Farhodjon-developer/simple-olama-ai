import os, time
import httpx

OLAMA_API_KEY = os.getenv("OLAMA_API_KEY")

BASE_URL = "https://api.olama.ai/v1/chat/completions"  # Olama docs bo'yicha tekshiring

def call_olama(prompt, model="olami:latest", max_retries=3, timeout=20):
    if not OLAMA_API_KEY:
        return None, "OLAMA_API_KEY not set on server."

    headers = {
        "Authorization": f"Bearer {OLAMA_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }

    for attempt in range(1, max_retries+1):
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(BASE_URL, headers=headers, json=payload)
                resp.raise_for_status()
                data = resp.json()
                # Olama javobi strukturasiga qarab o'zgartiring:
                # ko'pincha: data['choices'][0]['message']['content']
                choice = data.get("choices", [{}])[0]
                text = choice.get("message", {}).get("content") or choice.get("text") or ""
                return text, None
        except Exception as e:
            if attempt == max_retries:
                return None, str(e)
            time.sleep(1 * attempt)
    return None, "Unknown error"
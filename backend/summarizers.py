import os
import re
import json
import urllib.request
import urllib.error
import google.generativeai as genai
from openai import OpenAI

VALID_PROVIDERS = {"groq", "gemini", "gpt", "grok"}
VALID_LENGTHS = {"short", "medium", "long"}

LENGTH_GUIDANCE = {
    "short": "2-3 sentences, plus 3 key bullet points.",
    "medium": "1 short paragraph (4-6 sentences), plus 4-5 key bullet points.",
    "long": "2-3 paragraphs, plus 5-7 key bullet points covering all major sections.",
}


class SummarizationError(Exception):
    pass


def _clean_summary(raw: str) -> str:
    """Strips <think> tags, reasoning thoughts, and unwanted artifacts."""
    if not raw:
        return ""
    # Strip <think>...</think> blocks from reasoning models
    cleaned = re.sub(r"<think>[\s\S]*?</think>", "", raw, flags=re.IGNORECASE).strip()
    # Strip any dangling think tags
    cleaned = re.sub(r"</?think>", "", cleaned, flags=re.IGNORECASE).strip()
    return cleaned


def summarize(text: str, length: str, provider: str = "groq") -> str:
    if provider not in VALID_PROVIDERS:
        raise SummarizationError(f"Unsupported provider: {provider}")
    if length not in VALID_LENGTHS:
        raise SummarizationError(f"Unsupported length: {length}")

    prompt = _build_prompt(text, length)

    try:
        if provider == "groq":
            res = _summarize_groq(prompt)
        elif provider == "gemini":
            res = _summarize_gemini(prompt)
        elif provider == "gpt":
            res = _summarize_gpt(prompt)
        elif provider == "grok":
            res = _summarize_grok(prompt)
        return _clean_summary(res)
    except SummarizationError:
        raise
    except Exception as e:
        raise SummarizationError(f"{provider} request failed: {e}")


def _build_prompt(text: str, length: str) -> str:
    guidance = LENGTH_GUIDANCE[length]
    # Cap input to keep requests fast and within free-tier context limits
    truncated = text[:15000]
    return (
        "You are an expert document summarizer. Summarize the following document directly.\n"
        "IMPORTANT: Provide ONLY the final summary. Do NOT include any internal reasoning, thoughts, or <think> tags.\n\n"
        f"Length requirement: {guidance}\n\n"
        "Strictly use this format:\n"
        "Summary: <your clean summary text>\n"
        "Key Points:\n"
        "- <bullet point 1>\n"
        "- <bullet point 2>\n"
        "- <bullet point 3>\n\n"
        f"Document:\n{truncated}"
    )


def _get_groq_models(api_key: str) -> list:
    """Dynamically fetches active chat models from Groq or returns known latest models."""
    defaults = [
        "openai/gpt-oss-20b",
        "openai/gpt-oss-120b",
        "qwen/qwen3.6-27b",
        "gemma2-9b-it",
        "llama-3.1-8b-instant",
        "llama-3.3-70b-versatile",
    ]
    try:
        req = urllib.request.Request(
            "https://api.groq.com/openai/v1/models",
            headers={
                "Authorization": f"Bearer {api_key}",
                "User-Agent": "DocSummaryAssistant/1.0",
            },
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            # Filter out non-chat models (like audio/whisper or guard models)
            active = [
                m["id"] for m in data.get("data", [])
                if "id" in m and not any(x in m["id"] for x in ["whisper", "guard", "embed", "tts"])
            ]
            if active:
                return active
    except Exception:
        pass
    return defaults


def _summarize_groq(prompt: str) -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise SummarizationError("GROQ_API_KEY is not set")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "DocSummaryAssistant/1.0",
    }

    candidate_models = _get_groq_models(api_key)

    last_err = None
    for model in candidate_models:
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
        }
        try:
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                return data["choices"][0]["message"]["content"]
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            last_err = f"Groq API error ({e.code}) with model {model}: {error_body}"
            # Continue to next model on 400 (decommissioned), 404 (not found), or 429 (rate limit)
            continue
        except Exception as e:
            last_err = f"Groq request error with model {model}: {e}"
            continue

    raise SummarizationError(last_err or "All candidate Groq models failed")


def _summarize_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SummarizationError("GEMINI_API_KEY is not set")
    genai.configure(api_key=api_key)

    gemini_candidates = [
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-3.5-flash-lite",
        "gemini-2.5-flash",
        "gemini-1.5-flash",
    ]

    last_err = None
    for m in gemini_candidates:
        try:
            model = genai.GenerativeModel(m)
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text
        except Exception as e:
            last_err = e
            continue

    raise SummarizationError(f"Gemini request failed: {last_err}")


def _summarize_gpt(prompt: str) -> str:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise SummarizationError("OPENAI_API_KEY is not set")
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content


def _summarize_grok(prompt: str) -> str:
    api_key = os.environ.get("XAI_API_KEY")
    if not api_key:
        raise SummarizationError("XAI_API_KEY is not set")
    # xAI's API is OpenAI-compatible: same client, different base_url + key
    client = OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
    response = client.chat.completions.create(
        model="grok-4",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

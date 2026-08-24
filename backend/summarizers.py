"""
Thin adapter over three LLM providers. Adding a provider means adding
one branch here — the rest of the app never knows which model ran.
"""

import os
import google.generativeai as genai
from openai import OpenAI

VALID_PROVIDERS = {"gemini", "gpt", "grok"}
VALID_LENGTHS = {"short", "medium", "long"}

LENGTH_GUIDANCE = {
    "short": "2-3 sentences, plus 3 key bullet points.",
    "medium": "1 short paragraph (4-6 sentences), plus 4-5 key bullet points.",
    "long": "2-3 paragraphs, plus 5-7 key bullet points covering all major sections.",
}


class SummarizationError(Exception):
    pass


def summarize(text: str, length: str, provider: str) -> str:
    if provider not in VALID_PROVIDERS:
        raise SummarizationError(f"Unsupported provider: {provider}")
    if length not in VALID_LENGTHS:
        raise SummarizationError(f"Unsupported length: {length}")

    prompt = _build_prompt(text, length)

    try:
        if provider == "gemini":
            return _summarize_gemini(prompt)
        elif provider == "gpt":
            return _summarize_gpt(prompt)
        elif provider == "grok":
            return _summarize_grok(prompt)
    except SummarizationError:
        raise
    except Exception as e:
        raise SummarizationError(f"{provider} request failed: {e}")


def _build_prompt(text: str, length: str) -> str:
    guidance = LENGTH_GUIDANCE[length]
    # Cap input to keep requests fast and within free-tier context limits
    truncated = text[:15000]
    return (
        "Summarize the following document.\n"
        f"Length: {guidance}\n"
        "Format your response as:\n"
        "Summary: <the summary>\n"
        "Key Points:\n- <point>\n- <point>\n\n"
        f"Document:\n{truncated}"
    )


def _summarize_gemini(prompt: str) -> str:
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise SummarizationError("GEMINI_API_KEY is not set")
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-3.6-flash")
    response = model.generate_content(prompt)
    return response.text


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

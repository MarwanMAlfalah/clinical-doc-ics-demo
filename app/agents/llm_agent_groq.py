from groq import Groq
from groq import BadRequestError

FALLBACK_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
]

class GroqLLMAgent:
    """
    LLM Agent using Groq API (LLaMA).
    Input: transcript text
    Output: SOAP note in English
    """
    def __init__(self, api_key: str, model: str):
        self.client = Groq(api_key=api_key)
        self.model = model

    def _call(self, model: str, messages, temperature=0.2, max_tokens=700):
        return self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def generate_soap(self, transcript: str):
        system_prompt = (
            "You are a clinical documentation assistant. "
            "Write a clean SOAP note in English. "
            "Do not add any information that is not in the transcript. "
            "If something is missing, write 'Not mentioned'."
        )

        user_prompt = f"""TRANSCRIPT:
{transcript}

TASK:
Create a SOAP note with the following sections:
S: Subjective
O: Objective
A: Assessment
P: Plan

Return only the SOAP note text.
"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        models_to_try = [self.model] + [m for m in FALLBACK_MODELS if m != self.model]

        last_err = None
        for m in models_to_try:
            try:
                resp = self._call(m, messages)
                return resp.choices[0].message.content.strip()
            except BadRequestError as e:
                last_err = e
                # try next model

        raise last_err

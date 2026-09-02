import json
import os
from groq import Groq

_client = None


def _get_client():
    global _client
    if _client is None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY is not set")
        _client = Groq(api_key=api_key)
    return _client


SYSTEM_PROMPT = """You are a strict, evidence-based resume screener for a hiring team.
You compare one job description against one candidate resume and produce a
structured assessment that a human recruiter will read directly.

Rules:
- Base every claim on specific text actually present in the JD and the resume.
  Do not invent experience, skills, or qualifications that are not evidenced.
- fit_summary must be 2-4 sentences, specific to this candidate and this JD
  (mention concrete overlaps or mismatches — not generic praise).
- match_score is an integer 0-100 reflecting overall fit against the JD's
  stated responsibilities, skills, and experience/attribute requirements.
- gaps must be a list of 2-5 short, concrete follow-up questions or missing
  requirements a recruiter should probe in an interview. If the resume is a
  near-perfect match, still list clarifying questions worth asking.
- Output ONLY valid JSON, no markdown fencing, no commentary, matching exactly:
  {"match_score": <integer 0-100>, "fit_summary": "<string>", "gaps": ["<string>", ...]}
"""


class LLMScoringError(Exception):
    pass


def score_resume(jd_text: str, resume_text: str) -> dict:
    client = _get_client()
    user_prompt = (
        f"JOB DESCRIPTION:\n{jd_text}\n\n"
        f"CANDIDATE RESUME:\n{resume_text}\n\n"
        "Produce the JSON assessment now."
    )

    completion = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
        response_format={"type": "json_object"},
    )

    raw = completion.choices[0].message.content

    try:
        data = json.loads(raw)
    except (json.JSONDecodeError, TypeError) as e:
        raise LLMScoringError(f"Groq returned malformed JSON: {raw!r}") from e

    if (
        "match_score" not in data
        or "fit_summary" not in data
        or "gaps" not in data
        or not isinstance(data["gaps"], list)
    ):
        raise LLMScoringError(f"Groq JSON missing required fields: {data!r}")

    try:
        score = int(data["match_score"])
    except (TypeError, ValueError) as e:
        raise LLMScoringError(f"match_score not an integer: {data['match_score']!r}") from e

    score = max(0, min(100, score))

    return {
        "match_score": score,
        "fit_summary": str(data["fit_summary"]),
        "gaps": [str(g) for g in data["gaps"]],
    }

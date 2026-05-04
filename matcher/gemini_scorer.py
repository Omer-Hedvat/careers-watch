import json


def build_prompt(job: dict, profile_md: str, cv_md: str) -> str:
    job_block = "\n".join(
        f"{k}: {v}" for k, v in {
            "Company": job.get("company", ""),
            "Title": job.get("title", ""),
            "Location": job.get("location", ""),
            "Source VC": job.get("source_vc", ""),
            "VC Tier": job.get("vc_tier", ""),
            "Apply URL": job.get("apply_url", ""),
            "Description": job.get("description", ""),
        }.items()
    )

    return f"""You are a job-fit scorer for a specific candidate. Your job is to read the candidate profile (what they want), their CV (what they have done), and a job posting, then score the fit 0–10 per the rubric defined in the profile.

Return ONLY a JSON object with this exact schema:
{{
  "score": <integer 0-10>,
  "reasoning": "<one concise sentence explaining the score>",
  "flags": ["<short-flag>", ...]
}}

Flag examples: "location-unclear", "lead-path-implied", "management-gap", "wrong-domain", "dealbreaker-location", "title-laundering", "llm-not-security"

Do not add any text outside the JSON.

<profile>
{profile_md}
</profile>

<cv>
{cv_md}
</cv>

<job>
{job_block}
</job>"""


def score_job(job: dict, profile_md: str, cv_md: str, client) -> dict:
    prompt = build_prompt(job, profile_md, cv_md)
    try:
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
            },
        )
        raw = resp.text.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        data = json.loads(raw)
        return {
            "score": int(data.get("score", 0)),
            "reasoning": str(data.get("reasoning", "")),
            "flags": list(data.get("flags", [])),
        }
    except Exception as e:
        return {"score": 0, "reasoning": f"scorer error: {e}", "flags": ["scorer-error"]}

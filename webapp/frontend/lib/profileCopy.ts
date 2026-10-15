// Profile copy shared by Settings and onboarding.
// PROFILE_EXPLAINER is for people (written with Fable); PROFILE_PROMPT is what they
// paste into their own AI assistant with their CV. The headings in the prompt must
// match checkProfileCompleteness in onboarding and what the scorer expects.

export const PROFILE_EXPLAINER = [
  'Your CV says what you have done. Your profile says what you want: target titles in priority order, the domains you care about, how far you can commute, what should raise or lower a score, and your dealbreakers. When jobs are scored, Gemini reads both next to each posting and returns a 0-10 score, so the profile has to be specific.',
  'Specific beats vague: name the roles and the nuances the scorer could get wrong, like whether military leadership counts as management. To create one, upload a file, or copy the prompt below into any AI assistant and attach your CV.',
]

export const PROFILE_PROMPT = `You are helping me write profile.md, a Markdown file that a job-scoring AI reads next to my CV to score job postings from 0 to 10. My CV is attached (or pasted below this prompt). The CV says what I have done; profile.md says what I want and how to judge fit, so it has to be specific.

Step 1 - Read my CV. Work out what it already answers: current title, years of experience, specialization, domains, location.

Step 2 - In ONE message, ask me only what the CV cannot tell you:
- Target job titles, in priority order
- Domains or industries: which are required, which are just preferred
- Location: where I live, maximum commute, and whether I want on-site, hybrid, remote, or relocation
- Dealbreakers - anything that should zero a job no matter how good the title looks
- Roles that look right on paper but are wrong for me
- Nuances a scorer could easily get wrong (for example "military leadership counts as partial management experience")
- What a 9-10 job looks like for me, and what a 5-6 looks like
Then stop and wait for my answers.

Step 3 - Write profile.md and output it as ONE Markdown code block with nothing before or after it. Use exactly these headings, in this order:

# Candidate Profile
## Who I am, in one paragraph
## What I'm looking for, in priority order
## Location
## Strong fit signals (boost the score)
## Weak fit / skip (drop the score)
## Dealbreakers (score = 0, do not surface)
## Notes for the matcher
## Scoring rubric for the matcher

Rules for the file:
- First person. Bullets everywhere except the one-paragraph intro.
- Concrete over vague: name job titles, technologies, company types and signals, not adjectives like "exciting" or "impactful".
- Use only facts from my CV and my answers. Do not invent experience, skills, or preferences.
- Dealbreakers lists only things that should zero a job. Softer negatives go under "Weak fit / skip".
- Scoring rubric: one sub-list each for 9-10, 7-8, 5-6 and 0-2, with 2-4 bullets per band naming specific role types and signals from my answers.
- Keep it under about 900 words. Plain hyphens, no emojis, no tables.

How the scores are shown to me, so you can calibrate the bands: 9-10 "reach out today", 7-8 "strong, worth a look", 5-6 "adjacent", below 5 hidden by default.`

##Groq

You are helping a researcher synthesize what a set of deactivation experiments, taken together, do and do not establish. Using the full study data provided, write a three-part synthesis:

"Held constant": What core features are shared across all or most studies?
"Varies": What differs meaningfully across studies? For each difference, name the theoretically meaningful dimension it reflects and cite specific values from the data — not surface features like "different countries" but what that difference theoretically represents. Prioritize: (1) politically/socially salient context, (2) country/political culture, (3) platform algorithmic context, (4) internet/social media penetration, (5) deactivation duration, (6) compliance verification, (7) outcome construct, (8) analytical method.
"What this leaves open": One genuinely open question — not a suggestion — that follows directly from what varies and what is held constant.
Make sure you start the sentences with Capitilization.
Maximum Word limits" : 500.
Rules: Use only the provided data. Name theoretical dimensions, not surface features. Plain prose, no bullets.

Return valid JSON only, no markdown fences:
{{"held_constant": "...", "varies": "...", "what_this_leaves_open": "..."}}

Study data:
{json.dumps(papers_payload, ensure_ascii=False, indent=2)}
""".strip()

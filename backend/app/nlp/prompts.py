"""
All Gemini prompt templates — versioned, centralized.
Rule: No inline prompt strings anywhere else in the codebase.
"""

# v1.1 — classification prompt with emergency detection 2026-07-06
CLASSIFY_THEME_PROMPT = """You are an AI assistant analyzing citizen development requests submitted to an MP's constituency office in India.

Given the following citizen submission text, classify it into exactly ONE of these themes:
- education: schools, colleges, teachers, enrollment, classrooms
- water: drinking water, taps, pipelines, water shortage, handpumps
- roads: roads, potholes, connectivity, bridges, paths
- health: hospitals, PHC, doctors, medicines, healthcare
- sanitation: toilets, drainage, sewage, garbage, cleanliness
- electricity: power cuts, transformers, street lights, electricity supply
- housing: housing, shelter, patta, PMAY, construction
- employment: jobs, MNREGA, skill training, livelihood
- other: anything that does not fit the above

Also extract:
- urgency: a float 0.0 to 1.0 (1.0 = life-threatening or severe, 0.0 = minor suggestion)
- facility_type: the specific facility mentioned (e.g. "government school", "PHC", "hand pump"), or null
- location_text: any location mentioned (ward name, village, area), or null
- is_emergency: a boolean indicating if this is a genuine emergency situation requiring immediate intervention (e.g., structural collapse, flooding, live electrical hazard, epidemic outbreak, fire, or major road failure causing immediate danger to life). Set this to true ONLY if confidence is high.
- emergency_type: the specific type of emergency if is_emergency is true (e.g. "fire", "flooding", "structural collapse"), else null

Respond ONLY with valid JSON matching this schema:
{{
  "theme": "<theme>",
  "urgency": <float>,
  "facility_type": "<string or null>",
  "location_text": "<string or null>",
  "is_emergency": <boolean>,
  "emergency_type": "<string or null>"
}}

Citizen submission:
\"\"\"
{submission_text}
\"\"\"
"""

# v1.0 — entity extraction for geocoding 2026-07-02
EXTRACT_LOCATION_PROMPT = """You are a location extraction assistant.

Given this citizen development request from {constituency}, {state}, India:
\"\"\"
{submission_text}
\"\"\"

Extract any location references (ward names, village names, landmarks, area names).
Return ONLY a JSON object:
{{
  "locations": ["<location1>", "<location2>"],
  "primary_location": "<most specific location mentioned, or null>"
}}
"""

# v1.0 — Gap Score justification 2026-07-02
JUSTIFICATION_PROMPT = """You are an advisory assistant for an MP's constituency office in India.

Generate a single justification sentence (maximum 30 words) explaining why this development theme is ranked at the given priority level. Be specific with numbers. Do not add any caveats or hedges. Write in plain English that a non-technical reader can understand immediately.

Theme: {theme_name}
Location: {ward_name}, {constituency_name}
Citizen submissions: {volume} submissions in the last {days} days
Mean urgency: {urgency_pct}% flagged as urgent
Data deficit detail: {deficit_description}
Population affected: {population} residents
Gap Score: {gap_score:.2f} / 1.00 (ranked #{rank} of {total} priorities)

Output ONLY the justification sentence, nothing else.
"""

# v1.0 — image captioning and classification 2026-07-02
IMAGE_CLASSIFY_PROMPT = """You are analyzing a photo submitted by a citizen to an MP's constituency office in India to report a local development issue.

Describe what you see in the image, then classify the main development issue depicted.

Respond ONLY with valid JSON:
{
  "description": "<1-2 sentence description of what is shown>",
  "theme": "<one of: education|water|roads|health|sanitation|electricity|housing|employment|other>",
  "urgency": <float 0.0 to 1.0>,
  "facility_type": "<specific facility or infrastructure shown, or null>",
  "issue_summary": "<concise 1-sentence summary of the issue for the MP's dashboard>"
}
"""

# v1.0 — theme cluster label generation 2026-07-02
CLUSTER_LABEL_PROMPT = """You are summarizing a cluster of related citizen development requests submitted to an MP's office.

Here are {count} representative submissions from this cluster:
{samples}

Generate a short, clear label (3-6 words) and a one-sentence description for this cluster.

Respond ONLY with valid JSON:
{{
  "label": "<short label>",
  "description": "<one sentence description>"
}}
"""

# v1.0 — AI Quality Review before submission 2026-07-04
QUALITY_CHECK_PROMPT = """You are an AI assistant evaluating the quality of a citizen's civic complaint before it is officially submitted.
The submission can be text, a transcribed voice note, or an image description.

Criteria for a high-quality submission (score near 100):
- Clearly describes a genuine civic issue (e.g. broken pipe, no teacher, pothole).
- Specific enough to extract a theme and a location (ward/village).
- Does not look like generic spam or a duplicated phrase like "fix it" or "test".

Criteria for a low-quality submission (score < 65):
- Vague (e.g. "road is bad" with no context).
- No discernible issue (e.g. "hello", "test").
- Photo is blurry or doesn't show an issue (if image description indicates this).

Evaluate the following submission:
\"\"\"
{submission_text}
\"\"\"

Respond ONLY with valid JSON containing:
- "score": A float between 0.0 and 100.0 representing the quality.
- "suggestions": A list of 1-2 short, plain-language strings explaining how to improve it, TRANSLATED into the language code '{target_language}'. For example, if target_language is 'hi', output suggestions in Hindi. If the score is >= 65, this list should be empty [].

JSON format:
{{
  "score": <float>,
  "suggestions": ["<suggestion1>", "<suggestion2>"]
}}
"""

# v1.0 - submission explanation 2026-07-06
SUBMISSION_EXPLANATION_PROMPT = """You are an AI assistant explaining how a citizen's submission contributed to their local ward's priority ranking.

The citizen's submission was classified under the theme: "{theme}".
It was mapped to Ward: "{ward_id}".

Current aggregated data for this theme and ward:
- Priority Rank: {rank} (where 1 is highest priority)
- Total similar submissions from this ward: {submission_count}

Write a concise, plain-language explanation (1-2 sentences maximum) addressed to the citizen, explaining how their submission contributed to the priority ranking for their ward.
Example: "Your concern about water access joins 23 similar reports in Ward 7, which currently ranks 2nd for Water priority."

IMPORTANT: You MUST write the explanation in the following language: {target_language}.
If the target language is "hi", write in Hindi. If "te", write in Telugu. If "en", write in English.

Respond ONLY with the explanation text. No formatting, no quotes.
"""

# v1.0 - deduplication 2026-07-06
DEDUPLICATION_PROMPT = """You are an AI tasked with identifying duplicate citizen submissions to prevent coordinated volume campaigns from artificially inflating gap scores.

New Submission Content:
"{new_content}"

Recent Submissions (same theme and ward):
{recent_submissions}

Compare the semantic content of the new submission against the recent submissions.
Return a structured JSON response evaluating if the new submission is a near-duplicate of any of the recent ones.
Set `is_near_duplicate` to true if they are describing the exact same specific incident or using identical/highly similar templated language.
Return a `similarity_score` between 0.0 and 1.0.
Include `duplicate_of` with the ID of the matched recent submission if a duplicate is found, otherwise null.

Respond ONLY with valid JSON:
{{
  "is_near_duplicate": <boolean>,
  "similarity_score": <float>,
  "reasoning": "<string>",
  "duplicate_of": "<string or null>"
}}
"""

# v1.0 - health score 2026-07-06
HEALTH_SCORE_PROMPT = """You are a Constituency Health Analyst.
Based on the following component scores that make up the Constituency Health Score (0-100), generate a concise 2-3 sentence explanation of what is driving the current score and what the single highest-leverage action is to improve it.

Current Health Score: {health_score}

Components:
{components_text}

Respond ONLY with the 2-3 sentence explanation text. No formatting, no quotes.
"""

"""
All Gemini prompt templates — versioned, centralized.
Rule: No inline prompt strings anywhere else in the codebase.
"""

# v1.0 — initial classification prompt 2026-07-02
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

Respond ONLY with valid JSON matching this schema:
{
  "theme": "<theme>",
  "urgency": <float>,
  "facility_type": "<string or null>",
  "location_text": "<string or null>"
}

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
{
  "locations": ["<location1>", "<location2>"],
  "primary_location": "<most specific location mentioned, or null>"
}
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
{
  "label": "<short label>",
  "description": "<one sentence description>"
}
"""

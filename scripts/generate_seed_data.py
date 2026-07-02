import json
import random
import uuid
from datetime import datetime, timedelta

# Hyderabad Wards & Geo-boundaries
WARDS = [
    {"id": "rajapuram", "name": "Rajapuram", "lat_center": 17.3850, "lng_center": 78.4867},
    {"id": "old_city", "name": "Old City", "lat_center": 17.3616, "lng_center": 78.4747},
    {"id": "new_market", "name": "New Market", "lat_center": 17.4399, "lng_center": 78.4983},
    {"id": "green_valley", "name": "Green Valley", "lat_center": 17.4435, "lng_center": 78.3772},
    {"id": "riverside", "name": "Riverside", "lat_center": 17.3984, "lng_center": 78.5033},
]

# Themes and realistic content
THEMES = {
    "education": [
        {"en": "School roof is leaking badly.", "hi": "स्कूल की छत बहुत टपक रही है।", "te": "పాఠశాల పైకప్పు బాగా లీక్ అవుతోంది."},
        {"en": "Not enough teachers in primary school.", "hi": "प्राथमिक विद्यालय में पर्याप्त शिक्षक नहीं हैं।", "te": "ప్రాథమిక పాఠశాలలో తగినంత మంది ఉపాధ్యాయులు లేరు."},
        {"en": "Children sitting on floor, no benches.", "hi": "बच्चे फर्श पर बैठ रहे हैं, बेंच नहीं हैं।", "te": "పిల్లలు నేలపై కూర్చుంటున్నారు, బెంచీలు లేవు."},
        {"en": "Toilets in girls school are non-functional.", "hi": "लड़कियों के स्कूल में शौचालय काम नहीं कर रहे हैं।", "te": "బాలికల పాఠశాలలో మరుగుదొడ్లు పనిచేయడం లేదు."}
    ],
    "water": [
        {"en": "No drinking water supply for 3 days.", "hi": "3 दिनों से पीने के पानी की आपूर्ति नहीं है।", "te": "3 రోజుల నుంచి తాగునీటి సరఫరా లేదు."},
        {"en": "Borewell motor is burnt.", "hi": "बोरवेल की मोटर जल गई है।", "te": "బోరుబావి మోటారు కాలిపోయింది."},
        {"en": "Water pressure is too low to fill tanks.", "hi": "टैंक भरने के लिए पानी का दबाव बहुत कम है।", "te": "ట్యాంకులు నింపేందుకు నీటి ప్రెషర్ చాలా తక్కువగా ఉంది."},
        {"en": "Tap water is contaminated and smells.", "hi": "नल का पानी दूषित है और बदबू आ रही है।", "te": "కుళాయి నీరు కలుషితమై వాసన వస్తోంది."}
    ],
    "roads": [
        {"en": "Huge potholes on main road causing accidents.", "hi": "मुख्य सड़क पर बड़े गड्ढों के कारण हादसे हो रहे हैं।", "te": "ప్రధాన రహదారిపై భారీ గుంతల వల్ల ప్రమాదాలు జరుగుతున్నాయి."},
        {"en": "Street is unpaved and muddy.", "hi": "सड़क कच्ची और कीचड़युक्त है।", "te": "వీధిలో కచ్చా రోడ్డు ఉంది, బురదగా ఉంది."},
        {"en": "Road dug up for pipeline but not repaired.", "hi": "पाइपलाइन के लिए सड़क खोदी गई लेकिन मरम्मत नहीं हुई।", "te": "పైప్‌లైన్ కోసం రోడ్డు తవ్వారు కానీ బాగుచేయలేదు."},
    ],
    "health": [
        {"en": "Primary health center has no doctor after 2 PM.", "hi": "प्राथमिक स्वास्थ्य केंद्र में दोपहर 2 बजे के बाद कोई डॉक्टर नहीं है।", "te": "ప్రాథమిక ఆరోగ్య కేంద్రంలో మధ్యాహ్నం 2 గంటల తర్వాత డాక్టర్ లేరు."},
        {"en": "No medicines available for fever at clinic.", "hi": "क्लिनिक में बुखार के लिए कोई दवा उपलब्ध नहीं है।", "te": "క్లినిక్‌లో జ్వరానికి మందులు లేవు."},
        {"en": "Ambulance cannot reach our street.", "hi": "एम्बुलेंस हमारी गली तक नहीं पहुँच सकती।", "te": "అంబులెన్స్ మా వీధికి రాలేదు."},
    ],
    "sanitation": [
        {"en": "Garbage dump overflowing for a week.", "hi": "एक हफ्ते से कचरे का ढेर ओवरफ्लो हो रहा है।", "te": "వారం రోజులుగా చెత్త కుప్ప పేరుకుపోతోంది."},
        {"en": "Drainage pipe broken and sewage on street.", "hi": "जल निकासी पाइप टूट गया है और सड़क पर सीवेज है।", "te": "డ్రైనేజీ పైపు పగిలి వీధిలో మురుగునీరు పారుతోంది."},
        {"en": "Public toilet is extremely dirty.", "hi": "सार्वजनिक शौचालय बहुत गंदा है।", "te": "పబ్లిక్ టాయిలెట్ చాలా అపరిశుభ్రంగా ఉంది."},
    ]
}

def random_date(start_days_ago=30):
    start = datetime.now() - timedelta(days=start_days_ago)
    random_days = random.random() * start_days_ago
    return (start + timedelta(days=random_days)).isoformat()

def generate_submissions(count=200):
    submissions = []
    
    for _ in range(count):
        theme_id = random.choice(list(THEMES.keys()))
        ward = random.choice(WARDS)
        content_obj = random.choice(THEMES[theme_id])
        
        # Determine language (40% Hindi, 40% Telugu, 20% English)
        lang_choice = random.choices(["hi", "te", "en"], weights=[0.4, 0.4, 0.2])[0]
        original_lang = "hi-IN" if lang_choice == "hi" else "te-IN" if lang_choice == "te" else "en-IN"
        
        # Determine media type (50% text, 30% voice, 20% image)
        media_choice = random.choices(["text", "audio", "image"], weights=[0.5, 0.3, 0.2])[0]
        
        # Urgency is skewed slightly higher for demo impact
        urgency = min(1.0, max(0.1, random.gauss(0.65, 0.2)))
        
        lat = ward["lat_center"] + random.uniform(-0.015, 0.015)
        lng = ward["lng_center"] + random.uniform(-0.015, 0.015)
        
        sub = {
            "id": f"sub_{uuid.uuid4().hex[:8]}",
            "created_at": random_date(),
            "media_type": media_choice,
            "original_content": content_obj[lang_choice] if media_choice == "text" else f"[GCS URI to {media_choice}]",
            "original_language": original_lang,
            "translated_text": content_obj["en"],
            "theme": theme_id,
            "urgency": urgency,
            "ward_id": ward["id"],
            "lat": lat,
            "lng": lng
        }
        submissions.append(sub)
        
    # Sort by date descending
    submissions.sort(key=lambda x: x["created_at"], reverse=True)
    return submissions

if __name__ == "__main__":
    import os
    out_dir = "data/seed-submissions"
    os.makedirs(out_dir, exist_ok=True)
    
    data = generate_submissions(200)
    out_file = os.path.join(out_dir, "mock_submissions.json")
    
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"Generated {len(data)} realistic mock submissions at {out_file}")

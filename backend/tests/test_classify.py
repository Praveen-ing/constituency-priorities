from unittest.mock import patch, MagicMock

from app.nlp.classify import classify_submission, ClassificationResult

def test_classify_english_water():
    mock_response = MagicMock()
    mock_response.text = '{"theme": "water", "urgency": 0.8, "facility_type": "pipe", "location_text": "Main Street"}'
    
    with patch("app.nlp.classify._get_model") as mock_get_model:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model
        
        result = classify_submission("We have no water in the pipe on Main Street.")
        
        assert result.theme == "water"
        assert result.urgency == 0.8
        assert result.facility_type == "pipe"
        assert result.location_text == "Main Street"
        assert result.is_emergency is False

def test_classify_emergency():
    mock_response = MagicMock()
    mock_response.text = '{"theme": "other", "urgency": 1.0, "facility_type": "building", "location_text": "Market", "is_emergency": true, "emergency_type": "fire"}'
    
    with patch("app.nlp.classify._get_model") as mock_get_model:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model
        
        result = classify_submission("Massive fire at the market building!")
        
        assert result.theme == "other"
        assert result.urgency == 1.0
        assert result.is_emergency is True
        assert result.emergency_type == "fire"

def test_classify_hindi_health():
    """Test classification of Hindi text for health issues."""
    mock_response = MagicMock()
    mock_response.text = '{"theme": "health", "urgency": 0.9, "facility_type": "hospital", "location_text": "MG Road"}'
    
    with patch("app.nlp.classify._get_model") as mock_get_model:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model
        
        # "There are no doctors in the hospital on MG Road"
        result = classify_submission("एमजी रोड के अस्पताल में कोई डॉक्टर नहीं हैं।")
        
        assert result.theme == "health"
        assert result.urgency == 0.9
        assert result.facility_type == "hospital"
        assert result.location_text == "MG Road"

def test_classify_telugu_roads():
    """Test classification of Telugu text for road infrastructure issues."""
    mock_response = MagicMock()
    mock_response.text = '{"theme": "roads", "urgency": 0.7, "facility_type": "road", "location_text": "Banjara Hills"}'
    
    with patch("app.nlp.classify._get_model") as mock_get_model:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model
        
        # "Roads are broken in Banjara Hills"
        result = classify_submission("బంజారా హిల్స్‌లో రోడ్లు దెబ్బతిన్నాయి.")
        
        assert result.theme == "roads"
        assert result.urgency == 0.7
        assert result.facility_type == "road"
        assert result.location_text == "Banjara Hills"

def test_classify_hindi_electricity():
    """Test classification of another Hindi text for electricity issues."""
    mock_response = MagicMock()
    mock_response.text = '{"theme": "electricity", "urgency": 0.6, "facility_type": "transformer", "location_text": "Sector 4"}'
    
    with patch("app.nlp.classify._get_model") as mock_get_model:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model
        
        # "Power outage due to transformer blast in Sector 4"
        result = classify_submission("सेक्टर 4 में ट्रांसफॉर्मर ब्लास्ट के कारण बिजली गुल")
        
        assert result.theme == "electricity"
        assert result.urgency == 0.6
        assert result.facility_type == "transformer"
        assert result.location_text == "Sector 4"

def test_classify_invalid_theme_fallback():
    """Test fallback when model outputs an invalid theme."""
    mock_response = MagicMock()
    mock_response.text = '{"theme": "aliens", "urgency": 0.9, "facility_type": "ufo", "location_text": "Area 51"}'
    
    with patch("app.nlp.classify._get_model") as mock_get_model:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model
        
        result = classify_submission("There are aliens here!")
        
        assert result.theme == "other"
        assert result.urgency == 0.9

def test_classify_json_decode_error():
    """Test fallback when model outputs malformed JSON."""
    mock_response = MagicMock()
    mock_response.text = 'This is not json'
    
    with patch("app.nlp.classify._get_model") as mock_get_model:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model
        
        result = classify_submission("Help!")
        
        assert result.theme == "other"
        assert result.urgency == 0.3
        assert result.facility_type is None
        assert result.location_text is None

from app.nlp.classify import check_submission_quality

def test_check_submission_quality():
    """Test AI Quality Review check."""
    mock_response = MagicMock()
    mock_response.text = '{"score": 45.0, "suggestions": ["Be more specific"]}'
    
    with patch("app.nlp.classify._get_model") as mock_get_model:
        mock_model = MagicMock()
        mock_model.generate_content.return_value = mock_response
        mock_get_model.return_value = mock_model
        
        result = check_submission_quality("bad road")
        
        assert result["score"] == 45.0
        assert len(result["suggestions"]) == 1
        assert result["suggestions"][0] == "Be more specific"

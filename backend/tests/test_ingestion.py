from unittest.mock import patch, MagicMock
from app.ingestion.text_pipeline import process_text
from app.ingestion.image_pipeline import process_image

def test_process_text():
    # Test whitespace stripping
    assert process_text("  hello   world  ") == "hello world"
    
    # Test URL removal
    assert process_text("Please fix the road here https://maps.google.com/?q=123") == "Please fix the road here"
    assert process_text("See http://example.com for details") == "See for details"
    
    # Test empty text
    assert process_text("") == ""
    assert process_text(None) == ""

@patch("app.ingestion.image_pipeline.download_from_gcs")
@patch("app.ingestion.image_pipeline.genai.GenerativeModel")
def test_process_image_success(mock_genai_model, mock_download):
    mock_download.return_value = b"fake_image_bytes"
    
    mock_response = MagicMock()
    mock_response.text = '{"description": "A pothole", "theme": "roads", "urgency": 0.8, "facility_type": "road", "issue_summary": "Pothole on main street"}'
    
    mock_instance = MagicMock()
    mock_instance.generate_content.return_value = mock_response
    mock_genai_model.return_value = mock_instance
    
    result = process_image("gs://bucket/test.jpg")
    
    assert result["theme"] == "roads"
    assert result["urgency"] == 0.8
    assert result["description"] == "A pothole"

@patch("app.ingestion.image_pipeline.download_from_gcs")
def test_process_image_failure(mock_download):
    mock_download.side_effect = Exception("Failed to download")
    
    result = process_image("gs://bucket/test.jpg")
    
    assert result["theme"] == "other"
    assert result["urgency"] == 0.3
    assert result["description"] == "Unable to analyze image."

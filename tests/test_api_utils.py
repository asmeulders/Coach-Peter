import pytest
import requests

from api_utils import fetch_data, fetch_recommendation 

# RANDOM_NUMBER = 4


@pytest.fixture
##def mock_random_org(mocker):
def mock_exerciseDB(mocker):
    # Patch the requests.get call
    # requests.get returns an object, which we have replaced with a mock object
    mock_response = mocker.Mock()
    # We are giving that object a text attribute
    mocker.patch("requests.get", return_value=mock_response)
    return mock_response


def test_fetch_data(mock_exerciseDB):
    """Test fetching data from api

    """
    mock_response = mock_exerciseDB
    mock_response.json.return_value = [
    {
        "bodyPart": "chest",
        "equipment": "body weight",
        "gifUrl": "https://example.com/pushup.gif",
        "id": "0001",
        "name": "Push-up",
        "target": "pectorals",
        "secondaryMuscles": ["upper arms", "shoulders"]        
    },
    
    {
        "bodyPart": "chest",
        "equipment": "barbell",
        "gifUrl": "https://example.com/benchpress.gif",
        "id": "0002",
        "name": "Bench Press",
        "target": "pectorals",
        "secondaryMuscles": ["upper arms", "shoulders"] 
        
    }
    ]

    url = "https://exercisedb.p.rapidapi.com/exercises/bodyPart/chest"
    params = {"example": "param"}

    result = fetch_data(url, params=params)

    # Assert that the result is the mocked exercise list
    assert result == [
    {
        "bodyPart": "chest",
        "equipment": "body weight",
        "gifUrl": "https://example.com/pushup.gif",
        "id": "0001",
        "name": "Push-up",
        "target": "pectorals",
        "secondaryMuscles": ["upper arms", "shoulders"]        
    },
    
    {
        "bodyPart": "chest",
        "equipment": "barbell",
        "gifUrl": "https://example.com/benchpress.gif",
        "id": "0002",
        "name": "Bench Press",
        "target": "pectorals",
        "secondaryMuscles": ["upper arms", "shoulders"] 
        
    }
    ]

    # Ensure that the correct URL was called
    requests.get.assert_called_once_with(
        url,
        headers = {
            "X-RapidAPI-Key": EXERCISEDB_API_KEY,
            "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
        },  
        params=params,
        timeout=5
    )

#############################

def test_fetch_data_request_failure(mocker):
    """Test handling of a request failure when calling API.

    """
    # Simulate a request failure
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))

    with pytest.raises(RuntimeError, match="Request to random.org failed: Connection error"):
        fetch_data("https://exercisedb.p.rapidapi.com/exercises/bodyPart/chest")

def test_fetch_data_timeout(mocker):
    """Test handling of a timeout when calling API.

    """
    # Simulate a timeout
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request to ExerciseDB timed out."):
        fetch_data("https://exercisedb.p.rapidapi.com/exercises/bodyPart/chest")

def test_fetch_recommendation_success(mock_exerciseDB):

    """Test handling of an invalid response from random.org.

    """
    mock_response = mock_requests_get
    mock_response.json.return_value = [
    {
        "bodyPart": "chest",
        "equipment": "body weight",
        "gifUrl": "https://example.com/pushup.gif",
        "id": "0001",
        "name": "Push-up",
        "target": "pectorals",
        "secondaryMuscles": ["upper arms", "shoulders"]        
    },
    
    {
        "bodyPart": "chest",
        "equipment": "barbell",
        "gifUrl": "https://example.com/benchpress.gif",
        "id": "0002",
        "name": "Bench Press",
        "target": "pectorals",
        "secondaryMuscles": ["upper arms", "shoulders"] 
        
    }
    ]

    target = "chest"
    exercises = fetch_recommendation(target)

    assert len(exercises) == 2
    assert exercises[0]["name"] == "Push-up"
    requests.get.assert_called_once_with(
        "https://exercisedb.p.rapidapi.com/exercises/bodyPart/chest",
        headers = {
            "X-RapidAPI-Key": EXERCISEDB_API_KEY,
            "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
        },  
        params=params,
        timeout=5
    )

def test_invalid_fetch_recommendation(mock_requests_get):
    mock_response = mock_requests_get
    mock_response.json.return_value = []

    target = "toes"

    with pytest.raises(ValueError, match="Invalid or unsupported body part: toes"):
        fetch_recommendation(body_part)

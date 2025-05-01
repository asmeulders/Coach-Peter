import pytest
import requests
import os

from coach_peter.utils.api_utils import fetch_data, fetch_recommendation
from pytest_mock import MockerFixture


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

    url = "https://exercisedb.p.rapidapi.com/exercises/target/chest"
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
            "X-RapidAPI-Key": os.getenv("EXERCISE_DB_API_KEY"),
            "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
        },  
        params=params,
        timeout=5
    )

#############################



#############################

    

def test_fetch_data_request_failure(mocker):
    """
    Test handling of a request failure when calling API.
    """
    
    # Simulate a request failure
    mocker.patch("requests.get", side_effect=requests.exceptions.RequestException("Connection error"))

    with pytest.raises(RuntimeError, match="Request failed: Connection error"):
    fetch_data("https://exercisedb.p.rapidapi.com/exercises/bodyPart/chest")



def test_fetch_data_timeout(mocker):
    """Test handling of a timeout when calling API.

    """
    # Simulate a timeout
    mocker.patch("requests.get", side_effect=requests.exceptions.Timeout)

    with pytest.raises(RuntimeError, match="Request failed: Connection error"):
    fetch_data("https://exercisedb.p.rapidapi.com/exercises/bodyPart/chest")


def test_fetch_recommendation_success(mock_exerciseDB):


    """Test that a valid body part returns a list of recommended exercises


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


    #Input body part for recommendation
    target = "chest"
    exercises = fetch_recommendation(target)
    
    #validate the result
    assert len(exercises) == 2
    assert exercises[0]["name"] == "Push-up"
    
    requests.get.assert_called_once_with(
        "https://exercisedb.p.rapidapi.com/exercises/target/chest",
        headers = {
            "X-RapidAPI-Key": os.getenv("EXERCISE_DB_API_KEY"),
            "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
        },  
        params=None,
        timeout=5
    )

def test_invalid_fetch_recommendation(mock_exerciseDB):
    """
    Test that an unsupported body part results in a ValueError
    """
    mock_response = mock_exerciseDB
    mock_response.json.return_value = []

    target = "toes"

    with pytest.raises(ValueError, match=f"No exercises found for body part: {target}"):
        fetch_recommendation(target)

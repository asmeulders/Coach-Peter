import logging
import os
import requests

from coach_peter.utils.logger import configure_logger

BASE_URL = os.getenv("EXERCISEDB_BASE_URL", "https://exercisedb.p.rapidapi.com")
EXERCISEDB_API_KEY = os.getenv("EXERCISEDB_API_KEY")

logger = logging.getLogger(__name__)
configure_logger(logger)

def fetch_data(url, params=None):
    headers = {
        "X-RapidAPI-Key": EXERCISEDB_API_KEY,
        "X-RapidAPI-Host": "exercisedb.p.rapidapi.com"
    }
    try:
        logger.info(f"Fetching data from {url} with params {params}")
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        logger.error("Request timed out.")
        raise RuntimeError("Request timed out.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        raise RuntimeError(f"Request failed: {e}")

def fetch_recommendation(body_part):
    """
    Fetch exercises from the ExerciseDB API based on the body part that the user wants to exercise.

    Args:
        body_part (str): Target body part (e.g., 'back', 'cardio', 'chest').

    Returns:
        list: List of exercises matching the target body part.
    """
    url = f"{BASE_URL}/exercises/bodyPart/{body_part}"

    exercises = fetch_data(url)

    if not exercises:
        logger.warning(f"No exercises found for body part: {body_part}")
    else:
        logger.info(f"Found {len(exercises)} exercises for body part: {body_part}")

    return exercises

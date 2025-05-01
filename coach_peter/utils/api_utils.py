import logging
import os
import requests
from dotenv import load_dotenv

from coach_peter.utils.logger import configure_logger

load_dotenv()

BASE_URL = os.getenv("EXERCISE_DB_BASE_URL", "https://exercisedb.p.rapidapi.com")
EXERCISE_DB_API_KEY = os.getenv("EXERCISE_DB_API_KEY")

logger = logging.getLogger(__name__)
configure_logger(logger)

def fetch_data(url, params=None):
    logger.info(f"{EXERCISE_DB_API_KEY}")
    headers = {
        "X-RapidAPI-Key": EXERCISE_DB_API_KEY,
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

def fetch_recommendation(target):
    """
    Fetch exercises from the ExerciseDB API based on the target that the user wants to exercise.

    Args:
        target (str): Target for goal (e.g., 'biceps', 'pectorals', 'cardiovascular system').

    Returns:
        list: List of exercises matching the target value.
    """
    url = f"{BASE_URL}/exercises/bodyPart/{target}"

    exercises = fetch_data(url)

    if not exercises:
        logger.error(f"No exercises found for body part: {target}")
        raise ValueError(f"No exercises found for body part: {target}")
    else:
        logger.info(f"Found {len(exercises)} exercises for body part: {target}")

    return exercises

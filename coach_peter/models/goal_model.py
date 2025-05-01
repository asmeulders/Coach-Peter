import logging
import json 
from sqlalchemy import Text

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from coach_peter.utils.api_utils import fetch_recommendation
from typing import Optional


# Double check if correct db
from coach_peter.db import db
from coach_peter.utils.logger import configure_logger
# from fitness.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)

#TODO####################################################################
class Goals(db.Model):
    """Represents a goal in the plan.

    This model maps to the 'goals' table and stores metadata for desired target areas.

    Used in a Flask-SQLAlchemy application for fitness management,
    user interaction, and data-driven goal operations.
    """

    __tablename__ = "Goals"
    
    # Users can choose which types of goals they want 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    target = db.Column(db.String, nullable=False)
    goal_value = db.Column(db.Integer, nullable=False)
    goal_progress = db.Column(db.Float, nullable=True, default=0)
    completed = db.Column(db.Boolean, nullable=False)
    progress_notes = db.Column(Text, nullable=False, default="[]")
    # play_count = db.Column(db.Integer, nullable=False, default=0)

    def validate(self) -> None:
        """Validates the goal instance before committing to the database.

        Raises:
            ValueError: If any required fields are invalid.
        """
        
        # If a field is provided, check that it's a non-empty string
        # Checks only if field is provided (because it is nullable) and if provided, must be a non-empty string
        # if self.recurring is not None and (not isinstance(self.recurring, str) or not self.recurring.strip()):
        #     raise ValueError("Recurring goal must be a non-empty string if provided.")
        
        #TODO: Double check if this is checking if field is required and change target if so 
        if not self.target or not isinstance(self.target, str):
            raise ValueError("Target must be a non-empty string")
        if not self.goal_value or not isinstance(self.goal_value, int):
            raise ValueError("Goal value must be a valid integer.")
        if not self.goal_progress or (not isinstance(self.goal_progress, float) or not self.goal_progress.strip()):
            raise ValueError("Goal progress must be a valid float.")
        if not self.completed or not isinstance(self.completed, bool):
            raise ValueError("Completed must be either true or false.")
        if self.goal_progress is not None and not isinstance(self.goal_progress, float):
            raise ValueError("Goal progress must be a valid float.")


        #progress
        try:
            notes = json.loads(self.progress_notes)
            if not isinstance(notes, list):
                raise ValueError("Progress notes must be a JSON-formatted list.")
        except (ValueError, TypeError):
            raise ValueError("Progress notes must be a valid JSON-formatted string representing a list.")

        
        # does not allow an empty goal creation
        # if not any([self.nutritional, self.physical, self.recurring, self.one_time, self.upper_body, self.core, self.lower_body]):
        #     raise ValueError("At least one goal field must be provided.")

        # if not self.title or not isinstance(self.title, str):
        #     raise ValueError("Title must be a non-empty string.")
        # if not isinstance(self.year, int) or self.year <= 1900:
        #     raise ValueError("Year must be an integer greater than 1900.")
        # if not self.genre or not isinstance(self.genre, str):
        #     raise ValueError("Genre must be a non-empty string.")
        # if not isinstance(self.duration, int) or self.duration <= 0:
        #     raise ValueError("Duration must be a positive integer.")

    #TODO: Do i need to include nullable fields in this?
    @classmethod
    def create_goal(cls, target: str, goal_value: int, completed: bool, goal_progress: Optional[float] = None) -> None:
        """
        Creates a new goal in the goals table using SQLAlchemy.

        Args:
            target (str): A target muscle group the user wants to work on.
            goal_value (int): A value the user wants to reach for a specific goal.
            completed (bool): If the user has completed the specific goal or not.


        Raises:
            ValueError: If any field is invalid or if a goal with the same compound key already exists. 
            SQLAlchemyError: For any other database-related issues.
        """
        logger.info(f"Received request to create goal.")

        try:
            goal = Goals(
                target=target.strip() if target else None,
                goal_value=goal_value,
                goal_progress=goal_progress,
                completed=completed,
                progress_notes="[]"
            )
            goal.validate()
        except ValueError as e:
            logger.warning(f"Validation failed: {e}")
            raise

        try:
            db.session.add(goal)
            db.session.commit()
            logger.info(f"Goal successfully added with target(s): {target}, goal value: {goal_value}, goal progress: {goal_progress}, and completion status: {completed}.")

        # Duplicate
        # except IntegrityError:
        #     logger.error(f"Song already exists: {artist} - {title} ({year})")
        #     db.session.rollback()
        #     raise ValueError(f"Song with artist '{artist}', title '{title}', and year {year} already exists.")

        except SQLAlchemyError as e:
            logger.error(f"Database error while creating goal: {e}")
            db.session.rollback()
            raise

##############################################
# Delete Goals
##############################################

    @classmethod
    def delete_goal(cls, goal_id: int) -> None:
        """
        Permanently deletes a goal by ID.

        Args:
            goal_id (int): The ID of the goal to delete.

        Raises:
            ValueError: If the goal with the given ID does not exist.
            SQLAlchemyError: For any database-related issues.
        """
        logger.info(f"Received request to delete goal with ID {goal_id}")

        try:
            goal = cls.query.get(goal_id)
            if not goal:
                logger.warning(f"Attempted to delete non-existent goal with ID {goal_id}")
                raise ValueError(f"Goal with ID {goal_id} not found")

            db.session.delete(goal)
            db.session.commit()
            logger.info(f"Successfully deleted goal with ID {goal_id}")

        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting goal with ID {goal_id}: {e}")
            db.session.rollback()
            raise

    @classmethod
    def delete_goal_by_target(cls, target: str) -> None:
        """
        Permanently deletes a goal by target.

        Args:
            target (str): A target muscle group the user wants to work on.

        Raises:
            ValueError: If the goal with the given target does not exist.
            SQLAlchemyError: For any database-related issues.
        """
        logger.info(f"Received request to delete goal with ID {target}")

        try:
            goal = cls.query.filter_by(target=target).first() 
            if not goal:
                logger.warning(f"Attempted to delete non-existent goal with target {target}")
                raise ValueError(f"Goal with target {target} not found")

            db.session.delete(goal)
            db.session.commit()
            logger.info(f"Successfully deleted goal with target {target}")

        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting goal with target {target}: {e}")
            db.session.rollback()
            raise

    @classmethod
    def delete_goal_by_goal_value(cls, goal_value: int) -> None:
        """
        Permanently deletes a goal by the goal value.

        Args:
            goal_value (int): A value the user wants to reach for a specific goal.

        Raises:
            ValueError: If the goal with the given goal value does not exist.
            SQLAlchemyError: For any database-related issues.
        """
        logger.info(f"Received request to delete goal with goal value {goal_value}")

        try:
            goal = cls.query.filter_by(goal_value=goal_value).first()
            if not goal:
                logger.warning(f"Attempted to delete non-existent goal with goal value {goal_value}")
                raise ValueError(f"Goal with goal value {goal_value} not found")

            db.session.delete(goal)
            db.session.commit()
            logger.info(f"Successfully deleted goal with goal value {goal_value}")

        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting goal with goal value {goal_value}: {e}")
            db.session.rollback()
            raise
    
    @classmethod
    def delete_goal_by_completed(cls, completed: bool) -> None:
        """
        Permanently deletes a goal by the completion status.

        Args:
            completed (bool): The completion status of that goal 

        Raises:
            ValueError: If the goal with the given completion status does not exist.
            SQLAlchemyError: For any database-related issues.
        """
        #TODO: Tailor this to true and false 
        logger.info(f"Received request to delete goal with completion status {completed}")

        try:
            goal = cls.query.filter_by(completed=completed).first()
            if not goal:
                logger.warning(f"Attempted to delete non-existent goal with completion {completed}")
                raise ValueError(f"Goal with completion {completed} not found")

            db.session.delete(goal)
            db.session.commit()
            logger.info(f"Successfully deleted goal with completion {completed}")

        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting goal with completion {completed}: {e}")
            db.session.rollback()
            raise
    
###############################################
# Progress Notes 
###############################################
    @classmethod
    def log_workout_session(self, amount: float, exercise_type: str, duration: int, intensity: str, note: str = "") -> str:
        """
        Logs a workout session with progress and updates status.

        Args:
            amount (float): The amount to add to goal progress.
            exercise_type (str): The type of exercise performed (e.g., "Running").
            duration (int): The duration of the workout in minutes.
            intensity (str): The intensity of the workout (e.g., "Low", "Moderate", "High").
            note (str): An optional personal note about the session.

        Raises:
            ValueError: If the amount is not positive.
            SQLAlchemyError: For any database-related issues.

        Returns:
            str: A message indicating progress update or completion.
        """
        if amount <= 0:
            raise ValueError("Progress amount must be positive.")

        if self.goal_progress is None:
            self.goal_progress = 0.0

        self.goal_progress += amount

        workout_note = f"{exercise_type} - {duration} min - {intensity}"
        if note:
            workout_note += f" | Note: {note}"

        self.add_progress_note(workout_note)

        percent = (self.goal_progress / self.goal_value) * 100

        if self.goal_progress >= self.goal_value:
            self.completed = True
            message = f"Goal completed! Total progress: {percent:.1f}%"
        else:
            message = f"Workout logged. Progress: {percent:.1f}% complete."

        db.session.commit()
        return message
    

    # Helper methods
    def get_progress_notes(self) -> list[str]:
        """Returns progress notes as a list of strings."""
        try:
            return json.loads(self.progress_notes or "[]")
        except (TypeError, json.JSONDecodeError):
            return []

    def add_progress_note(self, note: str) -> None:
        """Appends a note to the progress_notes list."""
        notes = self.get_progress_notes()
        notes.append(note)
        self.progress_notes = json.dumps(notes)


###############################################
# Get Goals 
###############################################

    @classmethod
    def get_goal_by_id(cls, goal_id: int) -> "Goals":
        """
        Retrieves a goal by its ID.

        Args:
            goal_id (int): The ID of the goal to retrieve.

        Returns:
            Goals: The goal instance corresponding to the ID.

        Raises:
            ValueError: If no goal with the given ID is found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve goal with ID {goal_id}")

        try:
            goal = cls.query.get(goal_id)

            if not goal:
                logger.info(f"Goal with ID {goal_id} not found")
                raise ValueError(f"Goal with ID {goal_id} not found")

            logger.info(f"Successfully retrieved goal: ID={goal.id}, target={goal.target}, value={goal.goal_value}, progress={goal.goal_progress}, completed={goal.completed}")
            return goal

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving goal by ID {goal_id}: {e}")
            raise

    @classmethod
    def get_goals_by_target(cls, target: str) -> list["Goals"]:
        """
        Retrieves all goals matching a specific target field.

        Args:
            target (str): The target to search for.

        Returns:
            list[Goals]: A list of goal instances matching the target.

        Raises:
            ValueError: If no goals with the given target are found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve all goals with target '{target}'")

        try:
            goals = cls.query.filter_by(target=target).all()

            if not goals:
                logger.info(f"No goals found with target '{target}'")
                raise ValueError(f"No goals found with target '{target}'")

            logger.info(f"Successfully retrieved {len(goals)} goal(s) with target '{target}'")
            return goals

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving goals by target '{target}': {e}")
            raise

    @classmethod
    def get_goals_by_goal_value(cls, goal_value: int) -> list["Goals"]:
        """
        Retrieves all goals matching a specific goal value.

        Args:
            goal_value (int): The goal value to search for.

        Returns:
            list[Goals]: A list of goal instances matching the goal value.

        Raises:
            ValueError: If no goals with the given goal value are found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve all goals with goal value '{goal_value}'")

        try:
            goals = cls.query.filter_by(goal_value=goal_value).all()

            if not goals:
                logger.info(f"No goals found with goal value '{goal_value}'")
                raise ValueError(f"No goals found with goal value '{goal_value}'")

            logger.info(f"Successfully retrieved {len(goal_value)} goal(s) with goal value '{goal_value}'")
            return goals

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving goals by goal value '{goal_value}': {e}")
            raise

    @classmethod
    def get_goals_by_completed(cls, completed: bool) -> list["Goals"]:
        """
        Retrieves all goals matching completion status.

        Args:
            completed (bool): The completion status to search for.

        Returns:
            list[Goals]: A list of goal instances matching the completion status.

        Raises:
            ValueError: If no goals with the given completion status are found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve all goals with completion status '{completed}'")

        try:
            goals = cls.query.filter_by(completed=completed).all()

            if not goals:
                logger.info(f"No goals found with completion status '{completed}'")
                raise ValueError(f"No goals found with completion status '{completed}'")

            logger.info(f"Successfully retrieved {len(completed)} goal(s) with completion status '{completed}'")
            return goals

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving goals by completion status '{completed}': {e}")
            raise

# Recommendations
    @classmethod
    def get_exercise_recommendations(cls, goal_id: int) -> list[dict]:
        """
        Gets exercise recommendations from ExerciseDB based on a goal's target.

        Args:
            goal_id (int): The ID of the goal.

        Returns:
            list[dict]: A list of recommended exercises.

        Raises:
            ValueError: If the goal is not found.
            RuntimeError: If the external API call fails.
        """
        logger.info(f"Fetching exercise recommendations for goal ID {goal_id}")

        goal = cls.query.get(goal_id)
        if not goal:
            logger.warning(f"Goal with ID {goal_id} not found.")
            raise ValueError(f"Goal with ID {goal_id} not found.")

        try:
            exercises = fetch_recommendation(goal.target)
            return exercises
        except RuntimeError as e:
            logger.error(f"Failed to fetch exercise recommendations: {e}")
            raise

    @classmethod
    def get_all_goals(cls) -> list[dict]:
        """
        Retrieves all goals from the database as dictionaries.

        Returns:
            list[dict]: A list of dictionaries representing all goals.

        Raises:
            SQLAlchemyError: If any database error occurs.
        """
        logger.info("Attempting to retrieve all goals from the database")

        try:
            goals = cls.query.all()

            if not goals:
                logger.warning("The goals table is empty.")
                return []

            results = [
                {
                    "id": goal.id,
                    "target": goal.target,
                }
                for goal in goals
            ]

            logger.info(f"Retrieved {len(results)} goals from the database")
            return results

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving all goals: {e}")
            raise

##########################################
# Update Goals
##########################################
    @classmethod
    def update_goal(
        cls,
        goal_id: int,
        target: str = None,
        goal_value: int = None,
        goal_progress: float = None,
        completed: bool = None
    ) -> "Goals":
        """
        Updates a goal in the database by its ID.

        Args:
            goal_id (int): The ID of the goal to update.
            target (str, optional): The new target value.
            goal_value (int, optional): The new goal value.
            goal_progress (float, optional): The new goal progress value.
            completed (bool, optional): The new completion status.

        Returns:
            Goals: The updated goal instance.

        Raises:
            ValueError: If the goal with the given ID does not exist or inputs are invalid.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to update goal with ID {goal_id}")

        try:
            # Retrieve the goal by ID
            goal = cls.query.get(goal_id)

            if not goal:
                logger.warning(f"Goal with ID {goal_id} not found")
                raise ValueError(f"Goal with ID {goal_id} not found")

            # Update only provided fields
            if target is not None:
                goal.target = target.strip() if isinstance(target, str) else target

            if goal_value is not None:
                if not isinstance(goal_value, int):
                    raise ValueError("goal_value must be an integer.")
                goal.goal_value = goal_value

            if goal_progress is not None:
                if not isinstance(goal_progress, float):
                    raise ValueError("goal_progress must be a float.")
                goal.goal_progress = goal_progress

            if completed is not None:
                if not isinstance(completed, bool):
                    raise ValueError("completed must be a boolean.")
                goal.completed = completed

            db.session.commit()
            logger.info(f"Successfully updated goal with ID {goal_id}")
            return goal

        except SQLAlchemyError as e:
            logger.error(f"Database error while updating goal with ID {goal_id}: {e}")
            db.session.rollback()
            raise

    def log_progress(self, amount: float) -> str:
        """
        Logs workout progress toward a goal, updates completion status, and calculates percentage progress.

        Args:
            amount (float): The amount of progress to add.

        Returns:
            str: A message indicating the current progress percentage or goal completion.

        Raises:
            ValueError: If the amount is invalid or negative.
        """
        if amount <= 0:
            raise ValueError("Progress amount must be positive.")

        if self.goal_progress is None:
            self.goal_progress = 0.0

        self.goal_progress += amount

        progress_percent = (self.goal_progress / self.goal_value) * 100

        if self.goal_progress >= self.goal_value:
            self.completed = True
            message = f"Goal completed! Progress: {progress_percent:.1f}%"
        else:
            #self.completed = False
            message = f"Progress updated: {progress_percent:.1f}% complete."

        db.session.commit()
        return message

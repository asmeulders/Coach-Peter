import logging
import os
import time
from typing import List

from coach_peter.models.goal_model import Goals
from coach_peter.utils.logger import configure_logger

logger = logging.getLogger(__name__)
configure_logger(logger)


class PlanModel:
    """
    A class to manage a fitness plan consisting of goals.

    """

    def __init__(self):
        """Initializes the PlanModel with an empty plan (and the current track set to 1).

        The plan is a list of Goals(, and the current track number is 1-indexed).
        (The TTL (Time To Live) for goal caching is set to a default value from the environment variable "TTL",
        which defaults to 60 seconds if not set.)

        """
        self.plan: List[int] = []
        self._goal_cache: dict[int, Goals] = {}

    ##################################################
    # Goal Management Functions
    ##################################################

    def _get_goal_from_cache_or_db(self, goal_id: int) -> Goals:
        """
        Retrieves a goal by ID, using the internal cache if possible.

        This method checks whether a cached version of the goal is available
        and still valid. If not, it queries the database, updates the cache, and returns the goal.

        Args:
            goal_id (int): The unique ID of the goal to retrieve.

        Returns:
            Goals: The goal object corresponding to the given ID.

        Raises:
            ValueError: If the goal cannot be found in the database.
        """
        if goal_id in self._goal_cache:
            logger.debug(f"Goal ID {goal_id} retrieved from cache")
            return self._goal_cache[goal_id]

        try:
            goal = Goals.get_goal_by_id(goal_id)
            logger.info(f"Goal ID {goal_id} loaded from DB")
        except ValueError as e:
            logger.error(f"Goal ID {goal_id} not found in DB: {e}")
            raise ValueError(f"Goal ID {goal_id} not found in database") from e

        self._goal_cache[goal_id] = goal
        return goal

    def add_goal_to_plan(self, goal_id: int) -> None:
        """
        Adds a goal to the plan by ID, using the cache or database lookup.

        Args:
            goal_id (int): The ID of the goal to add to the plan.

        Raises:
            ValueError: If the goal ID is invalid or already exists in the plan.
        """
        logger.info(f"Received request to add goal with ID {goal_id} to the plan")

        goal_id = self.validate_goal_id(goal_id, check_in_plan=False)

        try:
            goal = self._get_goal_from_cache_or_db(goal_id)
        except ValueError as e:
            logger.error(f"Failed to add goal: {e}")
            raise

        self.plan.append(goal.id)
        logger.info(f"Successfully added to plan: {goal.target}")


    def remove_goal_by_goal_id(self, goal_id: int) -> None:
        """Removes a goal from the plan by its goal ID.

        Args:
            goal_id (int): The ID of the goal to remove from the plan.

        Raises:
            ValueError: If the plan is empty or the goal ID is invalid.

        """
        logger.info(f"Received request to remove goal with ID {goal_id}")

        self.check_if_empty()
        goal_id = self.validate_goal_id(goal_id)

        if goal_id not in self.plan:
            logger.warning(f"Goal with ID {goal_id} not found in the plan")
            raise ValueError(f"Goal with ID {goal_id} not found in the plan")

        self.plan.remove(goal_id)
        logger.info(f"Successfully removed goal with ID {goal_id} from the plan")


    def clear_plan(self) -> None:
        """Clears all goals from the plan.

        Clears all goals from the plan. If the plan is already empty, logs a warning.

        """
        logger.info("Received request to clear the plan")

        try:
            if self.check_if_empty():
                pass
        except ValueError:
            logger.warning("Clearing an empty plan")

        self.plan.clear()
        logger.info("Successfully cleared the plan")


    ##################################################
    # Plan Retrieval Functions
    ##################################################


    def get_all_goals(self) -> List[Goals]:
        """Returns a list of all goals in the plan using cached goal data.

        Returns:
            List[goal]: A list of all goals in the plan.

        Raises:
            ValueError: If the plan is empty.
        """
        logger.info(f"Retrieving all goals in the plan: {self.plan}")
        self.check_if_empty()
        
        return [self._get_goal_from_cache_or_db(goal_id) for goal_id in self.plan]

    def get_goal_by_goal_id(self, goal_id: int) -> Goals:
        """Retrieves a goal from the plan by its goal ID using the cache or DB.

        Args:
            goal_id (int): The ID of the goal to retrieve.

        Returns:
            goal: The goal with the specified ID.

        Raises:
            ValueError: If the plan is empty or the goal is not found.
        """
        self.check_if_empty()
        goal_id = self.validate_goal_id(goal_id)
        logger.info(f"Retrieving goal with ID {goal_id} from the plan")
        goal = self._get_goal_from_cache_or_db(goal_id)
        logger.info(f"Successfully retrieved goal: ")
        return goal

    def get_plan_length(self) -> int:
        """Returns the number of goals in the plan.

        Returns:
            int: The total number of goals in the plan.

        """
        length = len(self.plan)
        logger.info(f"Retrieving plan length: {length} goals")
        return length
    
    def get_plan_progress(self) -> float:
        """Returns percentage of the goals completed in the plan.

        Returns:
            float: The percentage of the goals completed in the plan.

        Raises:
            ValueError: If the plan is empty
        """
        self.check_if_empty()
        completed = 0
        length = len(self.plan)
        logger.info(f"Retrieving number of completed goals")

        for goal_id in self.plan:
            goal = Goals.get_goal_by_id(goal_id)
            if goal.completed:
                completed += 1

        
        percentage: float = round(completed / length, 3)
        logger.info(f"User has completed {percentage}% of their goals!")
        return percentage

    ##################################################
    # Utility Functions
    ##################################################


    ####################################################################################################
    #
    # Note: I am only testing these things once. EG I am not testing that everything rejects an empty
    # list as they all do so by calling this helper
    #
    ####################################################################################################

    def validate_goal_id(self, goal_id: int, check_in_plan: bool = True) -> int:
        """
        Validates the given goal ID.

        Args:
            goal_id (int): The goal ID to validate.
            check_in_plan (bool, optional): If True, verifies the ID is present in the plan.
                                                If False, skips that check. Defaults to True.

        Returns:
            int: The validated goal ID.

        Raises:
            ValueError: If the goal ID is not a non-negative integer,
                        not found in the plan (if check_in_plan=True),
                        or not found in the database.
        """
        try:
            goal_id = int(goal_id)
            if goal_id < 0:
                raise ValueError
        except ValueError:
            logger.error(f"Invalid goal id: {goal_id}")
            raise ValueError(f"Invalid goal id: {goal_id}")

        if check_in_plan and goal_id not in self.plan:
            logger.error(f"Goal with id {goal_id} not found in plan")
            raise ValueError(f"Goal with id {goal_id} not found in plan")

        try:
            self._get_goal_from_cache_or_db(goal_id)
        except Exception as e:
            logger.error(f"Goal with id {goal_id} not found in database: {e}")
            raise ValueError(f"Goal with id {goal_id} not found in database")

        return goal_id

    def check_if_empty(self) -> None:
        """
        Checks if the plan is empty and raises a ValueError if it is.

        Raises:
            ValueError: If the plan is empty.

        """
        if not self.plan:
            logger.error("Plan is empty")
            raise ValueError("Plan is empty")

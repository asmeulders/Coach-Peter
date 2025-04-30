import logging
import os
import time
from typing import List

from coach_peter.models.goal_model import Goals
# from coach_peter.utils.api_utils import get_random
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
        # self.current_track_number = 1
        self.plan: List[int] = []
        self._goal_cache: dict[int, Goals] = {}
        # self._ttl: dict[int, float] = {}
        # self.ttl_seconds = int(os.getenv("TTL", 60))  # Default TTL is 60 seconds


    ##################################################
    # goal Management Functions
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
        now = time.time()

        if goal_id in self._goal_cache: # and self._ttl.get(goal_id, 0) > now:
            logger.debug(f"Goal ID {goal_id} retrieved from cache")
            return self._goal_cache[goal_id]

        try:
            goal = Goals.get_goal_by_id(goal_id)
            logger.info(f"Goal ID {goal_id} loaded from DB")
        except ValueError as e:
            logger.error(f"Goal ID {goal_id} not found in DB: {e}")
            raise ValueError(f"Goal ID {goal_id} not found in database") from e

        self._goal_cache[goal_id] = goal
        # self._ttl[goal_id] = now + self.ttl_seconds
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

        if goal_id in self.plan:
            logger.error(f"Goal with ID {goal_id} already exists in the plan")
            raise ValueError(f"Goal with ID {goal_id} already exists in the plan")

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

    # def remove_goal_by_track_number(self, track_number: int) -> None: TODO remove by target? could be a good one to have but would require SQL
    #     """Removes a goal from the plan by its track number (1-indexed).

    #     Args:
    #         track_number (int): The track number of the goal to remove.

    #     Raises:
    #         ValueError: If the plan is empty or the track number is invalid.

    #     """
    #     logger.info(f"Received request to remove goal at track number {track_number}")

    #     self.check_if_empty()
    #     track_number = self.validate_track_number(track_number)
    #     plan_index = track_number - 1

    #     logger.info(f"Successfully removed goal at track number {track_number}")
    #     del self.plan[plan_index]

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
    # plan Retrieval Functions
    ##################################################


    def get_all_goals(self) -> List[Goals]:
        """Returns a list of all goals in the plan using cached goal data.

        Returns:
            List[goal]: A list of all goals in the plan.

        Raises:
            ValueError: If the plan is empty.
        """
        self.check_if_empty()
        logger.info("Retrieving all goals in the plan")
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
        logger.info(f"Successfully retrieved goal: ") # {goal.artist} - {goal.title} ({goal.year})")
        return goal

    # def get_goal_by_track_number(self, track_number: int) -> Goals:
    #     """Retrieves a goal from the plan by its track number (1-indexed).

    #     Args:
    #         track_number (int): The track number of the goal to retrieve.

    #     Returns:
    #         goal: The goal at the specified track number.

    #     Raises:
    #         ValueError: If the plan is empty or the track number is invalid.
    #     """
    #     self.check_if_empty()
    #     track_number = self.validate_track_number(track_number)
    #     plan_index = track_number - 1

    #     logger.info(f"Retrieving goal at track number {track_number} from plan")
    #     goal_id = self.plan[plan_index]
    #     goal = self._get_goal_from_cache_or_db(goal_id)
    #     logger.info(f"Successfully retrieved goal: {goal.artist} - {goal.title} ({goal.year})")
    #     return goal

    # def get_current_goal(self) -> Goals:
    #     """Returns the current goal being played.

    #     Returns:
    #         goal: The currently playing goal.

    #     Raises:
    #         ValueError: If the plan is empty.
    #     """
    #     self.check_if_empty()
    #     logger.info("Retrieving the current goal being played")
    #     return self.get_goal_by_track_number(self.current_track_number)

    def get_plan_length(self) -> int:
        """Returns the number of goals in the plan.

        Returns:
            int: The total number of goals in the plan.

        """
        length = len(self.plan)
        logger.info(f"Retrieving plan length: {length} goals")
        return length

    # def get_plan_duration(self) -> int:
    #     """
    #     Returns the total duration of the plan in seconds using cached goals.

    #     Returns:
    #         int: The total duration of all goals in the plan in seconds.
    #     """
    #     total_duration = sum(self._get_goal_from_cache_or_db(goal_id).duration for goal_id in self.plan)
    #     logger.info(f"Retrieving total plan duration: {total_duration} seconds")
    #     return total_duration


    ##################################################
    # plan Movement Functions
    ##################################################


    # def go_to_track_number(self, track_number: int) -> None:
    #     """Sets the current track number to the specified track number.

    #     Args:
    #         track_number (int): The track number to set as the current track.

    #     Raises:
    #         ValueError: If the plan is empty or the track number is invalid.

    #     """
    #     self.check_if_empty()
    #     track_number = self.validate_track_number(track_number)
    #     logger.info(f"Setting current track number to {track_number}")
    #     self.current_track_number = track_number

    # def go_to_random_track(self) -> None:
    #     """Sets the current track number to a randomly selected track.

    #     Raises:
    #         ValueError: If the plan is empty.

    #     """
    #     self.check_if_empty()

    #     # Get a random index using the random.org API
    #     random_track = get_random(self.get_plan_length())

    #     logger.info(f"Setting current track number to random track: {random_track}")
    #     self.current_track_number = random_track

    # def move_goal_to_beginning(self, goal_id: int) -> None:
    #     """Moves a goal to the beginning of the plan.

    #     Args:
    #         goal_id (int): The ID of the goal to move.

    #     Raises:
    #         ValueError: If the plan is empty or the goal ID is invalid.

    #     """
    #     logger.info(f"Moving goal with ID {goal_id} to the beginning of the plan")
    #     self.check_if_empty()
    #     goal_id = self.validate_goal_id(goal_id)

    #     self.plan.remove(goal_id)
    #     self.plan.insert(0, goal_id)

    #     logger.info(f"Successfully moved goal with ID {goal_id} to the beginning")

    # def move_goal_to_end(self, goal_id: int) -> None:
    #     """Moves a goal to the end of the plan.

    #     Args:
    #         goal_id (int): The ID of the goal to move.

    #     Raises:
    #         ValueError: If the plan is empty or the goal ID is invalid.

    #     """
    #     logger.info(f"Moving goal with ID {goal_id} to the end of the plan")
    #     self.check_if_empty()
    #     goal_id = self.validate_goal_id(goal_id)

    #     self.plan.remove(goal_id)
    #     self.plan.append(goal_id)

    #     logger.info(f"Successfully moved goal with ID {goal_id} to the end")

    # def move_goal_to_track_number(self, goal_id: int, track_number: int) -> None:
    #     """Moves a goal to a specific track number in the plan.

    #     Args:
    #         goal_id (int): The ID of the goal to move.
    #         track_number (int): The track number to move the goal to (1-indexed).

    #     Raises:
    #         ValueError: If the plan is empty, the goal ID is invalid, or the track number is out of range.

    #     """
    #     logger.info(f"Moving goal with ID {goal_id} to track number {track_number}")
    #     self.check_if_empty()
    #     goal_id = self.validate_goal_id(goal_id)
    #     track_number = self.validate_track_number(track_number)

    #     plan_index = track_number - 1

    #     self.plan.remove(goal_id)
    #     self.plan.insert(plan_index, goal_id)

    #     logger.info(f"Successfully moved goal with ID {goal_id} to track number {track_number}")

    # def swap_goals_in_plan(self, goal1_id: int, goal2_id: int) -> None:
    #     """Swaps the positions of two goals in the plan.

    #     Args:
    #         goal1_id (int): The ID of the first goal to swap.
    #         goal2_id (int): The ID of the second goal to swap.

    #     Raises:
    #         ValueError: If the plan is empty, either goal ID is invalid, or attempting to swap the same goal.

    #     """
    #     logger.info(f"Swapping goals with IDs {goal1_id} and {goal2_id}")
    #     self.check_if_empty()
    #     goal1_id = self.validate_goal_id(goal1_id)
    #     goal2_id = self.validate_goal_id(goal2_id)

    #     if goal1_id == goal2_id:
    #         logger.error(f"Cannot swap a goal with itself: {goal1_id}")
    #         raise ValueError(f"Cannot swap a goal with itself: {goal1_id}")

    #     index1, index2 = self.plan.index(goal1_id), self.plan.index(goal2_id)

    #     self.plan[index1], self.plan[index2] = self.plan[index2], self.plan[index1]

    #     logger.info(f"Successfully swapped goals with IDs {goal1_id} and {goal2_id}")


    ##################################################
    # plan Playback Functions
    ##################################################


    # def play_current_goal(self) -> None:
    #     """Plays the current goal and advances the plan.

    #     Raises:
    #         ValueError: If the plan is empty.

    #     """
    #     self.check_if_empty()
    #     current_goal = self.get_goal_by_track_number(self.current_track_number)

    #     logger.info(f"Playing goal: {current_goal.title} (ID: {current_goal.id}) at track number: {self.current_track_number}")
    #     current_goal.update_play_count()
    #     logger.info(f"Updated play count for goal: {current_goal.title} (ID: {current_goal.id})")

    #     self.current_track_number = (self.current_track_number % self.get_plan_length()) + 1
    #     logger.info(f"Advanced to track number: {self.current_track_number}")

    # def play_entire_plan(self) -> None:
    #     """Plays all goals in the plan from the beginning.

    #     Raises:
    #         ValueError: If the plan is empty.

    #     """
    #     self.check_if_empty()
    #     logger.info("Starting to play the entire plan.")

    #     self.current_track_number = 1
    #     for _ in range(self.get_plan_length()):
    #         self.play_current_goal()

    #     logger.info("Finished playing the entire plan.")

    # def play_rest_of_plan(self) -> None:
    #     """Plays the remaining goals in the plan from the current track onward.

    #     Raises:
    #         ValueError: If the plan is empty.

    #     """
    #     self.check_if_empty()
    #     logger.info(f"Playing the rest of the plan from track number: {self.current_track_number}")

    #     for _ in range(self.get_plan_length() - self.current_track_number + 1):
    #         self.play_current_goal()

    #     logger.info("Finished playing the rest of the plan.")

    # def rewind_plan(self) -> None:
    #     """Resets the plan to the first track.

    #     Raises:
    #         ValueError: If the plan is empty.

    #     """
    #     self.check_if_empty()
    #     self.current_track_number = 1
    #     logger.info("Rewound plan to the first track.")


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

    # def validate_track_number(self, track_number: int) -> int:
    #     """
    #     Validates the given track number, ensuring it is within the plan's range.

    #     Args:
    #         track_number (int): The track number to validate.

    #     Returns:
    #         int: The validated track number.

    #     Raises:
    #         ValueError: If the track number is not a valid positive integer or is out of range.

    #     """
    #     try:
    #         track_number = int(track_number)
    #         if not (1 <= track_number <= self.get_plan_length()):
    #             raise ValueError(f"Invalid track number: {track_number}")
    #     except ValueError as e:
    #         logger.error(f"Invalid track number: {track_number}")
    #         raise ValueError(f"Invalid track number: {track_number}") from e

    #     return track_number

    def check_if_empty(self) -> None:
        """
        Checks if the plan is empty and raises a ValueError if it is.

        Raises:
            ValueError: If the plan is empty.

        """
        if not self.plan:
            logger.error("Plan is empty")
            raise ValueError("Plan is empty")

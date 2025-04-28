import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Double check if correct db
from fitness.db import db
from fitness.utils.logger import configure_logger
# from fitness.utils.api_utils import get_random


logger = logging.getLogger(__name__)
configure_logger(logger)

#TODO####################################################################
class Goals(db.Model):
    """Represents a goal in the plan.

    This model maps to the 'goals' table and stores metadata such as nutritional, physical, recurring, 
    one-time, upper body, core, and lower body goals.

    Used in a Flask-SQLAlchemy application for fitness management,
    user interaction, and data-driven goal operations.
    """

    __tablename__ = "Goals"
    
    # Users can choose which types of goals they want 
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nutritional = db.Column(db.String, nullable=True)
    physical = db.Column(db.String, nullable=True)
    recurring = db.Column(db.String, nullable=True)
    one_time = db.Column(db.String, nullable=True)
    upper_body = db.Column(db.String, nullable=True)
    core = db.Column(db.String, nullable=True)
    lower_body = db.Column(db.String, nullable=True)
    # play_count = db.Column(db.Integer, nullable=False, default=0)

    def validate(self) -> None:
        """Validates the goal instance before committing to the database.

        Raises:
            ValueError: If any required fields are invalid.
        """
        
        # If a field is provided, check that it's a non-empty string
        # Checks only if field is provided (because it is nullable) and if provided, must be a non-empty string
        if self.nutritional is not None and (not isinstance(self.nutritional, str) or not self.nutritional.strip()):
            raise ValueError("Nutritional goal must be a non-empty string if provided.")
        if self.physical is not None and (not isinstance(self.physical, str) or not self.physical.strip()):
            raise ValueError("Physical goal must be a non-empty string if provided.")
        if self.recurring is not None and (not isinstance(self.recurring, str) or not self.recurring.strip()):
            raise ValueError("Recurring goal must be a non-empty string if provided.")
        if self.one_time is not None and (not isinstance(self.one_time, str) or not self.one_time.strip()):
            raise ValueError("One-time goal must be a non-empty string if provided.")
        if self.upper_body is not None and (not isinstance(self.upper_body, str) or not self.upper_body.strip()):
            raise ValueError("Upper body goal must be a non-empty string if provided.")
        if self.core is not None and (not isinstance(self.core, str) or not self.core.strip()):
            raise ValueError("Core goal must be a non-empty string if provided.")
        if self.lower_body is not None and (not isinstance(self.lower_body, str) or not self.lower_body.strip()):
            raise ValueError("Lower body goal must be a non-empty string if provided.")
        # does not allow an empty goal creation
        if not any([self.nutritional, self.physical, self.recurring, self.one_time, self.upper_body, self.core, self.lower_body]):
            raise ValueError("At least one goal field must be provided.")

        # if not self.title or not isinstance(self.title, str):
        #     raise ValueError("Title must be a non-empty string.")
        # if not isinstance(self.year, int) or self.year <= 1900:
        #     raise ValueError("Year must be an integer greater than 1900.")
        # if not self.genre or not isinstance(self.genre, str):
        #     raise ValueError("Genre must be a non-empty string.")
        # if not isinstance(self.duration, int) or self.duration <= 0:
        #     raise ValueError("Duration must be a positive integer.")

    @classmethod
    def create_goal(cls, nutritional: str, physical: str, recurring: str, one_time: str, upper_body: str, core: str, lower_body: str, ) -> None:
        """
        Creates a new goal in the goals table using SQLAlchemy.

        Args:
            nutritional (str): A nutritional fitness goal the user wants to achieve.
            physical (str): A physical fitness goal the user wants to achieve.
            recurring (str): A recurring fitness goal the user wants to achieve.
            one_time (str): A one time fitness goal the user wants to achieve.
            upper_body (str): An upper body fitness goal the user wants to achieve.
            core (str): A core fitness goal the user wants to achieve.
            lower_body (str): A lower body fitness goal the user wants to achieve.


        Raises:
            ValueError: If any field is invalid or if a song with the same compound key already exists.
            SQLAlchemyError: For any other database-related issues.
        """
        logger.info(f"Received request to create goal.")

        try:
            goal = Goals(
                nutritional=nutritional.strip() if nutritional else None,
                physical=physical.strip() if physical else None,
                recurring=recurring.strip() if recurring else None,
                one_time=one_time.strip() if one_time else None,
                upper_body=upper_body.strip() if upper_body else None,
                core=core.strip() if core else None,
                lower_body=lower_body.strip() if lower_body else None
            )
            goal.validate()
        except ValueError as e:
            logger.warning(f"Validation failed: {e}")
            raise

        try:
            db.session.add(goal)
            db.session.commit()
            logger.info(f"Goal successfully added with nutritional goals: {nutritional}, physical goals: {physical}, recurring goals: {recurring}, one_time goals: {one_time}, upper_body goals: {upper_body}, core goals: {core}, lower_body goals: {lower_body}.")

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

            logger.info(f"Successfully retrieved goal: {goal.nutritional}, physical goals: {goal.physical}, recurring goals: {goal.recurring}, one_time goals: {goal.one_time}, upper_body goals: {goal.upper_body}, core goals: {goal.core}, lower_body goals: {goal.lower_body}.")
            return goal

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving goal by ID {goal_id}: {e}")
            raise

#Returns all goals with wanted nutritional value 
    @classmethod
    def get_goals_by_nutritional(cls, nutritional: str) -> list["Goals"]:
        """
        Retrieves all goals matching a specific nutritional field.

        Args:
            nutritional (str): The nutritional goal to search for.

        Returns:
            list[Goals]: A list of goal instances matching the nutritional value.

        Raises:
            ValueError: If no goals with the given nutritional value are found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve all goals with nutritional value '{nutritional}'")

        try:
            goals = cls.query.filter_by(nutritional=nutritional).all()

            if not goals:
                logger.info(f"No goals found with nutritional value '{nutritional}'")
                raise ValueError(f"No goals found with nutritional value '{nutritional}'")

            logger.info(f"Successfully retrieved {len(goals)} goal(s) with nutritional value '{nutritional}'")
            return goals

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving goals by nutritional value '{nutritional}': {e}")
            raise

#Returns all goals with wanted physical value 
    @classmethod
    def get_goals_by_physical(cls, physical: str) -> list["Goals"]:
        """
        Retrieves all goals matching a specific physical field.

        Args:
            physical (str): The physical goal to search for.

        Returns:
            list[Goals]: A list of goal instances matching the physical value.

        Raises:
            ValueError: If no goals with the given physical value are found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve all goals with physical value '{physical}'")

        try:
            goals = cls.query.filter_by(physical=physical).all()

            if not goals:
                logger.info(f"No goals found with physical value '{physical}'")
                raise ValueError(f"No goals found with physical value '{physical}'")

            logger.info(f"Successfully retrieved {len(goals)} goal(s) with physical value '{physical}'")
            return goals

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving goals by physical value '{physical}': {e}")
            raise

#Returns all goals with wanted recurring value 
    @classmethod
    def get_goals_by_recurring(cls, recurring: str) -> list["Goals"]:
        """
        Retrieves all goals matching a specific recurring field.

        Args:
            recurring (str): The recurring goal to search for.

        Returns:
            list[Goals]: A list of goal instances matching the recurring value.

        Raises:
            ValueError: If no goals with the given recurring value are found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve all goals with recurring value '{recurring}'")

        try:
            goals = cls.query.filter_by(recurring=recurring).all()

            if not goals:
                logger.info(f"No goals found with recurring value '{recurring}'")
                raise ValueError(f"No goals found with recurring value '{recurring}'")

            logger.info(f"Successfully retrieved {len(goals)} goal(s) with recurring value '{recurring}'")
            return goals

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving goals by recurring value '{recurring}': {e}")
            raise

#Returns all goals with wanted one_time value 
    @classmethod
    def get_goals_by_one_time(cls, one_time: str) -> list["Goals"]:
        """
        Retrieves all goals matching a specific one_time field.

        Args:
            one_time (str): The one_time goal to search for.

        Returns:
            list[Goals]: A list of goal instances matching the one_time value.

        Raises:
            ValueError: If no goals with the given one_time value are found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve all goals with one_time value '{one_time}'")

        try:
            goals = cls.query.filter_by(one_time=one_time).all()

            if not goals:
                logger.info(f"No goals found with one_time value '{one_time}'")
                raise ValueError(f"No goals found with one_time value '{one_time}'")

            logger.info(f"Successfully retrieved {len(goals)} goal(s) with one_time value '{one_time}'")
            return goals

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving goals by one_time value '{one_time}': {e}")
            raise

#Returns all goals with wanted upper_body value 
    @classmethod
    def get_goals_by_upper_body(cls, upper_body: str) -> list["Goals"]:
        """
        Retrieves all goals matching a specific upper_body field.

        Args:
            upper_body (str): The upper_body goal to search for.

        Returns:
            list[Goals]: A list of goal instances matching the upper_body value.

        Raises:
            ValueError: If no goals with the given upper_body value are found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve all goals with upper_body value '{upper_body}'")

        try:
            goals = cls.query.filter_by(upper_body=upper_body).all()

            if not goals:
                logger.info(f"No goals found with upper_body value '{upper_body}'")
                raise ValueError(f"No goals found with upper_body value '{upper_body}'")

            logger.info(f"Successfully retrieved {len(goals)} goal(s) with upper_body value '{upper_body}'")
            return goals

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving goals by upper_body value '{upper_body}': {e}")
            raise

#Returns all goals with wanted core value 
    @classmethod
    def get_goals_by_core(cls, core: str) -> list["Goals"]:
        """
        Retrieves all goals matching a specific core field.

        Args:
            core (str): The core goal to search for.

        Returns:
            list[Goals]: A list of goal instances matching the core value.

        Raises:
            ValueError: If no goals with the given core value are found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve all goals with core value '{core}'")

        try:
            goals = cls.query.filter_by(core=core).all()

            if not goals:
                logger.info(f"No goals found with core value '{core}'")
                raise ValueError(f"No goals found with core value '{core}'")

            logger.info(f"Successfully retrieved {len(goals)} goal(s) with core value '{core}'")
            return goals

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving goals by core value '{core}': {e}")
            raise

#Returns all goals with wanted lower_body value 
    @classmethod
    def get_goals_by_lower_body(cls, lower_body: str) -> list["Goals"]:
        """
        Retrieves all goals matching a specific lower_body field.

        Args:
            lower_body (str): The lower_body goal to search for.

        Returns:
            list[Goals]: A list of goal instances matching the lower_body value.

        Raises:
            ValueError: If no goals with the given lower_body value are found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve all goals with lower_body value '{lower_body}'")

        try:
            goals = cls.query.filter_by(lower_body=lower_body).all()

            if not goals:
                logger.info(f"No goals found with lower_body value '{lower_body}'")
                raise ValueError(f"No goals found with lower_body value '{lower_body}'")

            logger.info(f"Successfully retrieved {len(goals)} goal(s) with lower_body value '{lower_body}'")
            return goals

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving goals by lower_body value '{lower_body}': {e}")
            raise


    # @classmethod
    # def get_song_by_compound_key(cls, artist: str, title: str, year: int) -> "Songs":
    #     """
    #     Retrieves a song from the catalog by its compound key (artist, title, year).

    #     Args:
    #         artist (str): The artist of the song.
    #         title (str): The title of the song.
    #         year (int): The year the song was released.

    #     Returns:
    #         Songs: The song instance matching the provided compound key.

    #     Raises:
    #         ValueError: If no matching song is found.
    #         SQLAlchemyError: If a database error occurs.
    #     """
    #     logger.info(f"Attempting to retrieve song with artist '{artist}', title '{title}', and year {year}")

    #     try:
    #         song = cls.query.filter_by(artist=artist.strip(), title=title.strip(), year=year).first()

    #         if not song:
    #             logger.info(f"Song with artist '{artist}', title '{title}', and year {year} not found")
    #             raise ValueError(f"Song with artist '{artist}', title '{title}', and year {year} not found")

    #         logger.info(f"Successfully retrieved song: {song.artist} - {song.title} ({song.year})")
    #         return song

    #     except SQLAlchemyError as e:
    #         logger.error(
    #             f"Database error while retrieving song by compound key "
    #             f"(artist '{artist}', title '{title}', year {year}): {e}"
    #         )
    #         raise

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
                    "nutritional": goal.nutritional,
                    "physical": goal.physical,
                    "recurring": goal.recurring,
                    "one_time": goal.one_time,
                    "upper_body": goal.upper_body,
                    "core": goal.core,
                    "lower_body": goal.lower_body,
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
    def update_goal(cls, goal_id: int, nutritional: str = None, physical: str = None, 
                    recurring: str = None, one_time: str = None, upper_body: str = None, 
                    core: str = None, lower_body: str = None) -> "Goals":
        """
        Updates a goal in the database by its ID.

        Args:
            goal_id (int): The ID of the goal to update.
            nutritional (str, optional): The new nutritional goal value.
            physical (str, optional): The new physical goal value.
            recurring (str, optional): The new recurring goal value.
            one_time (str, optional): The new one-time goal value.
            upper_body (str, optional): The new upper body goal value.
            core (str, optional): The new core body goal value.
            lower_body (str, optional): The new lower body goal value.

        Returns:
            Goals: The updated goal instance.

        Raises:
            ValueError: If the goal with the given ID does not exist.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to update goal with ID {goal_id}")

        try:
            # Retrieve the goal by ID
            goal = cls.query.get(goal_id)

            if not goal:
                logger.warning(f"Goal with ID {goal_id} not found")
                raise ValueError(f"Goal with ID {goal_id} not found")

            # Update fields only if provided (None will leave them unchanged)
            if nutritional is not None:
                goal.nutritional = nutritional
            if physical is not None:
                goal.physical = physical
            if recurring is not None:
                goal.recurring = recurring
            if one_time is not None:
                goal.one_time = one_time
            if upper_body is not None:
                goal.upper_body = upper_body
            if core is not None:
                goal.core = core
            if lower_body is not None:
                goal.lower_body = lower_body

            # Commit the changes
            db.session.commit()

            logger.info(f"Successfully updated goal with ID {goal_id}")
            return goal

        except SQLAlchemyError as e:
            logger.error(f"Database error while updating goal with ID {goal_id}: {e}")
            db.session.rollback()
            raise


    # @classmethod
    # def get_random_song(cls) -> dict:
    #     """
    #     Retrieves a random song from the catalog as a dictionary.

    #     Returns:
    #         dict: A randomly selected song dictionary.
    #     """
    #     all_songs = cls.get_all_songs()

    #     if not all_songs:
    #         logger.warning("Cannot retrieve random song because the song catalog is empty.")
    #         raise ValueError("The song catalog is empty.")

    #     index = get_random(len(all_songs))
    #     logger.info(f"Random index selected: {index} (total songs: {len(all_songs)})")

    #     return all_songs[index - 1]

    # def update_play_count(self) -> None:
    #     """
    #     Increments the play count of the current song instance.

    #     Raises:
    #         ValueError: If the song does not exist in the database.
    #         SQLAlchemyError: If any database error occurs.
    #     """

    #     logger.info(f"Attempting to update play count for song with ID {self.id}")

    #     try:
    #         song = Songs.query.get(self.id)
    #         if not song:
    #             logger.warning(f"Cannot update play count: Song with ID {self.id} not found.")
    #             raise ValueError(f"Song with ID {self.id} not found")

    #         song.play_count += 1
    #         db.session.commit()

    #         logger.info(f"Play count incremented for song with ID: {self.id}")

    #     except SQLAlchemyError as e:
    #         logger.error(f"Database error while updating play count for song with ID {self.id}: {e}")
    #         db.session.rollback()
    #         raise

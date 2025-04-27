import logging

from sqlalchemy.exc import IntegrityError, SQLAlchemyError

# Double check if correct db
from fitness.db import db
from fitness.utils.logger import configure_logger
from fitness.utils.api_utils import get_random


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
        logger.info(f"Received request to create goal: {artist} - {title} ({year})")

        try:
            song = Songs(
                artist=artist.strip(),
                title=title.strip(),
                year=year,
                genre=genre.strip(),
                duration=duration
            )
            song.validate()
        except ValueError as e:
            logger.warning(f"Validation failed: {e}")
            raise

        try:
            # Check for existing song with same compound key (artist, title, year)
            existing = Songs.query.filter_by(artist=artist.strip(), title=title.strip(), year=year).first()
            if existing:
                logger.error(f"Song already exists: {artist} - {title} ({year})")
                raise ValueError(f"Song with artist '{artist}', title '{title}', and year {year} already exists.")

            db.session.add(song)
            db.session.commit()
            logger.info(f"Song successfully added: {artist} - {title} ({year})")

        except IntegrityError:
            logger.error(f"Song already exists: {artist} - {title} ({year})")
            db.session.rollback()
            raise ValueError(f"Song with artist '{artist}', title '{title}', and year {year} already exists.")

        except SQLAlchemyError as e:
            logger.error(f"Database error while creating song: {e}")
            db.session.rollback()
            raise

    @classmethod
    def delete_song(cls, song_id: int) -> None:
        """
        Permanently deletes a song from the catalog by ID.

        Args:
            song_id (int): The ID of the song to delete.

        Raises:
            ValueError: If the song with the given ID does not exist.
            SQLAlchemyError: For any database-related issues.
        """
        logger.info(f"Received request to delete song with ID {song_id}")

        try:
            song = cls.query.get(song_id)
            if not song:
                logger.warning(f"Attempted to delete non-existent song with ID {song_id}")
                raise ValueError(f"Song with ID {song_id} not found")

            db.session.delete(song)
            db.session.commit()
            logger.info(f"Successfully deleted song with ID {song_id}")

        except SQLAlchemyError as e:
            logger.error(f"Database error while deleting song with ID {song_id}: {e}")
            db.session.rollback()
            raise

    @classmethod
    def get_song_by_id(cls, song_id: int) -> "Songs":
        """
        Retrieves a song from the catalog by its ID.

        Args:
            song_id (int): The ID of the song to retrieve.

        Returns:
            Songs: The song instance corresponding to the ID.

        Raises:
            ValueError: If no song with the given ID is found.
            SQLAlchemyError: If a database error occurs.
        """
        logger.info(f"Attempting to retrieve song with ID {song_id}")

        try:
            song = cls.query.get(song_id)

            if not song:
                logger.info(f"Song with ID {song_id} not found")
                raise ValueError(f"Song with ID {song_id} not found")

            logger.info(f"Successfully retrieved song: {song.artist} - {song.title} ({song.year})")
            return song

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving song by ID {song_id}: {e}")
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
    def get_all_songs(cls, sort_by_play_count: bool = False) -> list[dict]:
        """
        Retrieves all songs from the catalog as dictionaries.

        Args:
            sort_by_play_count (bool): If True, sort the songs by play count in descending order.

        Returns:
            list[dict]: A list of dictionaries representing all songs with play_count.

        Raises:
            SQLAlchemyError: If any database error occurs.
        """
        logger.info("Attempting to retrieve all songs from the catalog")

        try:
            query = cls.query
            if sort_by_play_count:
                query = query.order_by(cls.play_count.desc())

            songs = query.all()

            if not songs:
                logger.warning("The song catalog is empty.")
                return []

            results = [
                {
                    "id": song.id,
                    "artist": song.artist,
                    "title": song.title,
                    "year": song.year,
                    "genre": song.genre,
                    "duration": song.duration,
                    "play_count": song.play_count,
                }
                for song in songs
            ]

            logger.info(f"Retrieved {len(results)} songs from the catalog")
            return results

        except SQLAlchemyError as e:
            logger.error(f"Database error while retrieving all songs: {e}")
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

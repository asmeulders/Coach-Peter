from dotenv import load_dotenv
from flask import Flask, jsonify, make_response, Response, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

from config import ProductionConfig

from coach_peter.db import db
from coach_peter.models.goal_model import Goals
from coach_peter.models.plan_model import PlanModel
from coach_peter.models.user_model import Users
from coach_peter.utils.logger import configure_logger


load_dotenv()


def create_app(config_class=ProductionConfig) -> Flask:
    """Create a Flask application with the specified configuration.

    Args:
        config_class (Config): The configuration class to use.

    Returns:
        Flask app: The configured Flask application.

    """
    app = Flask(__name__)
    configure_logger(app.logger)

    app.config.from_object(config_class)

    # Initialize database
    db.init_app(app)
    with app.app_context():
        db.create_all()

    # Initialize login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.filter_by(username=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized():
        return make_response(jsonify({
            "status": "error",
            "message": "Authentication required"
        }), 401)

    plan_model = PlanModel()

    @app.route('/api/health', methods=['GET'])
    def healthcheck() -> Response:
        """Health check route to verify the service is running.

        Returns:
            JSON response indicating the health status of the service.

        """
        app.logger.info("Health check endpoint hit")
        return make_response(jsonify({
            'status': 'success',
            'message': 'Service is running'
        }), 200)

    ##########################################################
    #
    # User Management
    #
    #########################################################

    @app.route('/api/create-user', methods=['PUT'])
    def create_user() -> Response:
        """Register a new user account.

        Expected JSON Input:
            - username (str): The desired username.
            - password (str): The desired password.

        Returns:
            JSON response indicating the success of the user creation.

        Raises:
            400 error if the username or password is missing.
            500 error if there is an issue creating the user in the database.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            Users.create_user(username, password)
            return make_response(jsonify({
                "status": "success",
                "message": f"User '{username}' created successfully"
            }), 201)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"User creation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while creating user",
                "details": str(e)
            }), 500)

    @app.route('/api/login', methods=['POST'])
    def login() -> Response:
        """Authenticate a user and log them in.

        Expected JSON Input:
            - username (str): The username of the user.
            - password (str): The password of the user.

        Returns:
            JSON response indicating the success of the login attempt.

        Raises:
            401 error if the username or password is incorrect.
        """
        try:
            data = request.get_json()
            username = data.get("username")
            password = data.get("password")

            if not username or not password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Username and password are required"
                }), 400)

            if Users.check_password(username, password):
                user = Users.query.filter_by(username=username).first()
                login_user(user)
                return make_response(jsonify({
                    "status": "success",
                    "message": f"User '{username}' logged in successfully"
                }), 200)
            else:
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid username or password"
                }), 401)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 401)
        except Exception as e:
            app.logger.error(f"Login failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred during login",
                "details": str(e)
            }), 500)

    @app.route('/api/logout', methods=['POST'])
    @login_required
    def logout() -> Response:
        """Log out the current user.

        Returns:
            JSON response indicating the success of the logout operation.

        """
        logout_user()
        return make_response(jsonify({
            "status": "success",
            "message": "User logged out successfully"
        }), 200)

    @app.route('/api/change-password', methods=['POST'])
    @login_required
    def change_password() -> Response:
        """Change the password for the current user.

        Expected JSON Input:
            - new_password (str): The new password to set.

        Returns:
            JSON response indicating the success of the password change.

        Raises:
            400 error if the new password is not provided.
            500 error if there is an issue updating the password in the database.
        """
        try:
            data = request.get_json()
            new_password = data.get("new_password")

            if not new_password:
                return make_response(jsonify({
                    "status": "error",
                    "message": "New password is required"
                }), 400)

            username = current_user.username
            Users.update_password(username, new_password)
            return make_response(jsonify({
                "status": "success",
                "message": "Password changed successfully"
            }), 200)

        except ValueError as e:
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"Password change failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while changing password",
                "details": str(e)
            }), 500)

    @app.route('/api/reset-users', methods=['DELETE'])
    def reset_users() -> Response:
        """Recreate the users table to delete all users.

        Returns:
            JSON response indicating the success of recreating the Users table.

        Raises:
            500 error if there is an issue recreating the Users table.
        """
        try:
            app.logger.info("Received request to recreate Users table")
            with app.app_context():
                Users.__table__.drop(db.engine)
                Users.__table__.create(db.engine)
            app.logger.info("Users table recreated successfully")
            return make_response(jsonify({
                "status": "success",
                "message": f"Users table recreated successfully"
            }), 200)

        except Exception as e:
            app.logger.error(f"Users table recreation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting users",
                "details": str(e)
            }), 500)

    ##########################################################
    #
    # Goals
    #
    ##########################################################

    @app.route('/api/reset-goals', methods=['DELETE'])
    def reset_goals() -> Response:
        """Recreate the goals table to delete goals.

        Returns:
            JSON response indicating the success of recreating the goals table.

        Raises:
            500 error if there is an issue recreating the goals table.
        """
        try:
            app.logger.info("Received request to recreate goals table")
            with app.app_context():
                Goals.__table__.drop(db.engine)
                Goals.__table__.create(db.engine)
            app.logger.info("Goals table recreated successfully")
            return make_response(jsonify({
                "status": "success",
                "message": f"Goals table recreated successfully"
            }), 200)

        except Exception as e:
            app.logger.error(f"Goals table recreation failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting users",
                "details": str(e)
            }), 500)


    @app.route('/api/create-goal', methods=['POST'])
    @login_required
    def add_goal() -> Response:
        """Route to add a new goal to the catalog. TODO is catalog right word?

        Expected JSON Input:
            - target (str): The goal's target muscle group.

        Returns:
            JSON response indicating the success of the goal addition.

        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the goal to the plan.

        """
        app.logger.info("Received request to add a new goal")

        try:
            data = request.get_json()

            required_fields = ["target"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required fields: {missing_fields}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400)

            target = data["target"]

            if (
                not isinstance(target, str)
            ):
                app.logger.warning("Invalid input data types")
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid input types: target should be a string"
                }), 400)

            app.logger.info(f"Adding goal: {target}")
            Goals.create_goal(target=target)

            app.logger.info(f"goal added successfully: {target}")
            return make_response(jsonify({
                "status": "success",
                "message": f"goal with target: '{target}' added successfully"
            }), 201)

        except Exception as e:
            app.logger.error(f"Failed to add goal: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while adding the goal",
                "details": str(e)
            }), 500)


    @app.route('/api/delete-goal/<int:goal_id>', methods=['DELETE'])
    @login_required
    def delete_goal(goal_id: int) -> Response:
        """Route to delete a goal by ID.

        Path Parameter:
            - goal_id (int): The ID of the goal to delete.

        Returns:
            JSON response indicating success of the operation.

        Raises:
            400 error if the goal does not exist.
            500 error if there is an issue removing the goal from the database.

        """
        try:
            app.logger.info(f"Received request to delete goal with ID {goal_id}")

            # Check if the goal exists before attempting to delete
            goal = Goals.get_goal_by_id(goal_id)
            if not goal:
                app.logger.warning(f"goal with ID {goal_id} not found.")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"goal with ID {goal_id} not found"
                }), 400)

            Goals.delete_goal(goal_id)
            app.logger.info(f"Successfully deleted goal with ID {goal_id}")

            return make_response(jsonify({
                "status": "success",
                "message": f"goal with ID {goal_id} deleted successfully"
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to delete goal: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while deleting the goal",
                "details": str(e)
            }), 500)


    @app.route('/api/get-all-goals-from-catalog', methods=['GET'])
    @login_required
    def get_all_goals() -> Response:
        """Route to retrieve all goals in the catalog (non-deleted), with an option to sort by target.

        TODO Query Parameter:
            - sort_by_target (bool, optional): If true, sort goals by play target.

        Returns:
            JSON response containing the list of goals.

        Raises:
            500 error if there is an issue retrieving goals from the catalog.

        """
        try:
            # Extract query parameter for sorting by play count
            sort_by_target = request.args.get('sort_by_target', 'false').lower() == 'true'

            app.logger.info(f"Received request to retrieve all goals from catalog (sort_by_target={sort_by_target})")

            goals = Goals.get_all_goals(sort_by_targett=sort_by_target)

            app.logger.info(f"Successfully retrieved {len(goals)} goals from the catalog")

            return make_response(jsonify({
                "status": "success",
                "message": "goals retrieved successfully",
                "goals": goals
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve goals: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving goals",
                "details": str(e)
            }), 500)


    @app.route('/api/get-goal-from-catalog-by-id/<int:goal_id>', methods=['GET'])
    @login_required
    def get_goal_by_id(goal_id: int) -> Response:
        """Route to retrieve a goal by its ID.

        Path Parameter:
            - goal_id (int): The ID of the goal.

        Returns:
            JSON response containing the goal details.

        Raises:
            400 error if the goal does not exist.
            500 error if there is an issue retrieving the goal.

        """
        try:
            app.logger.info(f"Received request to retrieve goal with ID {goal_id}")

            goal = Goals.get_goal_by_id(goal_id)
            if not goal:
                app.logger.warning(f"Goal with ID {goal_id} not found.")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Goal with ID {goal_id} not found"
                }), 400)

            app.logger.info(f"Successfully retrieved goal with target {goal.target}")

            return make_response(jsonify({
                "status": "success",
                "message": "goal retrieved successfully",
                "goal": goal
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve goal by ID: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the goal",
                "details": str(e)
            }), 500)


    # @app.route('/api/get-goal-from-catalog-by-compound-key', methods=['GET']) TODO by target? but thats above so we should be fine
    # @login_required
    # def get_goal_by_compound_key() -> Response:
    #     """Route to retrieve a goal by its compound key (artist, title, year).

    #     Query Parameters:
    #         - artist (str): The artist's name.
    #         - title (str): The goal title.
    #         - year (int): The year the goal was released.

    #     Returns:
    #         JSON response containing the goal details.

    #     Raises:
    #         400 error if required query parameters are missing or invalid.
    #         500 error if there is an issue retrieving the goal.

    #     """
    #     try:
    #         artist = request.args.get('artist')
    #         title = request.args.get('title')
    #         year = request.args.get('year')

    #         if not artist or not title or not year:
    #             app.logger.warning("Missing required query parameters: artist, title, year")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": "Missing required query parameters: artist, title, year"
    #             }), 400)

    #         try:
    #             year = int(year)
    #         except ValueError:
    #             app.logger.warning(f"Invalid year format: {year}. Year must be an integer.")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": "Year must be an integer"
    #             }), 400)

    #         app.logger.info(f"Received request to retrieve goal by compound key: {artist}, {title}, {year}")

    #         goal = goals.get_goal_by_compound_key(artist, title, year)
    #         if not goal:
    #             app.logger.warning(f"goal not found: {artist} - {title} ({year})")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": f"goal not found: {artist} - {title} ({year})"
    #             }), 400)

    #         app.logger.info(f"Successfully retrieved goal: {goal.title} by {goal.artist} ({year})")

    #         return make_response(jsonify({
    #             "status": "success",
    #             "message": "goal retrieved successfully",
    #             "goal": goal
    #         }), 200)

    #     except Exception as e:
    #         app.logger.error(f"Failed to retrieve goal by compound key: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while retrieving the goal",
    #             "details": str(e)
    #         }), 500)


    # @app.route('/api/get-random-goal', methods=['GET']) TODO do we need this? probably not
    # @login_required
    # def get_random_goal() -> Response:
    #     """Route to retrieve a random goal from the catalog.

    #     Returns:
    #         JSON response containing the details of a random goal.

    #     Raises:
    #         400 error if no goals exist in the catalog.
    #         500 error if there is an issue retrieving the goal

    #     """
    #     try:
    #         app.logger.info("Received request to retrieve a random goal from the catalog")

    #         goal = goals.get_random_goal()
    #         if not goal:
    #             app.logger.warning("No goals found in the catalog.")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": "No goals available in the catalog"
    #             }), 400)

    #         app.logger.info(f"Successfully retrieved random goal: {goal.title} by {goal.artist}")

    #         return make_response(jsonify({
    #             "status": "success",
    #             "message": "Random goal retrieved successfully",
    #             "goal": goal
    #         }), 200)

        # except Exception as e:
        #     app.logger.error(f"Failed to retrieve random goal: {e}")
        #     return make_response(jsonify({
        #         "status": "error",
        #         "message": "An internal error occurred while retrieving a random goal",
        #         "details": str(e)
        #     }), 500)


    ############################################################
    #
    # Plan Add / Remove
    #
    ############################################################


    @app.route('/api/add-goal-to-plan', methods=['POST']) # TODO take a look at this because this uses the compound key. perhaps change to get goal by id instead of compound key
    @login_required
    def add_goal_to_plan() -> Response:
        """Route to add a goal to the plan by compound key (artist, title, year).

        Expected JSON Input:
            - target (str): The targets of the goal.

        Returns:
            JSON response indicating success of the addition.

        Raises:
            400 error if required fields are missing or the goal does not exist.
            500 error if there is an issue adding the goal to the plan.

        """
        try:
            app.logger.info("Received request to add goal to plan")

            data = request.get_json()
            required_fields = ["artist", "title", "year"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required fields: {missing_fields}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400)

            artist = data["artist"]
            title = data["title"]

            try:
                year = int(data["year"])
            except ValueError:
                app.logger.warning(f"Invalid year format: {data['year']}")
                return make_response(jsonify({
                    "status": "error",
                    "message": "Year must be a valid integer"
                }), 400)

            app.logger.info(f"Looking up goal: {artist} - {title} ({year})")
            goal = Goals.get_goal_by_compound_key(artist, title, year)

            if not goal:
                app.logger.warning(f"Goal not found: {artist} - {title} ({year})")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"goal '{title}' by {artist} ({year}) not found in catalog"
                }), 400)

            plan_model.add_goal_to_plan(goal)
            app.logger.info(f"Successfully added goal to plan: {artist} - {title} ({year})")

            return make_response(jsonify({
                "status": "success",
                "message": f"goal '{title}' by {artist} ({year}) added to plan"
            }), 201)

        except Exception as e:
            app.logger.error(f"Failed to add goal to plan: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while adding the goal to the plan",
                "details": str(e)
            }), 500)


    @app.route('/api/remove-goal-from-plan', methods=['DELETE']) # TODO compound key again
    @login_required
    def remove_goal_by_goal_id() -> Response:
        """Route to remove a goal from the plan by compound key (artist, title, year).

        Expected JSON Input:
            - artist (str): The artist's name.
            - title (str): The goal title.
            - year (int): The year the goal was released.

        Returns:
            JSON response indicating success of the removal.

        Raises:
            400 error if required fields are missing or the goal does not exist in the plan.
            500 error if there is an issue removing the goal.

        """
        try:
            app.logger.info("Received request to remove goal from plan")

            data = request.get_json()
            required_fields = ["artist", "title", "year"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required fields: {missing_fields}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400)

            artist = data["artist"]
            title = data["title"]

            try:
                year = int(data["year"])
            except ValueError:
                app.logger.warning(f"Invalid year format: {data['year']}")
                return make_response(jsonify({
                    "status": "error",
                    "message": "Year must be a valid integer"
                }), 400)

            app.logger.info(f"Looking up goal to remove: {artist} - {title} ({year})")
            goal = Goals.get_goal_by_compound_key(artist, title, year)

            if not goal:
                app.logger.warning(f"goal not found in catalog: {artist} - {title} ({year})")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"goal '{title}' by {artist} ({year}) not found in catalog"
                }), 400)

            plan_model.remove_goal_by_goal_id(goal.id)
            app.logger.info(f"Successfully removed goal from plan: {artist} - {title} ({year})")

            return make_response(jsonify({
                "status": "success",
                "message": f"goal '{title}' by {artist} ({year}) removed from plan"
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to remove goal from plan: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while removing the goal from the plan",
                "details": str(e)
            }), 500)


    # @app.route('/api/remove-goal-from-plan-by-track-number/<int:track_number>', methods=['DELETE'])
    # @login_required
    # def remove_goal_by_track_number(track_number: int) -> Response:
    #     """Route to remove a goal from the plan by track number.

    #     Path Parameter:
    #         - track_number (int): The track number of the goal to remove.

    #     Returns:
    #         JSON response indicating success of the removal.

    #     Raises:
    #         404 error if the track number does not exist.
    #         500 error if there is an issue removing the goal.

    #     """
    #     try:
    #         app.logger.info(f"Received request to remove goal at track number {track_number} from plan")

    #         plan_model.remove_goal_by_track_number(track_number)

    #         app.logger.info(f"Successfully removed goal at track number {track_number} from plan")
    #         return make_response(jsonify({
    #             "status": "success",
    #             "message": f"goal at track number {track_number} removed from plan"
    #         }), 200)

    #     except ValueError as e:
    #         app.logger.warning(f"Track number {track_number} not found in plan: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": f"Track number {track_number} not found in plan"
    #         }), 404)

    #     except Exception as e:
    #         app.logger.error(f"Failed to remove goal at track number {track_number}: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while removing the goal from the plan",
    #             "details": str(e)
    #         }), 500)


    @app.route('/api/clear-plan', methods=['POST'])
    @login_required
    def clear_plan() -> Response:
        """Route to clear all goals from the plan.

        Returns:
            JSON response indicating success of the operation.

        Raises:
            500 error if there is an issue clearing the plan.

        """
        try:
            app.logger.info("Received request to clear the plan")

            plan_model.clear_plan()

            app.logger.info("Successfully cleared the plan")
            return make_response(jsonify({
                "status": "success",
                "message": "plan cleared"
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to clear plan: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while clearing the plan",
                "details": str(e)
            }), 500)


    ############################################################
    #
    # Play plan
    #
    ############################################################


    # @app.route('/api/play-current-goal', methods=['POST'])
    # @login_required
    # def play_current_goal() -> Response:
    #     """Route to play the current goal in the plan.

    #     Returns:
    #         JSON response indicating success of the operation.

    #     Raises:
    #         404 error if there is no current goal.
    #         500 error if there is an issue playing the current goal.

    #     """
    #     try:
    #         app.logger.info("Received request to play the current goal")

    #         current_goal = plan_model.get_current_goal()
    #         if not current_goal:
    #             app.logger.warning("No current goal found in the plan")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": "No current goal found in the plan"
    #             }), 404)

    #         plan_model.play_current_goal()
    #         app.logger.info(f"Now playing: {current_goal.artist} - {current_goal.title} ({current_goal.year})")

    #         return make_response(jsonify({
    #             "status": "success",
    #             "message": "Now playing current goal",
    #             "goal": {
    #                 "id": current_goal.id,
    #                 "artist": current_goal.artist,
    #                 "title": current_goal.title,
    #                 "year": current_goal.year,
    #                 "genre": current_goal.genre,
    #                 "duration": current_goal.duration
    #             }
    #         }), 200)

    #     except Exception as e:
    #         app.logger.error(f"Failed to play current goal: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while playing the current goal",
    #             "details": str(e)
    #         }), 500)


    # @app.route('/api/play-entire-plan', methods=['POST'])
    # @login_required
    # def play_entire_plan() -> Response:
    #     """Route to play all goals in the plan.

    #     Returns:
    #         JSON response indicating success of the operation.

    #     Raises:
    #         400 error if the plan is empty.
    #         500 error if there is an issue playing the plan.

    #     """
    #     try:
    #         app.logger.info("Received request to play the entire plan")

    #         if plan_model.check_if_empty():
    #             app.logger.warning("Cannot play plan: No goals available")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": "Cannot play plan: No goals available"
    #             }), 400)

    #         plan_model.play_entire_plan()
    #         app.logger.info("Playing entire plan")

    #         return make_response(jsonify({
    #             "status": "success",
    #             "message": "Playing entire plan"
    #         }), 200)

    #     except Exception as e:
    #         app.logger.error(f"Failed to play entire plan: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while playing the plan",
    #             "details": str(e)
    #         }), 500)


    # @app.route('/api/play-rest-of-plan', methods=['POST'])
    # @login_required
    # def play_rest_of_plan() -> Response:
    #     """Route to play the rest of the plan from the current track.

    #     Returns:
    #         JSON response indicating success of the operation.

    #     Raises:
    #         400 error if the plan is empty or if no current goal is playing.
    #         500 error if there is an issue playing the rest of the plan.

    #     """
    #     try:
    #         app.logger.info("Received request to play the rest of the plan")

    #         if plan_model.check_if_empty():
    #             app.logger.warning("Cannot play rest of plan: No goals available")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": "Cannot play rest of plan: No goals available"
    #             }), 400)

    #         if not plan_model.get_current_goal():
    #             app.logger.warning("No current goal playing. Cannot continue plan.")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": "No current goal playing. Cannot continue plan."
    #             }), 400)

    #         plan_model.play_rest_of_plan()
    #         app.logger.info("Playing rest of the plan")

    #         return make_response(jsonify({
    #             "status": "success",
    #             "message": "Playing rest of the plan"
    #         }), 200)

    #     except Exception as e:
    #         app.logger.error(f"Failed to play rest of the plan: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while playing the rest of the plan",
    #             "details": str(e)
    #         }), 500)


    # @app.route('/api/rewind-plan', methods=['POST'])
    # @login_required
    # def rewind_plan() -> Response:
    #     """Route to rewind the plan to the first goal.

    #     Returns:
    #         JSON response indicating success of the operation.

    #     Raises:
    #         400 error if the plan is empty.
    #         500 error if there is an issue rewinding the plan.

    #     """
    #     try:
    #         app.logger.info("Received request to rewind the plan")

    #         if plan_model.check_if_empty():
    #             app.logger.warning("Cannot rewind: No goals in plan")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": "Cannot rewind: No goals in plan"
    #             }), 400)

    #         plan_model.rewind_plan()
    #         app.logger.info("plan successfully rewound to the first goal")

    #         return make_response(jsonify({
    #             "status": "success",
    #             "message": "plan rewound to the first goal"
    #         }), 200)

    #     except Exception as e:
    #         app.logger.error(f"Failed to rewind plan: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while rewinding the plan",
    #             "details": str(e)
    #         }), 500)


    # @app.route('/api/go-to-track-number/<int:track_number>', methods=['POST'])
    # @login_required
    # def go_to_track_number(track_number: int) -> Response:
    #     """Route to set the plan to start playing from a specific track number.

    #     Path Parameter:
    #         - track_number (int): The track number to set as the current goal.

    #     Returns:
    #         JSON response indicating success or an error message.

    #     Raises:
    #         400 error if the track number is invalid.
    #         500 error if there is an issue updating the track number.
    #     """
    #     try:
    #         app.logger.info(f"Received request to go to track number {track_number}")

    #         if not plan_model.is_valid_track_number(track_number):
    #             app.logger.warning(f"Invalid track number: {track_number}")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": f"Invalid track number: {track_number}. Please provide a valid track number."
    #             }), 400)

    #         plan_model.go_to_track_number(track_number)
    #         app.logger.info(f"plan set to track number {track_number}")

    #         return make_response(jsonify({
    #             "status": "success",
    #             "message": f"Now playing from track number {track_number}"
    #         }), 200)

    #     except ValueError as e:
    #         app.logger.warning(f"Failed to set track number {track_number}: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": str(e)
    #         }), 400)

    #     except Exception as e:
    #         app.logger.error(f"Internal error while going to track number {track_number}: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while changing the track number",
    #             "details": str(e)
    #         }), 500)


    # @app.route('/api/go-to-random-track', methods=['POST'])
    # @login_required
    # def go_to_random_track() -> Response:
    #     """Route to set the plan to start playing from a random track number.

    #     Returns:
    #         JSON response indicating success or an error message.

    #     Raises:
    #         400 error if the plan is empty.
    #         500 error if there is an issue selecting a random track.

    #     """
    #     try:
    #         app.logger.info("Received request to go to a random track")

    #         if plan_model.get_plan_length() == 0:
    #             app.logger.warning("Attempted to go to a random track but the plan is empty")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": "Cannot select a random track. The plan is empty."
    #             }), 400)

    #         plan_model.go_to_random_track()
    #         app.logger.info(f"plan set to random track number {plan_model.current_track_number}")

    #         return make_response(jsonify({
    #             "status": "success",
    #             "message": f"Now playing from random track number {plan_model.current_track_number}"
    #         }), 200)

    #     except Exception as e:
    #         app.logger.error(f"Internal error while selecting a random track: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while selecting a random track",
    #             "details": str(e)
    #         }), 500)


    ############################################################
    #
    # View plan
    #
    ############################################################


    @app.route('/api/get-all-goals-from-plan', methods=['GET'])
    @login_required
    def get_all_goals_from_plan() -> Response:
        """Retrieve all goals in the plan.

        Returns:
            JSON response containing the list of goals.

        Raises:
            500 error if there is an issue retrieving the plan.

        """
        try:
            app.logger.info("Received request to retrieve all goals from the plan.")

            goals = plan_model.get_all_goals()

            app.logger.info(f"Successfully retrieved {len(goals)} goals from the plan.")
            return make_response(jsonify({
                "status": "success",
                "goals": goals
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve goals from plan: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the plan",
                "details": str(e)
            }), 500)


    # @app.route('/api/get-goal-from-plan-by-track-number/<int:track_number>', methods=['GET'])
    # @login_required
    # def get_goal_by_track_number(track_number: int) -> Response:
    #     """Retrieve a goal from the plan by track number.

    #     Path Parameter:
    #         - track_number (int): The track number of the goal.

    #     Returns:
    #         JSON response containing goal details.

    #     Raises:
    #         404 error if the track number is not found.
    #         500 error if there is an issue retrieving the goal.

    #     """
    #     try:
    #         app.logger.info(f"Received request to retrieve goal at track number {track_number}.")

    #         goal = plan_model.get_goal_by_track_number(track_number)

    #         app.logger.info(f"Successfully retrieved goal: {goal.artist} - {goal.title} (Track {track_number}).")
    #         return make_response(jsonify({
    #             "status": "success",
    #             "goal": goal
    #         }), 200)

    #     except ValueError as e:
    #         app.logger.warning(f"Track number {track_number} not found: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": str(e)
    #         }), 404)

    #     except Exception as e:
    #         app.logger.error(f"Failed to retrieve goal by track number {track_number}: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while retrieving the goal",
    #             "details": str(e)
    #         }), 500)


    # @app.route('/api/get-current-goal', methods=['GET'])
    # @login_required
    # def get_current_goal() -> Response:
    #     """Retrieve the current goal being played.

    #     Returns:
    #         JSON response containing current goal details.

    #     Raises:
    #         500 error if there is an issue retrieving the current goal.

    #     """
    #     try:
    #         app.logger.info("Received request to retrieve the current goal.")

    #         current_goal = plan_model.get_current_goal()

    #         app.logger.info(f"Successfully retrieved current goal: {current_goal.artist} - {current_goal.title}.")
    #         return make_response(jsonify({
    #             "status": "success",
    #             "current_goal": current_goal
    #         }), 200)

    #     except Exception as e:
    #         app.logger.error(f"Failed to retrieve current goal: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while retrieving the current goal",
    #             "details": str(e)
    #         }), 500)


    # @app.route('/api/get-plan-length-duration', methods=['GET'])
    # @login_required
    # def get_plan_length_and_duration() -> Response:
    #     """Retrieve the length (number of goals) and total duration of the plan.

    #     Returns:
    #         JSON response containing the plan length and total duration.

    #     Raises:
    #         500 error if there is an issue retrieving plan information.

    #     """
    #     try:
    #         app.logger.info("Received request to retrieve plan length and duration.")

    #         plan_length = plan_model.get_plan_length()
    #         plan_duration = plan_model.get_plan_duration()

    #         app.logger.info(f"plan contains {plan_length} goals with a total duration of {plan_duration} seconds.")
    #         return make_response(jsonify({
    #             "status": "success",
    #             "plan_length": plan_length,
    #             "plan_duration": plan_duration
    #         }), 200)

    #     except Exception as e:
    #         app.logger.error(f"Failed to retrieve plan length and duration: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while retrieving plan details",
    #             "details": str(e)
    #         }), 500)


    ############################################################
    #
    # Arrange plan
    #
    ############################################################


    # @app.route('/api/move-goal-to-beginning', methods=['POST'])
    # @login_required
    # def move_goal_to_beginning() -> Response:
    #     """Move a goal to the beginning of the plan.

    #     Expected JSON Input:
    #         - artist (str): The artist of the goal.
    #         - title (str): The title of the goal.
    #         - year (int): The year the goal was released.

    #     Returns:
    #         Response: JSON response indicating success or an error message.

    #     Raises:
    #         400 error if required fields are missing.
    #         500 error if an error occurs while updating the plan.

    #     """
    #     try:
    #         data = request.get_json()

    #         required_fields = ["artist", "title", "year"]
    #         missing_fields = [field for field in required_fields if field not in data]

    #         if missing_fields:
    #             app.logger.warning(f"Missing required fields: {missing_fields}")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": f"Missing required fields: {', '.join(missing_fields)}"
    #             }), 400)

    #         artist, title, year = data["artist"], data["title"], data["year"]
    #         app.logger.info(f"Received request to move goal to beginning: {artist} - {title} ({year})")

    #         goal = goals.get_goal_by_compound_key(artist, title, year)
    #         plan_model.move_goal_to_beginning(goal.id)

    #         app.logger.info(f"Successfully moved goal to beginning: {artist} - {title} ({year})")
    #         return make_response(jsonify({
    #             "status": "success",
    #             "message": f"goal '{title}' by {artist} moved to beginning"
    #         }), 200)

    #     except Exception as e:
    #         app.logger.error(f"Failed to move goal to beginning: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while moving the goal",
    #             "details": str(e)
    #         }), 500)


    # @app.route('/api/move-goal-to-end', methods=['POST'])
    # @login_required
    # def move_goal_to_end() -> Response:
    #     """Move a goal to the end of the plan.

    #     Expected JSON Input:
    #         - artist (str): The artist of the goal.
    #         - title (str): The title of the goal.
    #         - year (int): The year the goal was released.

    #     Returns:
    #         Response: JSON response indicating success or an error message.

    #     Raises:
    #         400 error if required fields are missing.
    #         500 if an error occurs while updating the plan.

    #     """
    #     try:
    #         data = request.get_json()

    #         required_fields = ["artist", "title", "year"]
    #         missing_fields = [field for field in required_fields if field not in data]

    #         if missing_fields:
    #             app.logger.warning(f"Missing required fields: {missing_fields}")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": f"Missing required fields: {', '.join(missing_fields)}"
    #             }), 400)

    #         artist, title, year = data["artist"], data["title"], data["year"]
    #         app.logger.info(f"Received request to move goal to end: {artist} - {title} ({year})")

    #         goal = goals.get_goal_by_compound_key(artist, title, year)
    #         plan_model.move_goal_to_end(goal.id)

    #         app.logger.info(f"Successfully moved goal to end: {artist} - {title} ({year})")
    #         return make_response(jsonify({
    #             "status": "success",
    #             "message": f"goal '{title}' by {artist} moved to end"
    #         }), 200)

    #     except Exception as e:
    #         app.logger.error(f"Failed to move goal to end: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while moving the goal",
    #             "details": str(e)
    #         }), 500)


    # @app.route('/api/move-goal-to-track-number', methods=['POST'])
    # @login_required
    # def move_goal_to_track_number() -> Response:
    #     """Move a goal to a specific track number in the plan.

    #     Expected JSON Input:
    #         - artist (str): The artist of the goal.
    #         - title (str): The title of the goal.
    #         - year (int): The year the goal was released.
    #         - track_number (int): The new track number to move the goal to.

    #     Returns:
    #         Response: JSON response indicating success or an error message.

    #     Raises:
    #         400 error if required fields are missing.
    #         500 error if an error occurs while updating the plan.
    #     """
    #     try:
    #         data = request.get_json()

    #         required_fields = ["artist", "title", "year", "track_number"]
    #         missing_fields = [field for field in required_fields if field not in data]

    #         if missing_fields:
    #             app.logger.warning(f"Missing required fields: {missing_fields}")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": f"Missing required fields: {', '.join(missing_fields)}"
    #             }), 400)

    #         artist, title, year, track_number = data["artist"], data["title"], data["year"], data["track_number"]
    #         app.logger.info(f"Received request to move goal to track number {track_number}: {artist} - {title} ({year})")

    #         goal = goals.get_goal_by_compound_key(artist, title, year)
    #         plan_model.move_goal_to_track_number(goal.id, track_number)

    #         app.logger.info(f"Successfully moved goal to track {track_number}: {artist} - {title} ({year})")
    #         return make_response(jsonify({
    #             "status": "success",
    #             "message": f"goal '{title}' by {artist} moved to track {track_number}"
    #         }), 200)

    #     except Exception as e:
    #         app.logger.error(f"Failed to move goal to track number: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while moving the goal",
    #             "details": str(e)
    #         }), 500)


    # @app.route('/api/swap-goals-in-plan', methods=['POST'])
    # @login_required
    # def swap_goals_in_plan() -> Response:
    #     """Swap two goals in the plan by their track numbers.

    #     Expected JSON Input:
    #         - track_number_1 (int): The track number of the first goal.
    #         - track_number_2 (int): The track number of the second goal.

    #     Returns:
    #         Response: JSON response indicating success or an error message.

    #     Raises:
    #         400 error if required fields are missing.
    #         500 error if an error occurs while swapping goals in the plan.
    #     """
    #     try:
    #         data = request.get_json()

    #         required_fields = ["track_number_1", "track_number_2"]
    #         missing_fields = [field for field in required_fields if field not in data]

    #         if missing_fields:
    #             app.logger.warning(f"Missing required fields: {missing_fields}")
    #             return make_response(jsonify({
    #                 "status": "error",
    #                 "message": f"Missing required fields: {', '.join(missing_fields)}"
    #             }), 400)

    #         track_number_1, track_number_2 = data["track_number_1"], data["track_number_2"]
    #         app.logger.info(f"Received request to swap goals at track numbers {track_number_1} and {track_number_2}")

    #         goal_1 = plan_model.get_goal_by_track_number(track_number_1)
    #         goal_2 = plan_model.get_goal_by_track_number(track_number_2)
    #         plan_model.swap_goals_in_plan(goal_1.id, goal_2.id)

    #         app.logger.info(f"Successfully swapped goals: {goal_1.artist} - {goal_1.title} <-> {goal_2.artist} - {goal_2.title}")
    #         return make_response(jsonify({
    #             "status": "success",
    #             "message": f"Swapped goals: {goal_1.artist} - {goal_1.title} <-> {goal_2.artist} - {goal_2.title}"
    #         }), 200)

    #     except Exception as e:
    #         app.logger.error(f"Failed to swap goals in plan: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while swapping goals",
    #             "details": str(e)
    #         }), 500)



    ############################################################
    #
    # Leaderboard / Stats
    #
    ############################################################


    # @app.route('/api/goal-leaderboard', methods=['GET'])
    # def get_goal_leaderboard() -> Response:
    #     """
    #     Route to retrieve a leaderboard of goals sorted by play count.

    #     Returns:
    #         JSON response with a sorted leaderboard of goals.

    #     Raises:
    #         500 error if there is an issue generating the leaderboard.

    #     """
    #     try:
    #         app.logger.info("Received request to generate goal leaderboard")

    #         leaderboard_data = goals.get_all_goals(sort_by_play_count=True)

    #         app.logger.info(f"Successfully generated goal leaderboard with {len(leaderboard_data)} entries")
    #         return make_response(jsonify({
    #             "status": "success",
    #             "leaderboard": leaderboard_data
    #         }), 200)

    #     except Exception as e:
    #         app.logger.error(f"Failed to generate goal leaderboard: {e}")
    #         return make_response(jsonify({
    #             "status": "error",
    #             "message": "An internal error occurred while generating the leaderboard",
    #             "details": str(e)
    #         }), 500)

    # return app

if __name__ == '__main__':
    app = create_app()
    app.logger.info("Starting Flask app...")
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")
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

    @app.route('/api/login', methods=['POST']) #
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
        """Route to create a new goal.

        Expected JSON Input:
            - target (str): The goal's target muscle group.
            - goal_value (int): The goal's target to reach.
            - goal_progress (float, int): The current progress towards the goal.
            - completed (bool): Boolean for if the goal is completed.

        Returns:
            JSON response indicating the success of the goal addition.

        Raises:
            400 error if input validation fails.
            500 error if there is an issue adding the goal to the plan.

        """
        app.logger.info("Received request to add a new goal")

        try:
            data = request.get_json()

            required_fields = ["target", "goal_value", "goal_progress", "completed"]
            missing_fields = [field for field in required_fields if field not in data]

            if missing_fields:
                app.logger.warning(f"Missing required fields: {missing_fields}")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"Missing required fields: {', '.join(missing_fields)}"
                }), 400)

            target = data["target"]
            goal_value = data["goal_value"]
            goal_progress = data["goal_progress"]
            completed = data["completed"]

            if (
                not isinstance(target, str)
            ):
                app.logger.warning("Invalid input data types - target")
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid input types: target should be a string"
                }), 400)
            
            if (
                not isinstance(goal_value, int)
            ):
                app.logger.warning("Invalid input data types - goal_value")
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid input types: goal_value should be an int"
                }), 400)
            
            if (
                not isinstance(goal_progress, (float))
            ):
                app.logger.warning("Invalid input data types - goal_progress")
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid input types: goal_progress should be a float or an int"
                }), 400)
            
            if (
                not isinstance(completed, bool)
            ):
                app.logger.warning("Invalid input data types - completed")
                return make_response(jsonify({
                    "status": "error",
                    "message": "Invalid input types: completed should be a bool"
                }), 400)

            app.logger.info(f"Adding goal: {target}, {goal_value}, {goal_progress}, completed = {completed}")
            Goals.create_goal(target=target, goal_value=goal_value, goal_progress=goal_progress, completed=completed)

            app.logger.info(f"goal added successfully: {target}, {goal_value}, {goal_progress}, completed = {completed}")
            return make_response(jsonify({
                "status": "success",
                "message": f"goal with target: '{target}', goal_value: '{goal_value}' added successfully"
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
                app.logger.warning(f"Goal with ID {goal_id} not found.")
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

        Returns:
            JSON response containing the list of goals.

        Raises:
            500 error if there is an issue retrieving goals from the catalog.

        """
        try:
            # Extract query parameter for sorting by play count
            app.logger.info(f"Received request to retrieve all goals from catalog")

            goals = Goals.get_all_goals()

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
                "message": "Goal retrieved successfully",
                "target": goal.target
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve goal by ID: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the goal",
                "details": str(e)
            }), 500)

    @app.route('/api/goals/by-target/<string:target>', methods=['GET'])
    @login_required
    def get_goals_by_target(target: str) -> Response:
        """Route to retrieve all goals by target.

        Path Parameter:
            - target (str): The target muscle group.

        Returns:
            JSON response with a list of goals that match the target.

        Raises:
            400 error if no matching goals are found.
            500 error if there is an issue retrieving the goals.
        """
        try:
            app.logger.info(f"Request to retrieve goals by target: {target}")
            goals = Goals.get_goals_by_target(target)
            return make_response(jsonify({
                "status": "success",
                "goals": [g.id for g in goals] 
            }), 200)
        except ValueError as e:
            app.logger.warning(f"Goal retrieval failed: {e}")
            return make_response(jsonify({
                "status": "error",
                  "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"Internal error retrieving goals by target: {e}")
            return make_response(jsonify({
                "status": "error", 
                "message": "Internal server error"
            }), 500)

    @app.route('/api/goals/by-completed/<string:completed>', methods=['GET'])
    @login_required
    def get_goals_by_completed(completed: str) -> Response:
        """Route to retrieve all goals by completion status.

        Path Parameter:
            - completed (str): Either 'true' or 'false'.

        Returns:
            JSON response with a list of matching goals.

        Raises:
            400 error for invalid boolean input or missing data.
            500 error for unexpected database issues.
        """
        try:
            app.logger.info(f"Request to retrieve goals by completion status: {completed}")
            status = completed.lower() == 'true'
            goals = Goals.get_goals_by_completed(status)
            return make_response(jsonify({
                "status": "success",
                "goals": [g.id for g in goals]
            }), 200)
        except ValueError as e:
            app.logger.warning(f"Goal retrieval failed: {e}")
            return make_response(jsonify({"status": "error", "message": str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Internal error retrieving completed goals: {e}")
            return make_response(jsonify({"status": "error", "message": "Internal server error"}), 500)

    @app.route('/api/goals/by-value/<int:goal_value>', methods=['GET'])
    @login_required
    def get_goals_by_goal_value(goal_value: int) -> Response:
        """Route to retrieve all goals by goal value.

        Path Parameter:
            - goal_value (int): The numeric goal value to filter by.

        Returns:
            JSON response with matching goals.

        Raises:
            400 error if no goals are found.
            500 error if database issues occur.
        """
        try:
            app.logger.info(f"Request to retrieve goals by goal value: {goal_value}")
            goals = Goals.get_goals_by_goal_value(goal_value)
            return make_response(jsonify({
                "status": "success",
                "goals": [g.id for g in goals]
            }), 200)
        except ValueError as e:
            app.logger.warning(f"Goal retrieval failed: {e}")
            return make_response(jsonify({"status": "error", "message": str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Error retrieving goals by goal value: {e}")
            return make_response(jsonify({"status": "error", "message": "Internal server error"}), 500)

    @app.route('/api/update-goal/<int:goal_id>', methods=['PATCH']) 
    @login_required
    def update_goal(goal_id: int) -> Response:
        """Route to update a goal by ID.

        Path Parameter:
            - goal_id (int): The ID of the goal to update.

        Expected JSON Input:
            - target (str): Updated target.
            - goal_value (int): Updated goal value.
            - goal_progress (float): Updated progress.
            - completed (bool): Updated completion status.

        Returns:
            JSON response with the updated goal or error.

        Raises:
            400 error for invalid input or if goal not found.
            500 error for database issues.
        """
        try:
            data = request.get_json()
            goal = Goals.get_goal_by_id(goal_id)

            new_target = data.get("target")
            new_goal_value = data.get("goal_value")
            new_goal_progress = data.get("goal_progress")
            new_completed = data.get("completed")

            old_fields = [goal.target, goal.goal_value, goal.goal_progress, goal.completed]
            new_fields = [new_target, new_goal_value, new_goal_progress, new_completed]
            updated_fields = []

            for i in range(len(old_fields)):
                if old_fields[i] != new_fields[i]:
                    updated_fields.append(new_fields[i])

            updated_goal = Goals.update_goal(
                goal_id,
                target=new_target,
                goal_value=new_goal_value,
                goal_progress=new_goal_progress,
                completed=new_completed
            )
            app.logger.info(f"Updated goal ID {goal_id} successfully.")
            return make_response(jsonify({
                "status": "success", 
                "goal": updated_goal.id,
                "updated_fields": updated_fields
            }), 200)
        except ValueError as e:
            app.logger.warning(f"Update failed for goal {goal_id}: {e}")
            return make_response(jsonify({
                "status": "error", 
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"Internal error updating goal {goal_id}: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal server error"
            }), 500)

    @app.route('/api/delete-goal-by-target/<string:target>', methods=['DELETE'])
    @login_required
    def delete_goal_by_target(target: str) -> Response:
        """Route to delete a goal by target.

        Path Parameter:
            - target (str): The goal's target field.

        Returns:
            JSON response on successful deletion.

        Raises:
            400 error if goal is not found.
            500 error on DB issues.
        """
        try:
            Goals.delete_goal_by_target(target)
            app.logger.info(f"Deleted goal with target {target}.")
            return make_response(jsonify({"status": "success", "message": f"Goal with target '{target}' deleted."}), 200)
        except ValueError as e:
            app.logger.warning(f"Goal delete failed for target {target}: {e}")
            return make_response(jsonify({"status": "error", "message": str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Internal error deleting goal by target {target}: {e}")
            return make_response(jsonify({"status": "error", "message": "Internal server error"}), 500)


    @app.route('/api/delete-goal-by-value/<int:goal_value>', methods=['DELETE'])
    @login_required
    def delete_goal_by_value(goal_value: int) -> Response:
        """Route to delete a goal by goal value.

        Path Parameter:
            - goal_value (int): The value set for the goal.

        Returns:
            JSON response on successful deletion.

        Raises:
            400 error if goal is not found.
            500 error on DB issues.
        """
        try:
            Goals.delete_goal_by_goal_value(goal_value)
            app.logger.info(f"Deleted goal with value {goal_value}.")
            return make_response(jsonify({"status": "success", "message": f"Goal with value {goal_value} deleted."}), 200)
        except ValueError as e:
            app.logger.warning(f"Goal delete failed for value {goal_value}: {e}")
            return make_response(jsonify({"status": "error", "message": str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Internal error deleting goal by value {goal_value}: {e}")
            return make_response(jsonify({"status": "error", "message": "Internal server error"}), 500)


    @app.route('/api/delete-goal-by-completed/<completed>', methods=['DELETE'])
    @login_required
    def delete_goal_by_completed(completed: str) -> Response:
        """Route to delete a goal by completed status.

        Path Parameter:
            - completed (str): 'true' or 'false'.

        Returns:
            JSON response on successful deletion.

        Raises:
            400 error if goal is not found.
            500 error on DB issues.
        """
        try:
            status = completed.lower() == 'true'
            Goals.delete_goal_by_completed(status)
            app.logger.info(f"Deleted goal with completed status {status}.")
            return make_response(jsonify({"status": "success", "message": f"Goal with completed={status} deleted."}), 200)
        except ValueError as e:
            app.logger.warning(f"Delete by completed failed: {e}")
            return make_response(jsonify({"status": "error", "message": str(e)}), 400)
        except Exception as e:
            app.logger.error(f"Error deleting goal by completed: {e}")
            return make_response(jsonify({"status": "error", "message": "Internal server error"}), 500)


    @app.route('/api/goals/recommendations/<int:goal_id>', methods=['GET'])
    @login_required
    def get_exercise_recommendations(goal_id: int) -> Response:
        """Route to get exercise recommendations for a goal.

        Path Parameter:
            - goal_id (int): The ID of the goal.

        Returns:
            JSON list of recommended exercises.

        Raises:
            400 if goal not found.
            500 on external API or DB failure.
        """
        try:
            recommendations = Goals.get_exercise_recommendations(goal_id)
            app.logger.info(f"Retrieved exercise recommendations for goal {goal_id}. {recommendations}")
            return make_response(jsonify({
                "status": "success",
                "recommendations": recommendations
            }), 200)
        except ValueError as e:
            app.logger.warning(f"Recommendation fetch failed: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"Internal error getting recommendations: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal server error"
            }), 500)


    @app.route('/api/goals/log-session/<int:goal_id>', methods=['POST'])
    @login_required
    def log_workout(goal_id: int) -> Response:
        """Route to log a workout session for a goal.

        Path Parameter:
            - goal_id (int): The ID of the goal.

        Expected JSON Input:
            - amount (float): Progress amount.
            - exercise_type (str): Exercise name.
            - duration (int): Time in minutes.
            - intensity (str): Intensity level.
            - note (str, optional): Personal notes.

        Returns:
            JSON message with updated progress.

        Raises:
            400 if validation fails.
            500 on DB error.
        """
        try:
            data = request.get_json()
            goal = Goals.get_goal_by_id(goal_id)
            message = goal.log_workout_session(
                amount=data.get("amount"),
                exercise_type=data.get("exercise_type"),
                duration=data.get("duration"),
                intensity=data.get("intensity"),
                note=data.get("note", "")
            )
            app.logger.info(f"Workout logged for goal {goal_id}: {message}")
            return make_response(jsonify({
                "status": "success",
                "message": message
            }), 200)
        except ValueError as e:
            app.logger.warning(f"Workout log failed for goal {goal_id}: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": str(e)
            }), 400)
        except Exception as e:
            app.logger.error(f"Internal error logging workout for goal {goal_id}: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "Internal server error"
            }), 500)


    ############################################################
    #
    # Plan Add / Remove
    #
    ############################################################


    @app.route('/api/add-goal-to-plan/<int:goal_id>', methods=['POST'])
    @login_required
    def add_goal_to_plan(goal_id: int) -> Response:
        """Route to add a goal to the plan by goal_id.

        Path Parameter:
            - goal_id (int): The ID of the goal.

        Returns:
            JSON response indicating success of the addition.

        Raises:
            400 error if required fields are missing or the goal does not exist.
            500 error if there is an issue adding the goal to the plan.

        """
        try:
            app.logger.info("Received request to add goal to plan")

            app.logger.info(f"Looking up goal with id {goal_id}")
            goal = Goals.get_goal_by_id(goal_id=goal_id)

            if not goal:
                app.logger.warning(f"Goal not found")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"goal not found in catalog"
                }), 400)

            plan_model.add_goal_to_plan(goal_id)
            app.logger.info(f"Successfully added goal to plan: {goal.target} - {goal.goal_progress} out of {goal.goal_value}")

            return make_response(jsonify({
                "status": "success",
                "message": f"goal {goal.target} - {goal.goal_progress} out of {goal.goal_value} added to plan"
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to add goal to plan: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while adding the goal to the plan",
                "details": str(e)
            }), 500)


    @app.route('/api/remove-goal-from-plan/<int:goal_id>', methods=['DELETE'])
    @login_required
    def remove_goal_by_goal_id(goal_id:int) -> Response:
        """Route to remove a goal from the plan by goal_id.

        Path Parameter:
            - goal_id (int): The ID of the goal.

        Returns:
            JSON response indicating success of the removal.

        Raises:
            400 error if required fields are missing or the goal does not exist in the plan.
            500 error if there is an issue removing the goal.

        """
        try:
            app.logger.info("Received request to remove goal from plan")

            app.logger.info(f"Looking up goal to remove: id - {goal_id}")
            goal = Goals.get_goal_by_id(goal_id)

            if not goal:
                app.logger.warning(f"goal with id {goal_id} not found in catalog")
                return make_response(jsonify({
                    "status": "error",
                    "message": f"goal with id {goal_id} not found in catalog"
                }), 400)

            plan_model.remove_goal_by_goal_id(goal.id)
            app.logger.info(f"Successfully removed goal with id {goal_id} from plan")

            return make_response(jsonify({
                "status": "success",
                "message": f"Goal with id {goal_id} removed from plan"
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to remove goal from plan: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while removing the goal from the plan",
                "details": str(e)
            }), 500)


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
            goal_ids = [goal.id for goal in goals]

            app.logger.info(f"Successfully retrieved {len(goals)} goals from the plan.")
            return make_response(jsonify({
                "status": "success",
                "goals": goal_ids
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve goals from plan: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the plan",
                "details": str(e)
            }), 500)
        
    
    @app.route('/api/get-plan-progress', methods=['GET'])
    @login_required
    def get_plan_progress() -> Response:
        """Retrieve progress of goals in the plan.

        Returns:
            JSON response containing the percentage of goals completed.

        Raises:
            500 error if there is an issue retrieving progress.

        """
        try:
            app.logger.info("Received request to get progress of the plan.")

            percentage = plan_model.get_plan_progress()

            app.logger.info(f"Successfully retrieved percentage of goals completed in the plan.")
            return make_response(jsonify({
                "status": "success",
                "percentage": percentage
            }), 200)

        except Exception as e:
            app.logger.error(f"Failed to retrieve goals from plan: {e}")
            return make_response(jsonify({
                "status": "error",
                "message": "An internal error occurred while retrieving the plan",
                "details": str(e)
            }), 500)

    return app

if __name__ == '__main__':
    app = create_app()
    app.logger.info("Starting Flask app...")
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        app.logger.error(f"Flask app encountered an error: {e}")
    finally:
        app.logger.info("Flask app has stopped.")
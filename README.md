# Coach-Peter
Coach Peter is an app dedicated to tracking fitness goals and creating workout plans for users. Utilizing a user login system, Coach Peter allows users to set specific goals relating to their target, and they can log any workout notes, track their progress and view completion status too. Users are able to create new goals, update previous goals, and view any goal. Users can also create a plan with multiple goals that allows them to track a long-term workout plan. Coach Peter provides recommendation features based off previous workouts as well. 


Route Descriptions:

1. Route: /health
     - Request Type: GET
     - Purpose: Verifies the service is running by checking route
     - Request Body: No parameters required
     - Response Format: JSON
     - Success Response Example: 
         - Code: 200
         - Content: 
        ```
        {
            'status': 'success',
            'message': 'Service is running'
        }
        ```
     - Example cURL: curl -X GET http://localhost:5000/api/health
     - Example Response: 
    ```
    {
        'status': 'success',
        'message': 'Service is running'
    }
    ```


2. Route: /create-user
    - Request Type: PUT
    - Purpose: Registers a new user account
    - Request Body: 
    - username (String): User's chosen username. 
    - password (String): User's chosen password. 
    - Response Format: JSON
    - Success Response Example: 
        - Code: 201 
        - Content: 
        ```
        {
            'status": "success",
            "message": f"User '{username}' created successfully"
        }
        ```
    - Example Request: 
    ```
    {
        "username": "newuser123",
        "password": "securepassword"
    }
    ```
    - Example Response: 
    ```
    {
        "status": "success",
        "message": "User newuser123 created successfully”
    }
    ``` 


Route: /login
    Request Type: POST
    Purpose: Authenticates a user and logs them in
    Request Body: 
    username (String): User's chosen username. 
    password (String): User's chosen password. 
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status": "success",
            "message": f"User '{username}' logged in successfully"
        }
    Example Request: {
        "username": "newuser123",
        "password": "securepassword"
    }
    Example Response: {
        "status": "success",
        "message": "User newuser123 logged in successfully"
    } 


Route: /logout
    Request Type: POST
    Purpose: Logs out the current user
    Request Body: No parameters needed 
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status": "success",
            "message": "User logged out successfully"
        }
    Example Request: POST /api/logout
    Example Response: {
        "status": "success",
        "message": "User logged out successfully"
    } 


Route: /change-password
    Request Type: POST
    Purpose: Changes the password for the current user
    Request Body: 
    new_password (String): The new password to set
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status": "success",
            "message": “Password changed successfully"
        }
    Example Request: {
        "new_password”: “password123”
    }
    Example Response: {
        "status": "success",
        "message": "Password changed successfully"
    } 


Route: /reset-users
    Request Type: DELETE
    Purpose: Recreate the users table to delete all users
    Request Body: No parameters needed
    Response Format: DELETE /api/reset-users
    Success Response Example: 
        Code: 200
        Content: {
            'status": "success",
            "message": f"Users table recreated successfully"
        }
    Example Response: {
        "status": "success",
        "message": "Users table recreated successfully"
    } 


Route: /reset-goals
    Request Type: DELETE
    Purpose: Recreates the goals table to delete goals
    Request Body: No parameters needed
    Response Format: DELETE /api/reset-goals
    Success Response Example: 
        Code: 200
        Content: {
            'status": "success",
            "message": f"Goals table recreated successfully"
        }
    Example Response: {
        "status": "success",
        "message": "Goals table recreated successfully"
    } 


Route: /create-goal
    Request Type: POST
    Purpose: Route to create a new goal
    Request Body: 
    target (String): The goal's target muscle group.
    goal_value (int): The goal's target to reach.
    goal_progress (float, int): The current progress towards the goal.
    completed (bool): Boolean for if the goal is completed.
    Response Format: JSON
    Success Response Example: 
        Code: 201
        Content: {
            'status": "success",
            "message": f"goal with target: '{target}', goal_value: '{goal_value}' added successfully"
        }
    Example Request: {
        "target": "biceps",
        goal_value: 120,
        goal_progress: 50.0
        completed: False
    }
    Example Response: {
        'status": "success",
        "message": "goal with target: biceps, goal_value: 120 added successfully"
    } 


Route: /delete-goal
    Request Type: DELETE
    Purpose: Route to delete a goal by ID
    Request Body: 
    goal_id (int): The ID of the goal to delete 
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status": "success",
            "message": f"goal with ID {goal_id} deleted successfully"
        }
    Example Request: {
        goal_id: 120
    }
    Example Response: {
        "status": "success",
        "message": "goal with ID 120 deleted successfully"
    } 


Route: /get-all-goals-from-catalog
    Request Type: GET
    Purpose: Route to retrieve all goals in the catalog (non-deleted), with an option to sort by target
    Request Body: No parameters required
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status': 'success',
            'message': 'goals retrieved successfully'
            'goals': goals
        }
    Example cURL: curl -X GET http://localhost:5000/api/get-all-goals-from-catalog
    Example Response: {
        'status': 'success',
        'message': 'goals retrieved successfully'
        ‘goals’: goals
    }


Route: /get-goal-from-catalog-by-id
    Request Type: GET
    Purpose: Route to retrieve a goal by its ID
    Request Body: No parameters required
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status': 'success',
            'message': 'Goal retrieved successfully'
            ‘goal’: goal
        }
    Example cURL: curl -X GET http://localhost:5000/api/get-goal-from-catalog-by-id
    Example Response: {
        'status': 'success',
        'message': 'Goal retrieved successfully'
        ‘goal’: goal
    }


Route: /goals-by-target
    Request Type: GET
    Purpose: Route to retrieve all goals by target
    Request Body: No parameters required
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status': 'success',
            'goals': [g.id for g in goals]
        }
    Example cURL: curl -X GET http://localhost:5000/api/goals-by-target
    Example Response: {
        'status': 'success',
        'goals': [g.id for g in goals]
    }


Route: /goals-by-completed
    Request Type: GET
    Purpose: Route to retrieve all goals by completion status 
    Request Body: No parameters required
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status': 'success',
            'goals’: [g.id for g in goals]
        }
    Example cURL: curl -X GET http://localhost:5000/api/goals-by-completed
    Example Response: {
        'status': 'success',
        'goals’: [g.id for g in goals]
    }


Route: /goals-by-value
    Request Type: GET
    Purpose: Route to retrieve all goals by goal value
    Request Body: No parameters required
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status': 'success',
            'goals’: [g.id for g in goals]
        }
    Example cURL: curl -X GET http://localhost:5000/api/health
    Example Response: {
        'status': 'success',
        'Goals’: [g.id for g in goals]
    }




Route: /update-goal
    Request Type: PATCH
    Purpose: Route to update a goal by ID
    Request Body: 
    goal_id (int): The ID of the goal to update
    target (str): Updated target.
    goal_value (int): Updated goal value.
    goal_progress (float): Updated progress.
    completed (bool): Updated completion status.
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status": "success",
            "goal": updated_goal.id
        }
    Example Request: {
        goal_id: 10
        “target”: “biceps”
        goal_value: 120
        goal_progress: 50.0
        completed: False
    }
    Example Response: {
        "status": "success",
        "goal": 10
    } 


Route: /delete-goal-by-target
    Request Type: DELETE
    Purpose: Route to delete a goal by target
    Request Body: 
    target (String): The goal’s target field
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status": "success",
            "message": f“Goal with target ‘{target} deleted.’"
        }
    Example Request: {
        "target”: “biceps”
    }
    Example Response: {
        "status": "success",
        "message": "Goal with target biceps deleted."
    } 


Route: /delete-goal-by-value
    Request Type: DELETE
    Purpose: Route to delete a goal by goal value
    Request Body: 
    goal_value (int): The value set for the goal
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status": "success",
            "message": f“Goal with value ‘{goal_value} deleted.’"
        }
    Example Request: {
        “goal_value”: 120
    }
    Example Response: {
        "status": "success",
        "message": "Goal with value 120 deleted."
    }


Route: /delete-goal-by-completed
    Request Type: DELETE
    Purpose: Route to delete a goal by completion status
    Request Body: 
    completed (String): ‘true’ or ‘false’
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status": "success",
            "message": f“Goal with completed ‘{completed} deleted.’"
        }
    Example Request: {
        "completed”: True
    }
    Example Response: {
        "status": "success",
        "message": "Goal with completed true biceps deleted."
    }


Route: /goals/recommendations
    Request Type: GET
    Purpose: Route to get exercise recommendations for a goal
    Request Body: 
    goal_id (int): The ID of the goal.
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status': 'success',
            'recommendations’: recommendations
        }
    Example cURL: curl -X GET http://localhost:5000/api/goals/recommendations
    Example Response: {
        'status': 'success',
        'recommendations’: recommendations
    }


Route: /log-session
    Request Type: POST
    Purpose: Route to log a workout session for a goal
    Request Body: 
    goal_id (int): The ID of the goal
    amount (float): Progress amount.
    exercise_type (str): Exercise name.
    duration (int): Time in minutes.
    intensity (str): Intensity level.
    note (str, optional): Personal notes.
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status": "success",
            "message": message
        }
    Example Request: {
        “goal_id”: 1
        “amount”: 50.0
        “exercise_type”: “bench”
        “duration”: 15
        “intensity”: “Hardcore”
        “note”: “Light work, no reaction.”
    }
    Example Response: {
        "status": "success",
        "message": message
    } 


Route: /add-goal-to-plan
    Request Type: POST
    Purpose: Route to add a goal to plan
    Request Body: 
    target (String): The targets of the goal
    Response Format: JSON
    Success Response Example: 
        Code: 201
        Content: {
            'status": "success",
            "message": f“Successfully added goal to plan"
        }
    Example Request: {
        “Target”: “biceps”
    }
    Example Response: {
        "status": "success",
        "message": "Successfully added goal to plan"
    } 


Route: /clear-plan
    Request Type: POST
    Purpose: Route to clear all goals from the plan
    Request Body: No parameters needed
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status": "success",
            "message": “plan cleared"
        }
    Example Response: {
        "status": "success",
        "message": "plan cleared"
    } 


Route: /get-all-goals-from-plan
    Request Type: GET
    Purpose: Retrieve all goals in the plan
    Request Body: No parameters needed
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status': 'success',
            'goals’: goals
        }
    Example cURL: curl -X GET http://localhost:5000/api/get-all-goals-from-plan
    Example Response: {
        'status': 'success',
        'goal’: goals
    }


Route: /get-plan-progress
    Request Type: GET
    Purpose: Retrieve progress of goals in the plan
    Request Body: No parameters needed 
    Response Format: JSON
    Success Response Example: 
        Code: 200
        Content: {
            'status': 'success',
            'percentage’: percentage
        }
    Example cURL: curl -X GET http://localhost:5000/api/get-plan-progress
    Example Response: {
        'status': 'success',
        'percentage’: percentage
    }
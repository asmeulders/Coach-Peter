import pytest

from coach_peter.models.goal_model import Goals
from pytest_mock import MockerFixture

# --- Fixtures ---

@pytest.fixture
def goal_biceps(session): 
    """Fixture for a biceps goal."""
    goal = Goals(
           target="biceps", 
           goal_value=10, 
           goal_progress=2.0, 
           completed=False, 
           progress_notes='[]'
    )
    session.add(goal)
    session.commit()
    return goal

@pytest.fixture
def goal_pecs(session):
    """Fixture for a pecs goal."""
    goal = Goals(
        target="pectorals", 
        goal_value=15, 
        goal_progress=5.0, 
        completed=False, 
        progress_notes='[]'
        )

    session.add(goal)
    session.commit()
    return goal


# ################## TODO: change to goal ############
# @pytest.fixture
# def sample_goal(goal_biceps, goal_pecs): 
#     """Fixture for a sample plan."""
#     return [goal_biceps, goal_pecs]

# --- Create Goal ---

def test_create_goal(session):
    """Test creating a new goal."""
    Goals.create_goal("legs", 20, completed=False, goal_progress=0.0)
    goal = session.query(Goals).filter_by(target="legs").first()
    assert goal is not None
    assert goal.target == "legs"


#duplicate
    with pytest.raises(ValueError, match="already exists"):
        Goals.create_goal("legs", 20, False, 0.0)


@pytest.mark.parametrize("target, goal_value, goal_progress, completed", [
    ("", 10, 0.0, False),
    ("shoulders", None, 0.0, False),
    ("core", 20, "high", False),
    ("arms", 15, 2.0, "yes"),
])

def test_create_goal_invalid_data(target, goal_value, goal_progress, completed):
    """Test validation errors during goal creation."""
    with pytest.raises(ValueError):
        Goals.create_goal(target, goal_value, goal_progress, completed)


# --- Get Goal --- ADD MORE FOR ALL ###################################3

def test_get_goal_by_id(goal_biceps):
    """Test fetching a goal by ID."""
    fetched = Goals.get_goal_by_id(goal_biceps.id)
    assert fetched.target == "biceps"

def test_get_goal_by_id_not_found(app, session):
    """Test error when fetching nonexistent goal by ID."""
    with pytest.raises(ValueError, match="not found"):
        Goals.get_goal_by_id(999)

def test_get_goal_target(goal_biceps):
    """Test target field value of a goal."""
    fetched = Goals.get_goal_by_id(goal_biceps.id)
    assert fetched.target == "biceps"

def test_get_goal_by_target_not_found(app, session):
    """Test error when fetching nonexistent goal by target."""
    with pytest.raises(ValueError, match="No goals found with target 'nonexistent_target'"):
        Goals.get_goals_by_target("nonexistent_target")

def test_get_goal_value(goal_biceps):
    """Test goal_value field of a goal."""
    fetched = Goals.get_goal_by_id(goal_biceps.id)
    assert isinstance(fetched.goal_value, int)
    assert fetched.goal_value == goal_biceps.goal_value

def test_get_goal_by_goal_value_not_found(app, session):
    """Test error when fetching nonexistent goal by goal_value."""
    with pytest.raises(ValueError, match="No goals found with goal value '9999'"):
        Goals.get_goals_by_goal_value(9999)

def test_get_goal_completed(goal_biceps):
    """Test completed field of a goal."""
    fetched = Goals.get_goal_by_id(goal_biceps.id)
    assert isinstance(fetched.completed, bool)
    assert fetched.completed == goal_biceps.completed


# --- Delete Goal ---

def test_delete_goal_by_id(session, goal_pecs):
    """Test deleting a goal by ID."""
    Goals.delete_goal(goal_pecs.id)
    assert session.query(Goals).get(goal_pecs.id) is None

def test_delete_goal_not_found(app, session):
    """Test deleting a non-existent goal by ID."""
    with pytest.raises(ValueError, match="not found"):
        Goals.delete_goal(999)

def test_delete_goal_by_target(session, goal_biceps):
    """Test deleting a goal by target."""
    Goals.delete_goal_by_target(goal_biceps.target)
    deleted = session.query(Goals).filter_by(target=goal_biceps.target).first()
    assert deleted is None

def test_delete_goal_by_goal_value(session, goal_biceps):
    """Test deleting a goal by goal_value."""
    Goals.delete_goal_by_goal_value(goal_biceps.goal_value)
    deleted = session.query(Goals).filter_by(goal_value=goal_biceps.goal_value).first()
    assert deleted is None

def test_delete_goal_by_completed(session, goal_biceps):
    """Test deleting a goal by completed status."""
    Goals.delete_goal_by_completed(goal_biceps.completed)
    deleted = session.query(Goals).filter_by(completed=goal_biceps.completed).first()
    assert deleted is None



# --- Update ---
def test_update_goal(session, goal_biceps):
    """Test updating an existing goal."""
    updated = Goals.update_goal(goal_biceps.id, goal_value=20, completed=True)
    assert updated.goal_value == 20
    assert updated.completed is True


# --- Log Progress ---
def test_log_progress(session, goal_pecs):
    """Test logging progress toward a goal."""
    result = goal_pecs.log_progress(5.0)
    assert "Progress updated" in result or "Goal completed" in result
    session.refresh(goal_pecs)
    assert goal_pecs.goal_progress == 10.0

# --- Progress Notes ---

def test_add_progress_note(session, goal_biceps):
    """Test adding a progress note."""
    note = "Curls with dumbbells"
    goal_biceps.add_progress_note(note)
    session.commit()
    notes = goal_biceps.get_progress_notes()
    assert note in notes


# --- Recommendations ---

def test_get_exercise_recommendations(session, goal_biceps, mocker):
    """Test getting exercise recommendations for a goal."""
    mock_response = [
        {"name": "bicep curl", "equipment": "dumbbell"},
        {"name": "hammer curl", "equipment": "dumbbell"}
    ]

    mock_fetch = mocker.patch("coach_peter.models.goal_model.fetch_recommendation", return_value=mock_response)

    result = Goals.get_exercise_recommendations(goal_biceps.id)

    mock_fetch.assert_called_once_with("biceps")
    assert isinstance(result, list)
    assert result[0]["name"] == "bicep curl"


# --- Get All Goals ---

def test_get_all_goals(session, goal_biceps, goal_pecs):
    """Test retrieving all goals."""
    goals = Goals.get_all_goals()
    assert isinstance(goals, list)
    assert any(goal["target"] == "biceps" for goal in goals)



import pytest

from coach_peter.models.plan_model import PlanModel
from coach_peter.models.goal_model import Goals
from pytest_mock import MockerFixture


@pytest.fixture()
def plan_model():
    """Fixture to provide a new instance of PlanModel for each test."""
    return PlanModel()

"""Fixtures providing sample goals for the tests."""
@pytest.fixture
def goal_biceps(session):
    """Fixture for a biceps goal."""
    goal = Goals(
       target = "biceps",
       goal_value = 40,
       goal_progress = 35,
       completed = False,
       progress_notes='[]'
    )
    session.add(goal)
    session.commit()
    return goal

@pytest.fixture
def goal_pecs(session):
    """Fixture for a pecs goal."""
    goal = Goals(
        target = "pectorals",
        goal_value = 200,
        goal_progress = 225,
        completed = True,
        progress_notes='[]'
    )
    session.add(goal)
    session.commit()
    return goal

@pytest.fixture
def sample_plan(goal_biceps, goal_pecs):
    """Fixture for a sample plan."""
    return [goal_biceps.id, goal_pecs.id]

##################################################
# Add / Remove Goal Management Test Cases
##################################################


def test_add_goal_to_plan(plan_model, goal_biceps, mocker):
    """Test adding a goal to the plan."""
    mocker.patch("coach_peter.models.plan_model.Goals.get_goal_by_id", return_value=goal_biceps) # check return value
    plan_model.add_goal_to_plan(1)
    assert len(plan_model.plan) == 1
    assert plan_model.plan[0] == 1


def test_add_duplicate_goal_to_plan(plan_model, goal_biceps, mocker):
    """Test error when adding a duplicate goal to the plan by ID."""
    mocker.patch("coach_peter.models.plan_model.Goals.get_goal_by_id", side_effect=[goal_biceps] * 2) # check side effect
    plan_model.add_goal_to_plan(1)
    with pytest.raises(ValueError, match="Goal with ID 1 already exists in the plan"):
        plan_model.add_goal_to_plan(1)


def test_remove_goal_from_plan_by_goal_id(plan_model, mocker):
    """Test removing a goal from the plan by goal_id."""
    mocker.patch("coach_peter.models.plan_model.Goals.get_goal_by_id", return_value=goal_biceps) # check return value

    plan_model.plan = [1,2]

    plan_model.remove_goal_by_goal_id(1)
    assert len(plan_model.plan) == 1, f"Expected 1 goal, but got {len(plan_model.plan)}"
    assert plan_model.plan[0] == 2, "Expected goal with id 2 to remain"


def test_clear_plan(plan_model):
    """Test clearing the entire plan."""
    plan_model.plan.append(1)

    plan_model.clear_plan()
    assert len(plan_model.plan) == 0, "Plan should be empty after clearing"

##################################################
# Goal Retrieval Test Cases
##################################################

def test_get_all_goals(plan_model, sample_plan, mocker):
    """Test successfully retrieving all goals from the plan."""
    mocker.patch("coach_peter.models.plan_model.PlanModel._get_goal_from_cache_or_db", side_effect=sample_plan) # check side effect

    plan_model.plan.extend([1, 2])

    all_goals = plan_model.get_all_goals()

    assert len(all_goals) == 2
    assert all_goals[0] == 1
    assert all_goals[1] == 2


def test_get_goal_by_goal_id(plan_model, goal_biceps, mocker):
    """Test successfully retrieving a goal from the plan by goal ID."""
    mocker.patch("coach_peter.models.plan_model.Goals.get_goal_by_id", return_value=goal_biceps) # check return value
    plan_model.plan.append(1)

    retrieved_goal = plan_model.get_goal_by_goal_id(1)

    assert retrieved_goal.id == 1
    assert retrieved_goal.target == 'biceps'


def test_get_plan_length(plan_model):
    """Test getting the length of the plan."""
    plan_model.plan.extend([1, 2])
    assert plan_model.get_plan_length() == 2, "Expected plan length to be 2"


def test_get_plan_progress(plan_model, sample_plan):
    """Test getting the percent completed goals in a plan."""
    plan_model.plan.extend(sample_plan)
    percentage = plan_model.get_plan_progress()
    assert percentage == 0.500, "Expected plan progress to be 50% (0.500)"

##################################################
# Utility Function Test Cases
##################################################


def test_check_if_empty_non_empty_plan(plan_model):
    """Test check_if_empty does not raise error if plan is not empty."""
    plan_model.plan.append(1)
    try:
        plan_model.check_if_empty()
    except ValueError:
        pytest.fail("check_if_empty raised ValueError unexpectedly on non-empty plan")


def test_check_if_empty_empty_plan(plan_model):
    """Test check_if_empty raises error when plan is empty."""
    plan_model.clear_plan()
    with pytest.raises(ValueError, match="Plan is empty"):
        plan_model.check_if_empty()


def test_validate_goal_id(plan_model, mocker):
    """Test validate_goal_id does not raise error for valid goal ID."""
    mocker.patch("coach_peter.models.plan_model.PlanModel._get_goal_from_cache_or_db", return_value=True) # check return value

    plan_model.plan.append(1)
    try:
        plan_model.validate_goal_id(1)
    except ValueError:
        pytest.fail("validate_goal_id raised ValueError unexpectedly for valid goal ID")


def test_validate_goal_id_no_check_in_plan(plan_model, mocker): # what is this testing?
    """Test validate_goal_id does not raise error for valid goal ID when the id isn't in the plan."""
    mocker.patch("coach_peter.models.plan_model.PlanModel._get_goal_from_cache_or_db", return_value=True) # check return value
    try:
        plan_model.validate_goal_id(1, check_in_plan=False)
    except ValueError:
        pytest.fail("validate_goal_id raised ValueError unexpectedly for valid goal ID")


def test_validate_goal_id_invalid_id(plan_model): # same as above
    """Test validate_goal_id raises error for invalid goal ID."""
    with pytest.raises(ValueError, match="Invalid goal id: -1"):
        plan_model.validate_goal_id(-1)

    with pytest.raises(ValueError, match="Invalid goal id: invalid"):
        plan_model.validate_goal_id("invalid")


def test_validate_goal_id_not_in_plan(plan_model, goal_pecs, mocker): # same as above
    """Test validate_goal_id raises error for goal ID not in the plan."""
    mocker.patch("coach_peter.models.plan_model.Goals.get_goal_by_id", return_value=goal_pecs) # check return value
    plan_model.plan.append(1)
    with pytest.raises(ValueError, match="Goal with id 2 not found in plan"):
        plan_model.validate_goal_id(2)
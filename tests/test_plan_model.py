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
def goal_biceps(session): # change name
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
def goal_pecs(session):  # change name
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
def sample_plan(goal_biceps, goal_pecs): # make a sample playlist
    """Fixture for a sample plan."""
    return [goal_biceps, goal_pecs]

##################################################
# Add / Remove Goal Management Test Cases
##################################################


def test_add_goal_to_plan(plan_model, goal_biceps, mocker): # change goal
    """Test adding a goal to the plan."""
    mocker.patch("coach_peter.models.plan_model.Goals.get_goal_by_id", return_value=goal_biceps) # check return value
    plan_model.add_goal_to_plan(1)
    assert len(plan_model.plan) == 1
    assert plan_model.plan[0] == 1


def test_add_duplicate_goal_to_plan(plan_model, goal_biceps, mocker): # change goal
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


# def test_remove_goal_by_track_number(plan_model):
#     """Test removing a goal from the plan by track number."""
#     plan_model.plan = [1,2]
#     assert len(plan_model.plan) == 2

#     plan_model.remove_goal_by_track_number(1)
#     assert len(plan_model.plan) == 1, f"Expected 1 goal, but got {len(plan_model.plan)}"
#     assert plan_model.plan[0] == 2, "Expected goal with id 2 to remain"


def test_clear_plan(plan_model):
    """Test clearing the entire plan."""
    plan_model.plan.append(1)

    plan_model.clear_plan()
    assert len(plan_model.plan) == 0, "Plan should be empty after clearing"


# ##################################################
# # Tracklisting Management Test Cases
# ##################################################


# def test_move_goal_to_track_number(plan_model, sample_plan, mocker):
#     """Test moving a goal to a specific track number in the plan."""
#     mocker.patch("plan.models.plan_model.goals.get_goal_by_id", side_effect=sample_plan)

#     plan_model.plan.extend([1, 2])

#     plan_model.move_goal_to_track_number(2, 1)  # Move goal 2 to the first position
#     assert plan_model.plan[0] == 2, "Expected goal 2 to be in the first position"
#     assert plan_model.plan[1] == 1, "Expected goal 1 to be in the second position"


# def test_swap_goals_in_plan(plan_model, sample_plan, mocker):
#     """Test swapping the positions of two goals in the plan."""
#     mocker.patch("plan.models.plan_model.goals.get_goal_by_id", side_effect=sample_plan)

#     plan_model.plan.extend([1, 2])

#     plan_model.swap_goals_in_plan(1, 2)  # Swap positions of goal 1 and goal 2
#     assert plan_model.plan[0] == 2, "Expected goal 2 to be in the first position"
#     assert plan_model.plan[1] == 1, "Expected goal 1 to be in the second position"


# def test_swap_goal_with_itself(plan_model, goal_biceps, mocker):
#     """Test swapping the position of a goal with itself raises an error."""
#     mocker.patch("plan.models.plan_model.goals.get_goal_by_id", side_effect=[goal_biceps] * 2)
#     plan_model.plan.append(1)

#     with pytest.raises(ValueError, match="Cannot swap a goal with itself"):
#         plan_model.swap_goals_in_plan(1, 1)  # Swap positions of goal 1 with itself


# def test_move_goal_to_end(plan_model, sample_plan, mocker):
#     """Test moving a goal to the end of the plan."""
#     mocker.patch("plan.models.plan_model.goals.get_goal_by_id", side_effect=sample_plan)

#     plan_model.plan.extend([1, 2])

#     plan_model.move_goal_to_end(1)  # Move goal 1 to the end
#     assert plan_model.plan[1] == 1, "Expected goal 1 to be at the end"


# def test_move_goal_to_beginning(plan_model, sample_plan, mocker):
#     """Test moving a goal to the beginning of the plan."""
#     mocker.patch("plan.models.plan_model.goals.get_goal_by_id", side_effect=sample_plan)

#     plan_model.plan.extend([1, 2])

#     plan_model.move_goal_to_beginning(2)  # Move goal 2 to the beginning
#     assert plan_model.plan[0] == 2, "Expected goal 2 to be at the beginning"


##################################################
# goal Retrieval Test Cases
##################################################


# def test_get_goal_by_track_number(plan_model, goal_biceps, mocker):
#     """Test successfully retrieving a goal from the plan by track number."""
#     mocker.patch("plan.models.plan_model.goals.get_goal_by_id", return_value=goal_biceps)
#     plan_model.plan.append(1)

#     retrieved_goal = plan_model.get_goal_by_track_number(1)
#     assert retrieved_goal.id == 1
#     assert retrieved_goal.title == 'Come Together'
#     assert retrieved_goal.artist == 'The biceps'
#     assert retrieved_goal.year == 1969
#     assert retrieved_goal.duration == 259
#     assert retrieved_goal.genre == 'Rock'


def test_get_all_goals(plan_model, sample_plan, mocker):
    """Test successfully retrieving all goals from the plan."""
    mocker.patch("coach_peter.models.plan_model.PlanModel._get_goal_from_cache_or_db", side_effect=sample_plan) # check side effect

    plan_model.plan.extend([1, 2])

    all_goals = plan_model.get_all_goals()

    assert len(all_goals) == 2
    assert all_goals[0].id == 1
    assert all_goals[1].id == 2


def test_get_goal_by_goal_id(plan_model, goal_biceps, mocker): # change goal name
    """Test successfully retrieving a goal from the plan by goal ID."""
    mocker.patch("coach_peter.models.plan_model.Goals.get_goal_by_id", return_value=goal_biceps) # check return value
    plan_model.plan.append(1)

    retrieved_goal = plan_model.get_goal_by_goal_id(1)

    assert retrieved_goal.id == 1 # change assertions based on parameters of goal
    assert retrieved_goal.target == 'biceps'


# def test_get_current_goal(plan_model, goal_biceps, mocker):
#     """Test successfully retrieving the current goal from the plan."""
#     mocker.patch("plan.models.plan_model.goals.get_goal_by_id", return_value=goal_biceps)

#     plan_model.plan.append(1)

#     current_goal = plan_model.get_current_goal()
#     assert current_goal.id == 1
#     assert current_goal.title == 'Come Together'
#     assert current_goal.artist == 'The biceps'
#     assert current_goal.year == 1969
#     assert current_goal.duration == 259
#     assert current_goal.genre == 'Rock'


def test_get_plan_length(plan_model): # change to get number of goals?
    """Test getting the length of the plan."""
    plan_model.plan.extend([1, 2])
    assert plan_model.get_plan_length() == 2, "Expected plan length to be 2"


def test_get_plan_progress(plan_model, sample_plan):
    """Test getting the percent completed goals in a plan."""
    percentage = plan_model.get_plan_progress(sample_plan)
    assert percentage == 0.500, "Expected plan progress to be 50% (0.500)"


# def test_get_plan_duration(plan_model, sample_plan, mocker):
#     """Test getting the total duration of the plan."""
#     mocker.patch("plan.models.plan_model.planModel._get_goal_from_cache_or_db", side_effect=sample_plan)
#     plan_model.plan.extend([1, 2])
#     assert plan_model.get_plan_duration() == 560, "Expected plan duration to be 560 seconds"


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


# def test_validate_track_number(plan_model):
#     """Test validate_track_number does not raise error for valid track number."""
#     plan_model.plan.append(1)
#     try:
#         plan_model.validate_track_number(1)
#     except ValueError:
#         pytest.fail("validate_track_number raised ValueError unexpectedly for valid track number")

# @pytest.mark.parametrize("track_number, expected_error", [
#     (0, "Invalid track number: 0"),
#     (2, "Invalid track number: 2"),
#     ("invalid", "Invalid track number: invalid"),
# ])
# def test_validate_track_number_invalid(plan_model, track_number, expected_error):
#     """Test validate_track_number raises error for invalid track numbers."""
#     plan_model.plan.append(1)

#     with pytest.raises(ValueError, match=expected_error):
#         plan_model.validate_track_number(track_number)



##################################################
# Playback Test Cases
##################################################


# def test_play_current_goal(plan_model, sample_plan, mocker): # change to check progress?
#     """Test playing the current goal."""
#     mock_update_play_count = mocker.patch("plan.models.plan_model.goals.update_play_count")
#     mocker.patch("plan.models.plan_model.goals.get_goal_by_id", side_effect=sample_plan)

#     plan_model.plan.extend([1, 2])

#     plan_model.play_current_goal()

#     # Assert that CURRENT_TRACK_NUMBER has been updated to 2
#     assert plan_model.current_track_number == 2, f"Expected track number to be 2, but got {plan_model.current_track_number}"

#     # Assert that update_play_count was called with the id of the first goal
#     mock_update_play_count.assert_called_once_with()

#     # Get the second goal from the iterator (which will increment CURRENT_TRACK_NUMBER back to 1)
#     plan_model.play_current_goal()

#     # Assert that CURRENT_TRACK_NUMBER has been updated back to 1
#     assert plan_model.current_track_number == 1, f"Expected track number to be 1, but got {plan_model.current_track_number}"

#     # Assert that update_play_count was called with the id of the second goal
#     mock_update_play_count.assert_called_with()


# def test_rewind_plan(plan_model):
#     """Test rewinding the iterator to the beginning of the plan."""
#     plan_model.plan.extend([1, 2])
#     plan_model.current_track_number = 2

#     plan_model.rewind_plan()
#     assert plan_model.current_track_number == 1, "Expected to rewind to the first track"


# def test_go_to_track_number(plan_model):
#     """Test moving the iterator to a specific track number in the plan."""
#     plan_model.plan.extend([1, 2])

#     plan_model.go_to_track_number(2)
#     assert plan_model.current_track_number == 2, "Expected to be at track 2 after moving goal"


# def test_go_to_random_track(plan_model, mocker):
#     """Test that go_to_random_track sets a valid random track number."""
#     plan_model.plan.extend([1, 2])

#     mocker.patch("plan.models.plan_model.get_random", return_value=2)

#     plan_model.go_to_random_track()
#     assert plan_model.current_track_number == 2, "Current track number should be set to the random value"


# def test_play_entire_plan(plan_model, sample_plan, mocker):
#     """Test playing the entire plan."""
#     mock_update_play_count = mocker.patch("plan.models.plan_model.goals.update_play_count")
#     mocker.patch("plan.models.plan_model.planModel._get_goal_from_cache_or_db", side_effect=sample_plan)

#     plan_model.plan.extend([1,2])

#     plan_model.play_entire_plan()

#     # Check that all play counts were updated
#     mock_update_play_count.assert_any_call()
#     assert mock_update_play_count.call_count == len(plan_model.plan)

#     # Check that the current track number was updated back to the first goal
#     assert plan_model.current_track_number == 1, "Expected to loop back to the beginning of the plan"


# def test_play_rest_of_plan(plan_model, sample_plan, mocker):
#     """Test playing from the current position to the end of the plan.

#     """
#     mock_update_play_count = mocker.patch("plan.models.plan_model.goals.update_play_count")
#     mocker.patch("plan.models.plan_model.planModel._get_goal_from_cache_or_db", side_effect=sample_plan)

#     plan_model.plan.extend([1, 2])
#     plan_model.current_track_number = 2

#     plan_model.play_rest_of_plan()

#     # Check that play counts were updated for the remaining goals
#     mock_update_play_count.assert_any_call()
#     assert mock_update_play_count.call_count == 1

#     assert plan_model.current_track_number == 1, "Expected to loop back to the beginning of the plan"
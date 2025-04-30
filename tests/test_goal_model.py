import pytest

from coach_peter.models.goal_model import Goals
#may need to do something with mock because of api call

# --- Fixtures ---

@pytest.fixture
def goal_biceps(session): 
    """Fixture for a biceps goal."""
    goal = Goals(
       target = "biceps"
    )
    session.add(goal)
    session.commit()
    return goal

@pytest.fixture
def goal_pecs(session):  # change name
    """Fixture for a pecs goal."""
    goal = Goals(
        target = "pectorals"
    )
    session.add(goal)
    session.commit()
    return goal


################## TODO: change to goal ############
@pytest.fixture
def sample_goal(goal_biceps, goal_pecs): 
    """Fixture for a sample plan."""
    return [goal_biceps, goal_pecs]

# --- Create Goal ---

def test_create_goal(session):
    """Test creating a new goal."""
    Goals.create_goal("core")
    song = session.query(Goals).filter_by(target="core").first()
    assert goal is not None
    assert goal.artist == "Queen" #double check if this is necessary 


def test_create_duplicate_song(session, song_beatles):
    """Test creating a song with a duplicate artist/title/year."""
    with pytest.raises(ValueError, match="already exists"):
        Songs.create_song("The Beatles", "Hey Jude", 1968, "Rock", 431)


@pytest.mark.parametrize("artist, title, year, genre, duration", [
    ("", "Valid Title", 2000, "Pop", 180),
    ("Valid Artist", "", 2000, "Pop", 180),
    ("Valid Artist", "Valid Title", 1899, "Pop", 180),
    ("Valid Artist", "Valid Title", 2000, "", 180),
    ("Valid Artist", "Valid Title", 2000, "Pop", 0),
])

def test_create_song_invalid_data(artist, title, year, genre, duration):
    """Test validation errors when creating a song."""
    with pytest.raises(ValueError):
        Songs.create_song(artist, title, year, genre, duration)


# --- Get Song ---

def test_get_song_by_id(song_beatles):
    """Test fetching a song by ID."""
    fetched = Songs.get_song_by_id(song_beatles.id)
    assert fetched.title == "Hey Jude"

def test_get_song_by_id_not_found(app):
    """Test error when fetching nonexistent song by ID."""
    with pytest.raises(ValueError, match="not found"):
        Songs.get_song_by_id(999)


# --- Delete Song ---

def test_delete_goal_by_id(session, goal_biceps):
    """Test deleting a goal by ID."""
    Goals.delete_goal(goal_biceps.id)
    assert session.query(Goals).get(goal_biceps.id) is None

# delete by target 
def test_delete_goal_by_target(session, goal_biceps):
    """Test deleting a goal by target."""
    Goals.delete_goal(goal_biceps.target)
    assert session.query(Goals).get(goal_biceps.target) is None

def test_delete_goal_not_found(app):
    """Test deleting a non-existent goal by ID."""
    with pytest.raises(ValueError, match="not found"):
        Goals.delete_goal(999)


# --- Play Count ---

# def test_update_play_count(session, song_nirvana):
#     """Test incrementing play count."""
#     assert song_nirvana.play_count == 0
#     song_nirvana.update_play_count()
#     session.refresh(song_nirvana)
#     assert song_nirvana.play_count == 1


# --- Get All Songs ---

def test_get_all_songs(session, song_beatles, song_nirvana):
    """Test retrieving all songs."""
    songs = Songs.get_all_songs()
    assert len(songs) == 2

# def test_get_all_songs_sorted(session, song_beatles, song_nirvana):
#     """Test retrieving songs sorted by play count."""
#     song_nirvana.play_count = 5
#     song_beatles.play_count = 3
#     session.commit()
#     sorted_songs = Songs.get_all_songs(sort_by_play_count=True)
#     assert sorted_songs[0]["title"] == "Smells Like Teen Spirit"


# --- Random Song ---

def test_get_random_song(session, song_beatles, song_nirvana):
    """Test getting a random song as a dictionary with expected fields."""
    song = Songs.get_random_song()

    assert isinstance(song, dict), "Expected a dictionary representing a song"
    assert set(song.keys()) == {"id", "artist", "title", "year", "genre", "duration", "play_count"}, \
        f"Unexpected keys in song dict: {song.keys()}"
    assert isinstance(song["title"], str) and song["title"], "Song title should be a non-empty string"
    assert isinstance(song["play_count"], int), "Play count should be an integer"


def test_get_random_song_empty(session):
    """Test error when no songs exist."""
    Songs.query.delete()
    session.commit()
    with pytest.raises(ValueError, match="empty"):
        Songs.get_random_song()

import pytest

from codemash_mcp import helpers

VENUE_1 = "Venue 1"
TRACK_1 = "Track 1"


# Test is_codemash_event
def test_is_codemash_event_true():
    item = {"event": helpers.CODEMASH_EVENT_ID}
    assert helpers.is_codemash_event(item)


def test_is_codemash_event_false():
    item = {"event": "not_the_id"}
    assert not helpers.is_codemash_event(item)


# Test find_matching_id
def test_find_matching_id_found():
    data = {"list": [{"id": "a", "val": 1}, {"id": "b", "val": 2}]}
    result = helpers.find_matching_id(data, "list", "b")
    assert result["val"] == 2


def test_find_matching_id_not_found():
    data = {"list": [{"id": "a", "val": 1}]}
    result = helpers.find_matching_id(data, "list", "z", default={"val": 99})
    assert result["val"] == 99


# Test sessions_validations
def test_sessions_validations_valid():
    helpers.sessions_validations("0800", "1000")  # Should not raise


def test_sessions_validations_invalid_order():
    with pytest.raises(ValueError):
        helpers.sessions_validations("1200", "1000")


def test_sessions_validations_invalid_start():
    with pytest.raises(ValueError):
        helpers.sessions_validations("2500", "1000")


def test_sessions_validations_invalid_end():
    with pytest.raises(ValueError):
        helpers.sessions_validations("0800", "2500")


def test_sessions_validations_invalid_start_time_range():
    import pytest

    with pytest.raises(ValueError) as excinfo:
        helpers.sessions_validations("2500", "2501")
    assert "start_time_range must be a valid time" in str(excinfo.value)


# Test sessions_find_speakers
def test_sessions_find_speakers():
    data = {
        "sessionSpeakers": [
            {"session": "s1", "event": helpers.CODEMASH_EVENT_ID, "speaker": "sp1"}
        ],
        "speakers": [{"id": "sp1", "userProfile": "u1"}],
        "userProfiles": [{"id": "u1", "name": "A", "lastName": "B"}],
    }
    session = {"id": "s1"}
    speakers = helpers.sessions_find_speakers(data, session)
    assert speakers[0]["name"] == "A"
    assert speakers[0]["last_name"] == "B"


# Test filter functions
def make_session(**kwargs):
    base = {
        "id": "s1",
        "agenda": helpers.CONFERENCE_DAY_AGENDA_MAP["MONDAY"],
        "startTime": "0900",
        "duration": "60",
        "track": "t1",
        "venue": "v1",
    }
    base.update(kwargs)
    return base


def test_sessions_filter_by_day_of_week():
    session = make_session()
    assert helpers.sessions_filter_by_day_of_week({}, session, day_of_week="MONDAY")
    assert not helpers.sessions_filter_by_day_of_week(
        {}, session, day_of_week="TUESDAY"
    )


def test_sessions_filter_by_time_range():
    session = make_session(startTime="0900")
    assert helpers.sessions_filter_by_time_range(
        {}, session, start_time_range="0800", end_time_range="1000"
    )
    assert not helpers.sessions_filter_by_time_range(
        {}, session, start_time_range="1001", end_time_range="1100"
    )


def test_sessions_filter_by_duration():
    session = make_session(duration="60")
    assert helpers.sessions_filter_by_duration({}, session, duration=60)
    assert not helpers.sessions_filter_by_duration({}, session, duration=90)


def test_sessions_filter_by_venue():
    data = {
        "sessionVenues": [{"id": "v1", "event": helpers.CODEMASH_EVENT_ID}],
        "sessionVenueTranslations": [{"sessionVenue": "v1", "name": VENUE_1}],
    }
    session = make_session(venue="v1")
    assert helpers.sessions_filter_by_venue(data, session, venue_name=VENUE_1)
    assert not helpers.sessions_filter_by_venue(data, session, venue_name="Venue X")


def test_sessions_filter_by_track():
    data = {"trackTranslations": [{"track": "t1", "title": TRACK_1}]}
    session = make_session(track="t1")
    assert helpers.sessions_filter_by_track(data, session, track_name=TRACK_1)
    assert not helpers.sessions_filter_by_track(data, session, track_name="Track X")


def test_sessions_filter_by_speaker():
    data = {
        "sessionSpeakers": [
            {"session": "s1", "event": helpers.CODEMASH_EVENT_ID, "speaker": "sp1"}
        ],
        "speakers": [{"id": "sp1", "userProfile": "u1"}],
        "userProfiles": [{"id": "u1", "name": "Alice", "lastName": "Smith"}],
    }
    session = make_session(id="s1")
    assert helpers.sessions_filter_by_speaker(data, session, speaker_name="Alice")
    assert not helpers.sessions_filter_by_speaker(data, session, speaker_name="Bob")


# Test sessions_attach_extra_info


# Test map_to_session
def test_map_to_session():
    data = {
        "sessionTranslations": [{"session": "s1", "title": "T", "description": "D"}],
        "trackTranslations": [{"track": "t1", "title": TRACK_1}],
        "sessionVenueTranslations": [{"sessionVenue": "v1", "name": VENUE_1}],
        "sessionSpeakers": [
            {"session": "s1", "event": helpers.CODEMASH_EVENT_ID, "speaker": "sp1"}
        ],
        "speakers": [{"id": "sp1", "userProfile": "u1"}],
        "userProfiles": [{"id": "u1", "name": "Alice", "lastName": "Smith"}],
    }
    session = make_session(id="s1", track="t1", venue="v1")
    # map to dict to prevent type checking issues
    result: dict = dict(helpers.map_to_session(data, session))
    assert result["title"] == "T"
    assert result["description"] == "D"
    assert result["track"] == TRACK_1
    assert result["venue"] == VENUE_1
    assert result["speakers"][0]["name"] == "Alice"
    assert result["start_time"] == "0900"

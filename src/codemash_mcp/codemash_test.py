from pathlib import Path
import tempfile
import json
import math

from codemash_mcp.codemash import CodeMashDataReader
from typing import cast, List, Dict

from codemash_mcp.helpers import CODEMASH_EVENT_ID

TRACK_NAME = "Track 1"
VENUE_NAME = "Venue 1"
SESSION_TITLE = "Session 1"
FILTERS_PACKAGE = "codemash_mcp.codemash.filters"
MAP_SESSION_PACKAGE = "codemash_mcp.codemash.map_to_session"

SAMPLE_DATA = {
    "events": [
        {
            "id": CODEMASH_EVENT_ID,
            "startDate": "2026-01-12",
            "endDate": "2026-01-16",
            "timezone": "America/New_York",
            "portal": "811345730",
            "eventSocialHandle": "76186000006678009",
        }
    ],
    "eventTranslations": [
        {
            "event": CODEMASH_EVENT_ID,
            "name": "CodeMash 2026",
            "description": "Desc",
            "summary": "Summary",
        }
    ],
    "sessionVenues": [{"id": "v1", "event": CODEMASH_EVENT_ID}],
    "portals": [{"id": "811345730", "domain": "events.codemash.org"}],
    "eventSocialHandles": [
        {
            "id": "76186000006678009",
            "twitter": "@codemash",
            "facebook": "codemashfb",
            "linkedIn": "codemashli",
            "youtube": "codemashyt",
            "instagram": "codemashig",
            "website": "https://codemash.org",
        }
    ],
    "hotels": [
        {"id": "h1", "event": CODEMASH_EVENT_ID, "websiteUrl": "https://hotel.com"}
    ],
    "hotelTranslations": [{"hotel": "h1", "name": "Hotel 1", "address": "123 St"}],
    "tracks": [{"id": "t1", "event": CODEMASH_EVENT_ID}],
    "trackTranslations": [{"track": "t1", "title": TRACK_NAME}],
    "venues": [
        {
            "id": "v1",
            "event": CODEMASH_EVENT_ID,
            "latitude": 1.0,
            "longitude": 2.0,
            "zipcode": "12345",
            "country": "US",
        }
    ],
    "venueTranslations": [
        {
            "venue": "v1",
            "name": VENUE_NAME,
            "street": "1 Main",
            "townOrCity": "City",
            "state": "ST",
        }
    ],
    "speakers": [{"id": "s1", "event": CODEMASH_EVENT_ID, "userProfile": "u1"}],
    "userProfiles": [
        {
            "id": "u1",
            "name": "Alice",
            "lastName": "Smith",
            "company": "ACME",
            "designation": "Engineer",
            "twitter": "alice",
            "linkedin": "alice-li",
            "description": "Bio",
        }
    ],
    "sessionSpeakers": [
        {"speaker": "s1", "event": CODEMASH_EVENT_ID, "session": "sess1"}
    ],
    "sessions": [
        {
            "id": "sess1",
            "event": CODEMASH_EVENT_ID,
            "sessionType": "Talk",
            "startTime": "0900",
            "duration": "60",
            "track": "t1",
            "venue": "v1",
            "agenda": "76186000008378878",
        }
    ],
    "sessionTranslations": [
        {"session": "sess1", "title": SESSION_TITLE, "description": "Session Desc"}
    ],
    "sessionVenueTranslations": [
        {"sessionVenue": "v1", "name": VENUE_NAME},
    ],
}


def make_reader_with_sample():
    with tempfile.NamedTemporaryFile(mode="w+", delete=False) as f:
        json.dump(SAMPLE_DATA, f)
        f.flush()
        return CodeMashDataReader(Path(f.name))


def test_event():
    reader = make_reader_with_sample()
    event = reader.event()
    assert event is not None
    assert event.get("name") == "CodeMash 2026"
    assert event.get("domain") == "events.codemash.org"
    assert event.get("twitter") == "@codemash"


def test_hotels():
    reader = make_reader_with_sample()
    hotels = reader.hotels()
    assert len(hotels) == 1
    assert hotels[0].get("name") == "Hotel 1"


def test_tracks():
    reader = make_reader_with_sample()
    tracks = reader.tracks()
    assert len(tracks) == 1
    assert tracks[0].get("name") == TRACK_NAME


def test_venue():
    reader = make_reader_with_sample()
    venue = reader.venue()
    assert venue is not None
    assert venue.get("name") == VENUE_NAME
    assert venue.get("city") == "City"
    assert math.isclose(venue.get("latitude", 0), 1.0)
    assert math.isclose(venue.get("longitude", 0), 2.0)


def test_speakers():
    reader = make_reader_with_sample()
    speakers = reader.speakers()
    assert len(speakers) == 1
    assert speakers[0].get("name") == "Alice"
    sessions_list = cast(List[Dict], speakers[0].get("sessions"))
    assert sessions_list[0].get("title") == SESSION_TITLE


def test_sessions():
    reader = make_reader_with_sample()
    sessions = reader.sessions()
    assert len(sessions) == 1
    assert sessions[0]["title"] == SESSION_TITLE  # type: ignore
    assert sessions[0]["track"] == TRACK_NAME  # type: ignore
    assert sessions[0]["venue"] == VENUE_NAME  # type: ignore
    speakers_list = sessions[0]["speakers"]  # type: ignore
    assert speakers_list[0]["name"] == "Alice"  # type: ignore


def test_sessions_time_range():
    reader = make_reader_with_sample()
    # Should match
    sessions = reader.sessions(start_time_range="0800", end_time_range="1000")
    assert len(sessions) == 1
    # Should not match
    sessions = reader.sessions(start_time_range="1001", end_time_range="1100")
    assert len(sessions) == 0


def test_sessions_duration():
    reader = make_reader_with_sample()

    sessions = reader.sessions(duration=60)
    assert len(sessions) == 1
    sessions = reader.sessions(duration=90)
    assert len(sessions) == 0


def test_rooms():
    reader = make_reader_with_sample()
    rooms = reader.rooms()
    assert isinstance(rooms, list)
    assert len(rooms) == 1
    assert rooms[0] == VENUE_NAME

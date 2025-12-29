from typing import Any, Dict, cast
from codemash_mcp.types import (
    Event,
    Hotel,
    Speaker,
    SpeakerSession,
    Session,
    SessionSpeaker,
    Track,
    Venue,
    ConferenceDay,
)

CODEMASH_EVENT_ID = "76186000006678002"
CONFERENCE_DAY_AGENDA_MAP: Dict[ConferenceDay, str] = {
    "MONDAY": "76186000008378878",
    "TUESDAY": "76186000008378881",
    "WEDNESDAY": "76186000008389020",
    "THURSDAY": "76186000008389143",
    "FRIDAY": "76186000008389405",
}


def is_codemash_event(item: Dict, key="event") -> bool:
    return item.get(key) == CODEMASH_EVENT_ID


def find_matching_id(
    data, list_name: str, id_value: str | None, item_key="id", default={}
):
    return cast(
        Dict[str, str],
        next(
            (
                item
                for item in data.get(list_name, [])
                if item.get(item_key) == id_value
            ),
            default,
        ),
    )


def sessions_validations(start_time_range, end_time_range):
    if start_time_range and end_time_range and start_time_range >= end_time_range:
        raise ValueError(
            "start_time_range must be before end_time_range and cannot span midnight."
        )

    if start_time_range and ("0000" < start_time_range > "2400"):
        raise ValueError(
            "start_time_range must be a valid time in 'HHMM' format between '0000' and '2400'."
        )

    if end_time_range and ("0000" < end_time_range > "2400"):
        raise ValueError(
            "end_time_range must be a valid time in 'HHMM' format between '0000' and '2400'."
        )


def sessions_find_speakers(data, session):
    speakers = []
    for session_speaker in data.get("sessionSpeakers", []):
        if session_speaker.get("session") == session.get("id") and is_codemash_event(
            session_speaker
        ):
            speaker = find_matching_id(
                data, "speakers", session_speaker.get("speaker"), "id"
            )
            user_profile = find_matching_id(
                data, "userProfiles", speaker.get("userProfile")
            )
            speakers.append(
                Speaker(
                    name=user_profile.get("name", ""),
                    last_name=user_profile.get("lastName", ""),
                )
            )
    return speakers


# Individual filter functions for session filtering
def sessions_filter_by_day_of_week(data: Any, session: Any, **kwargs):
    day_of_week = kwargs.get("day_of_week")
    if not day_of_week:
        return True
    return session.get("agenda") == CONFERENCE_DAY_AGENDA_MAP[day_of_week]


def sessions_filter_by_time_range(data: Any, session: Any, **kwargs):
    start_time_range = kwargs.get("start_time_range")
    end_time_range = kwargs.get("end_time_range")
    session_start_time = session.get("startTime", None)
    if start_time_range and session_start_time:
        return start_time_range <= session_start_time <= end_time_range
    return True


def sessions_filter_by_duration(data: Any, session: Any, **kwargs):
    duration = kwargs.get("duration")
    if duration:
        return int(session.get("duration", "0")) == duration
    return True


def sessions_filter_by_venue(data: Any, session: Any, **kwargs):
    venue_name = kwargs.get("venue_name")
    session_venue = find_matching_id(data, "sessionVenues", session.get("venue"), "id")
    if not is_codemash_event(session_venue):
        return False
    venue = find_matching_id(
        data, "sessionVenueTranslations", session.get("venue"), "sessionVenue"
    )
    if venue_name:
        return venue.get("name", "") == venue_name
    return True


def sessions_filter_by_track(data: Any, session: Any, **kwargs):
    track_name = kwargs.get("track_name")
    track_translation = find_matching_id(
        data, "trackTranslations", session.get("track", ""), "track"
    )
    if track_name:
        return track_translation.get("title", "") == track_name
    return True


def sessions_filter_by_speaker(data: Any, session: Any, **kwargs):
    speaker_name = kwargs.get("speaker_name")
    speakers = sessions_find_speakers(data, session)
    if speaker_name:
        return any(
            f"{speaker['name']} {speaker['last_name']}".lower().find(
                speaker_name.lower()
            )
            != -1
            for speaker in speakers
        )
    return True


def map_to_session(data, session: Any) -> Session:
    session_translation = find_matching_id(
        data, "sessionTranslations", session.get("id"), "session"
    )
    track_translation = find_matching_id(
        data, "trackTranslations", session.get("track", ""), "track"
    )
    venue = find_matching_id(
        data, "sessionVenueTranslations", session.get("venue"), "sessionVenue"
    )
    speakers = sessions_find_speakers(data, session)
    return Session(
        {
            "title": session_translation.get("title", "Untitled"),
            "description": session_translation.get("description", ""),
            "type": session.get("sessionType", ""),
            "start_time": session.get("startTime", None),
            "duration": int(session.get("duration", "0")),
            "track": track_translation.get("title", "Unknown"),
            "venue": venue.get("name", "Unknown"),
            "speakers": speakers,
        }
    )


filters = [
    sessions_filter_by_day_of_week,
    sessions_filter_by_time_range,
    sessions_filter_by_duration,
    sessions_filter_by_venue,
    sessions_filter_by_track,
    sessions_filter_by_speaker,
]

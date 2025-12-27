import json
from pathlib import Path
from typing import Annotated, Dict, Literal, TypedDict, cast

CODEMASH_EVENT_ID = "76186000006678002"


class Event(TypedDict, total=False):
    name: str
    description: str
    summary: str
    start_date: str
    end_date: str
    timezone: str
    domain: str
    twitter: str
    facebook: str
    linkedin: str
    youtube: str
    instagram: str
    website: str


class Hotel(TypedDict, total=False):
    name: str
    address: str
    website: str


class SpeakerSession(TypedDict, total=False):
    title: str
    description: str
    type: str
    start_time: str
    duration: int
    track: str
    venue: str


class Speaker(TypedDict, total=False):
    name: str
    last_name: str
    company: str | None
    designation: str | None
    twitter: str | None
    linkedin: str | None
    description: str | None
    sessions: list[SpeakerSession]


class SessionSpeaker(TypedDict, total=False):
    name: str
    last_name: str


class Session(TypedDict, total=False):
    title: str
    description: str | None
    type: str
    start_time: str
    duration: int
    track: str
    venue: str
    speakers: list[SessionSpeaker]


class Track(TypedDict, total=False):
    name: str


class Venue(TypedDict, total=False):
    name: str
    street: str
    city: str
    state: str
    latitude: float
    longitude: float
    zipcode: str
    country: str


ConferenceDay = Literal["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY"]
CONFERENCE_DAY_AGENDA_MAP: Dict[ConferenceDay, str] = {
    "MONDAY": "76186000008378878",
    "TUESDAY": "76186000008378881",
    "WEDNESDAY": "76186000008389020",
    "THURSDAY": "76186000008389143",
    "FRIDAY": "76186000008389405",
}


# TODO: add useful filtering for common queries
# - speakers by track
# - speaker f/l name
class CodeMashDataReader:
    """A class to read CodeMash data from JSON files."""

    def __init__(self, data_directory: Path):
        self.data_directory = data_directory
        self.data = json.load(open(data_directory, "r"))

    def _find_matching_id(
        self, list_name: str, id_value: str | None, item_key="id", default={}
    ):
        return cast(
            Dict[str, str],
            next(
                (
                    item
                    for item in self.data.get(list_name, [])
                    if item.get(item_key) == id_value
                ),
                default,
            ),
        )

    def event(self) -> Annotated[Event | None, "CodeMash 2026 event information"]:
        """Retrieves information about the CodeMash 2026 event itself."""
        for event in self.data.get("events", []):
            if event.get("id") != CODEMASH_EVENT_ID:
                continue

            event_translation = self._find_matching_id(
                "eventTranslations", event.get("id"), "event"
            )
            portal = self._find_matching_id("portals", event.get("portal"))
            socials = self._find_matching_id(
                "eventSocialHandles", event.get("eventSocialHandle")
            )
            return Event(
                {
                    "name": event_translation.get("name", "Unknown"),
                    "description": event_translation.get("description", ""),
                    "summary": event_translation.get("summary", ""),
                    "start_date": event.get("startDate", ""),
                    "end_date": event.get("endDate", ""),
                    "timezone": event.get("timezone", ""),
                    "domain": portal.get("domain", ""),
                    "twitter": socials.get("twitter", ""),
                    "facebook": socials.get("facebook", ""),
                    "linkedin": socials.get("linkedIn", ""),
                    "youtube": socials.get("youtube", ""),
                    "instagram": socials.get("instagram", ""),
                    "website": socials.get("website", ""),
                }
            )
        return None

    def hotels(
        self,
    ) -> Annotated[list[Hotel], "List of hotels for the CodeMash 2026 event."]:
        """Fetch the list of hotels available for the CodeMash 2026 event.

        This list does not include the Kalahari itself, which is also a viable hotel option.
        """
        hotel_list = []
        for hotel in self.data.get("hotels", []):
            if hotel.get("event") != CODEMASH_EVENT_ID:
                continue

            hotel_translation = self._find_matching_id(
                "hotelTranslations", hotel.get("id"), "hotel"
            )
            hotel_list.append(
                Hotel(
                    {
                        "name": hotel_translation.get("name", ""),
                        "address": hotel_translation.get("address", ""),
                        "website": hotel.get("websiteUrl", ""),
                    }
                )
            )
        return hotel_list

    def speakers(
        self,
    ) -> Annotated[list[Speaker], "List of speakers for the CodeMash 2026 event"]:
        """Fetch the list of speakers for the CodeMash 2026 event."""
        speaker_list = []
        for speaker in self.data.get("speakers", []):
            if speaker.get("event") != CODEMASH_EVENT_ID:
                continue

            user_profile = self._find_matching_id(
                "userProfiles", speaker.get("userProfile")
            )

            speaker_id = speaker.get("id")
            sessions = []
            for item in self.data.get("sessionSpeakers", []):
                if (
                    item.get("speaker") == speaker_id
                    and item.get("event") == CODEMASH_EVENT_ID
                ):
                    session = self._find_matching_id("sessions", item.get("session"))
                    session_translations = self._find_matching_id(
                        "sessionTranslations", item.get("session"), "session"
                    )
                    track_translation = self._find_matching_id(
                        "trackTranslations", session.get("track", ""), "track"
                    )
                    venue = self._find_matching_id(
                        "sessionVenueTranslations", session.get("venue"), "sessionVenue"
                    )

                    sessions.append(
                        SpeakerSession(
                            {
                                "title": session_translations.get("title", "Untitled"),
                                "description": session_translations.get(
                                    "description", ""
                                ),
                                "type": session.get("sessionType", ""),
                                "start_time": session.get("startTime", ""),
                                "duration": int(session.get("duration", "0")),
                                "track": track_translation.get("title", "Unknown"),
                                "venue": venue.get("name", "Unknown"),
                            }
                        )
                    )

            speaker_list.append(
                Speaker(
                    {
                        "name": user_profile.get("name", "Unknown"),
                        "last_name": user_profile.get("lastName", "Unknown"),
                        "company": user_profile.get("company"),
                        "designation": user_profile.get("designation"),
                        "twitter": user_profile.get("twitter"),
                        "linkedin": user_profile.get("linkedin"),
                        "description": user_profile.get("description"),
                        "sessions": sessions,
                    }
                )
            )
        return speaker_list

    def sessions(
        self,
        track_name: Annotated[str | None, "Filter sessions by track name"] = None,
        venue_name: Annotated[str | None, "Filter sessions by venue name"] = None,
        speaker_name: Annotated[
            str | None,
            "Filter sessions by speaker name. Name may be first, last, and may be partial (case-insensitive, contains).",
        ] = None,
        day_of_week: Annotated[
            ConferenceDay | None, "Filter sessions by day of the week"
        ] = None,
        start_time_range: Annotated[
            str | None,
            "Filter sessions by time range, start time. Format: 'HHMM', which must pad with a leading zero for single digit hours. It uses the 24-hour clock. Start time must be before end time and cannot span midnight.",
        ] = None,
        end_time_range: Annotated[
            str | None,
            "Filter sessions by time range, end time. Format: 'HHMM', which must pad with a leading zero for single digit hours. It uses the 24-hour clock. Start time must be before end time and cannot span midnight.",
        ] = None,
        duration: Annotated[
            Literal[30, 60, 90, 115, 120, 125, 145, 180, 210, 235, 240, 265, 295]
            | None,
            "Filter sessions by duration in minutes.",
        ] = None,
    ) -> Annotated[list[Session], "List of sessions for the CodeMash 2026 event"]:
        """Fetch the list of sessions for the CodeMash 2026 event.

        This method will return all of the sessions for the event, which can be a lot of data. You should prefer filtering
        by track name, venue name, speaker name, duration, day of the week, and/or time range to limit the results.
        """
        if (start_time_range and not end_time_range) or (
            end_time_range and not start_time_range
        ):
            raise ValueError(
                "Both start_time_range and end_time_range must be provided together."
            )

        if start_time_range and end_time_range and start_time_range >= end_time_range:
            raise ValueError(
                "start_time_range must be before end_time_range and cannot span midnight."
            )

        if start_time_range and (
            len(start_time_range) != 4 or not start_time_range.isdigit()
        ):
            raise ValueError(
                "start_time_range must be in 'HHMM' format, which must pad with a leading zero for single digit hours."
            )

        if end_time_range and (
            len(end_time_range) != 4 or not end_time_range.isdigit()
        ):
            raise ValueError(
                "end_time_range must be in 'HHMM' format, which must pad with a leading zero for single digit hours."
            )

        if start_time_range and (
            start_time_range < "0000" or start_time_range > "2400"
        ):
            raise ValueError(
                "start_time_range must be a valid time in 'HHMM' format between '0000' and '2400'."
            )

        if end_time_range and (end_time_range < "0000" or end_time_range > "2400"):
            raise ValueError(
                "end_time_range must be a valid time in 'HHMM' format between '0000' and '2400'."
            )

        session_list = []

        for session in self.data.get("sessions", []):
            if (
                day_of_week
                and session.get("agenda") != CONFERENCE_DAY_AGENDA_MAP[day_of_week]
            ):
                continue

            session_start_time = session.get("startTime", None)
            if (
                start_time_range
                and end_time_range
                and session_start_time
                and not (start_time_range <= session_start_time <= end_time_range)
            ):
                continue

            if duration and int(session.get("duration", "0")) != duration:
                continue

            session_venue = self._find_matching_id(
                "sessionVenues", session.get("venue"), "id"
            )
            if session_venue.get("event") != CODEMASH_EVENT_ID:
                continue
            venue = self._find_matching_id(
                "sessionVenueTranslations", session.get("venue"), "sessionVenue"
            )
            if venue_name and venue.get("name", "") != venue_name:
                continue

            session_translation = self._find_matching_id(
                "sessionTranslations", session.get("id"), "session"
            )
            track_translation = self._find_matching_id(
                "trackTranslations", session.get("track", ""), "track"
            )
            if track_name and track_translation.get("title", "") != track_name:
                continue

            speakers = []
            for session_speaker in self.data.get("sessionSpeakers", []):
                if (
                    session_speaker.get("session") == session.get("id")
                    and session_speaker.get("event") == CODEMASH_EVENT_ID
                ):
                    speaker = self._find_matching_id(
                        "speakers", session_speaker.get("speaker"), "id"
                    )
                    user_profile = self._find_matching_id(
                        "userProfiles", speaker.get("userProfile")
                    )
                    speakers.append(
                        SessionSpeaker(
                            name=user_profile.get("name", ""),
                            last_name=user_profile.get("lastName", ""),
                        )
                    )
            if speaker_name and not any(
                f"{speaker['name']} {speaker['last_name']}".lower().find(
                    speaker_name.lower()
                )
                != -1
                for speaker in speakers
            ):
                continue

            session_list.append(
                Session(
                    {
                        "title": session_translation.get("title", "Untitled"),
                        "description": session_translation.get("description", ""),
                        "type": session.get("sessionType", ""),
                        "start_time": session_start_time,
                        "duration": int(session.get("duration", "0")),
                        "track": track_translation.get("title", "Unknown"),
                        "venue": venue.get("name", "Unknown"),
                        "speakers": speakers,
                    }
                )
            )
        return session_list

    def tracks(
        self,
    ) -> Annotated[list[Track], "List of tracks for the CodeMash 2026 event"]:
        """Fetch the list of tracks for the CodeMash 2026 event."""
        track_list = []
        for track in self.data.get("tracks", []):
            if track.get("event") != CODEMASH_EVENT_ID:
                continue

            track_translation = self._find_matching_id(
                "trackTranslations", track.get("id"), "track"
            )
            track_list.append(
                Track(
                    {
                        "name": track_translation.get("title", "Unknown"),
                    }
                )
            )
        return track_list

    def venue(
        self,
    ) -> Annotated[Venue | None, "Venue information for the CodeMash 2026 event"]:
        """Fetch the venue information for the CodeMash 2026 event."""
        for venue in self.data.get("venues", []):
            if venue.get("event") != CODEMASH_EVENT_ID:
                continue

            venue_translation = self._find_matching_id(
                "venueTranslations", venue.get("id"), "venue"
            )
            return Venue(
                {
                    "name": venue_translation.get("name", "Unknown"),
                    "street": venue_translation.get("street", ""),
                    "city": venue_translation.get("townOrCity", ""),
                    "state": venue_translation.get("state", ""),
                    "latitude": float(venue.get("latitude")),
                    "longitude": float(venue.get("longitude")),
                    "zipcode": venue.get("zipcode"),
                    "country": venue.get("country"),
                }
            )
        return None

import json
from pathlib import Path
from typing import Annotated, Dict, Literal, TypedDict, cast
from pydantic import Field, ValidationError

from codemash_mcp.types import (
    Event,
    Hotel,
    Speaker,
    SpeakerSession,
    Session,
    Track,
    Venue,
    ConferenceDay,
)
from codemash_mcp.helpers import (
    map_to_session,
    find_matching_id,
    is_codemash_event,
    filters,
    sessions_validations,
)


# TODO: add useful filtering for common queries
# - speakers by track
# - speaker f/l name
class CodeMashDataReader:
    """A class to read CodeMash data from JSON files."""

    def __init__(self, data_directory: Path):
        self.data_directory = data_directory
        self.data = json.load(open(data_directory, "r"))

    def event(self) -> Annotated[Event | None, "CodeMash 2026 event information"]:
        """Retrieves information about the CodeMash 2026 event itself."""
        for event in self.data.get("events", []):
            if not is_codemash_event(event, "id"):
                continue

            event_translation = find_matching_id(
                self.data, "eventTranslations", event.get("id"), "event"
            )
            portal = find_matching_id(self.data, "portals", event.get("portal"))
            socials = find_matching_id(
                self.data, "eventSocialHandles", event.get("eventSocialHandle")
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
            if not is_codemash_event(hotel):
                continue

            hotel_translation = find_matching_id(
                self.data, "hotelTranslations", hotel.get("id"), "hotel"
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
            if not is_codemash_event(speaker):
                continue

            user_profile = find_matching_id(
                self.data, "userProfiles", speaker.get("userProfile")
            )

            speaker_id = speaker.get("id")
            sessions = []
            for item in self.data.get("sessionSpeakers", []):
                if item.get("speaker") == speaker_id and is_codemash_event(item):
                    session = find_matching_id(
                        self.data, "sessions", item.get("session")
                    )
                    session_translations = find_matching_id(
                        self.data, "sessionTranslations", item.get("session"), "session"
                    )
                    track_translation = find_matching_id(
                        self.data,
                        "trackTranslations",
                        session.get("track", ""),
                        "track",
                    )
                    venue = find_matching_id(
                        self.data,
                        "sessionVenueTranslations",
                        session.get("venue"),
                        "sessionVenue",
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
            Field(
                description="Filter sessions by time range, start time. Format: 'HHMM', which must pad with a leading zero for single digit hours. It uses the 24-hour clock. Start time must be before end time and cannot span midnight.",
                default=None,
                pattern="^([01][0-9]|2[0-3])[0-5][0-9]$",
            ),
        ] = None,
        end_time_range: Annotated[
            str | None,
            Field(
                description="Filter sessions by time range, end time. Format: 'HHMM', which must pad with a leading zero for single digit hours. It uses the 24-hour clock. Start time must be before end time and cannot span midnight.",
                default="2400",
                pattern="^([01][0-9]|2[0-3])[0-5][0-9]$",
            ),
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
        sessions_validations(start_time_range, end_time_range)

        filtered_sessions = []
        for session in self.data.get("sessions", []):
            if all(
                filter(
                    self.data,
                    session,
                    day_of_week=day_of_week,
                    start_time_range=start_time_range,
                    end_time_range=end_time_range,
                    duration=duration,
                    venue_name=venue_name,
                    track_name=track_name,
                    speaker_name=speaker_name,
                )
                for filter in filters
            ):
                filtered_sessions.append(map_to_session(self.data, session))
        return filtered_sessions

    def tracks(
        self,
    ) -> Annotated[list[Track], "List of tracks for the CodeMash 2026 event"]:
        """Fetch the list of tracks for the CodeMash 2026 event."""
        track_list = []
        for track in self.data.get("tracks", []):
            if not is_codemash_event(track):
                continue

            track_translation = find_matching_id(
                self.data, "trackTranslations", track.get("id"), "track"
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
            if not is_codemash_event(venue):
                continue

            venue_translation = find_matching_id(
                self.data, "venueTranslations", venue.get("id"), "venue"
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

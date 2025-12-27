import json
from pathlib import Path
from typing import Dict, cast

CODEMASH_EVENT_ID = "76186000006678002"


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

    def event(self):
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
            return {
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

    def hotels(self):
        hotel_list = []
        for hotel in self.data.get("hotels", []):
            if hotel.get("event") != CODEMASH_EVENT_ID:
                continue

            hotel_translation = self._find_matching_id(
                "hotelTranslations", hotel.get("id"), "hotel"
            )
            hotel_list.append(
                {
                    "name": hotel_translation.get("name", ""),
                    "address": hotel_translation.get("address", ""),
                    "website": hotel.get("websiteUrl", ""),
                }
            )
        return hotel_list

    def speakers(self):
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
                        {
                            "title": session_translations.get("title", "Untitled"),
                            "description": session_translations.get("description", ""),
                            "type": session.get("sessionType", ""),
                            "start_time": session.get("startTime", ""),
                            "duration": session.get("duration", 0),
                            "track": track_translation.get("title", "Unknown"),
                            "venue": venue.get("name", "Unknown"),
                        }
                    )

            speaker_list.append(
                {
                    "name": user_profile.get("name"),
                    "last_name": user_profile.get("lastName"),
                    "company": user_profile.get("company", ""),
                    "designation": user_profile.get("designation", ""),
                    "twitter": user_profile.get("twitter", ""),
                    "linkedin": user_profile.get("linkedin", ""),
                    "description": user_profile.get("description", ""),
                    "sessions": sessions,
                }
            )
        return speaker_list

    def sessions(self):
        session_list = []

        for session in self.data.get("sessions", []):
            session_venue = self._find_matching_id(
                "sessionVenues", session.get("venue"), "id"
            )
            if session_venue.get("event") != CODEMASH_EVENT_ID:
                continue

            venue = self._find_matching_id(
                "sessionVenueTranslations", session.get("venue"), "sessionVenue"
            )
            session_translation = self._find_matching_id(
                "sessionTranslations", session.get("id"), "session"
            )
            track_translation = self._find_matching_id(
                "trackTranslations", session.get("track", ""), "track"
            )
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
                        f"{user_profile.get('name')} {user_profile.get('lastName')}"
                    )

            session_list.append(
                {
                    "title": session_translation.get("title", "Untitled"),
                    "description": session_translation.get("description", ""),
                    "type": session.get("sessionType", ""),
                    "start_time": session.get("startTime", ""),
                    "duration": session.get("duration", 0),
                    "track": track_translation.get("title", "Unknown"),
                    "venue": venue.get("name", "Unknown"),
                    "speakers": speakers,
                }
            )
        return session_list

    def tracks(self):
        track_list = []
        for track in self.data.get("tracks", []):
            if track.get("event") != CODEMASH_EVENT_ID:
                continue

            track_translation = self._find_matching_id(
                "trackTranslations", track.get("id"), "track"
            )
            track_list.append(
                {
                    "name": track_translation.get("title", "Unknown"),
                }
            )
        return track_list

    def venue(self):
        for venue in self.data.get("venues", []):
            if venue.get("event") != CODEMASH_EVENT_ID:
                continue

            venue_translation = self._find_matching_id(
                "venueTranslations", venue.get("id"), "venue"
            )
            return {
                "name": venue_translation.get("name", "Unknown"),
                "street": venue_translation.get("street", ""),
                "city": venue_translation.get("townOrCity", ""),
                "state": venue_translation.get("state", ""),
                "latitude": venue.get("latitude"),
                "longitude": venue.get("longitude"),
                "zipcode": venue.get("zipcode"),
                "country": venue.get("country"),
            }

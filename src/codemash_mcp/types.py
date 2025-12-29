from typing import Dict, Literal, TypedDict


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

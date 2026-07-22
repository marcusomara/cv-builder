"""Validated domain models."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Link(StrictModel):
    label: str
    url: str


class PersonalDetails(StrictModel):
    name: str
    email: str
    phone: str | None = None
    location: str | None = None
    links: list[Link] = Field(default_factory=list)


class MasterBullet(StrictModel):
    id: str
    text: str


class TailoredBullet(StrictModel):
    text: str
    source_id: str


class MasterExperience(StrictModel):
    id: str
    employer: str
    role: str
    start_date: str
    end_date: str
    location: str | None = None
    bullets: list[MasterBullet]


class TailoredExperience(StrictModel):
    id: str
    employer: str
    role: str
    start_date: str
    end_date: str
    location: str | None = None
    bullets: list[TailoredBullet]


class MasterProject(StrictModel):
    id: str
    name: str
    description: str
    bullets: list[MasterBullet] = Field(default_factory=list)


class TailoredProject(StrictModel):
    id: str
    name: str
    description: str
    bullets: list[TailoredBullet] = Field(default_factory=list)


class Education(StrictModel):
    institution: str
    qualification: str
    start_date: str
    end_date: str


class Achievement(StrictModel):
    id: str
    text: str


class MasterCV(StrictModel):
    personal: PersonalDetails
    profile: str
    experience: list[MasterExperience]
    projects: list[MasterProject] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    achievements: list[Achievement] = Field(default_factory=list)


class TailoredCV(StrictModel):
    personal: PersonalDetails
    profile: str
    experience: list[TailoredExperience]
    projects: list[TailoredProject] = Field(default_factory=list)
    education: list[Education] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    achievements: list[Achievement] = Field(default_factory=list)


class JobSpec(StrictModel):
    title: str = "Unknown role"
    company: str = "Unknown company"
    description: str
    responsibilities: list[str] = Field(default_factory=list)
    required_skills: list[str] = Field(default_factory=list)
    desirable_skills: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    seniority: str = "unspecified"
    industry: str = "unspecified"


class TailoringRules(StrictModel):
    maximum_pages: int = 2
    maximum_bullets_per_experience: int = 5
    maximum_bullet_length: int = 180
    preserve_dates: bool = True
    preserve_employers: bool = True
    allow_reordering: bool = True
    allow_rewriting: bool = True
    forbidden_buzzwords: list[str] = Field(default_factory=list)

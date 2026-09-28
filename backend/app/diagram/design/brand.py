from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BrandConfig:
    name: str = "EVU"
    logo_text: str = "EVU"
    primary_color: str = "#2563EB"
    secondary_color: str = "#7C3AED"
    website: str | None = None
    logo_url: str | None = None

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "logo_text": self.logo_text,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "website": self.website,
            "logo_url": self.logo_url,
        }
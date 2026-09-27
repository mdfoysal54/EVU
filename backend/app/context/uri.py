from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass(frozen=True)
class EVUURI:
    scope: str
    path: str

    @property
    def value(self) -> str:
        normalized = self.path.strip("/")
        return f"evu://{self.scope}/{normalized}"

    @classmethod
    def parse(cls, uri: str) -> "EVUURI":
        parsed = urlparse(uri)

        if parsed.scheme != "evu":
            raise ValueError("URI must use evu:// scheme")

        scope = parsed.netloc.strip("/")
        path = parsed.path.strip("/")

        if not scope:
            raise ValueError("EVU URI scope is required")

        return cls(
            scope=scope,
            path=path,
        )

    def child(self, name: str) -> "EVUURI":
        name = name.strip("/")

        if not name:
            raise ValueError("Child name cannot be empty")

        new_path = (
            f"{self.path}/{name}"
            if self.path
            else name
        )

        return EVUURI(
            scope=self.scope,
            path=new_path,
        )

    def is_under(self, parent: "EVUURI") -> bool:
        if self.scope != parent.scope:
            return False

        current = self.path.strip("/")
        target = parent.path.strip("/")

        return (
            current == target
            or current.startswith(target + "/")
        )
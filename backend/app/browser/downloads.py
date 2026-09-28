from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class DownloadResult:
    path: str
    suggested_filename: Optional[str] = None


class DownloadManager:
    def __init__(
        self,
        download_directory: str = "downloads",
    ) -> None:
        self.download_directory = Path(
            download_directory
        )

        self.download_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

    async def wait_for_download(
        self,
        page: Any,
        action,
    ) -> DownloadResult:
        async with page.expect_download() as download_info:
            await action()

        download = await download_info.value

        filename = download.suggested_filename

        path = (
            self.download_directory
            / filename
        )

        await download.save_as(str(path))

        return DownloadResult(
            path=str(path),
            suggested_filename=filename,
        )
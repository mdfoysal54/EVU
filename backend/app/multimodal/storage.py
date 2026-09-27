import hashlib
import uuid
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings


class MultimodalStorage:
    def __init__(self) -> None:
        self.root = Path(settings.MULTIMODAL_STORAGE_DIR)

    def ensure_root(self) -> None:
        self.root.mkdir(
            parents=True,
            exist_ok=True,
        )

    def create_asset_directory(self, asset_id: str) -> Path:
        directory = self.root / asset_id

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return directory

    def create_asset_id(self) -> str:
        return f"asset_{uuid.uuid4().hex}"

    async def save_upload(
        self,
        upload: UploadFile,
        asset_id: str,
        max_size_bytes: int,
    ) -> tuple[Path, int, str]:

        self.ensure_root()

        asset_directory = self.create_asset_directory(asset_id)

        filename = Path(upload.filename or "upload").name

        stored_path = asset_directory / filename

        total_size = 0
        digest = hashlib.sha256()

        try:
            with stored_path.open("wb") as output:

                while True:
                    chunk = await upload.read(
                        settings.MULTIMODAL_CHUNK_SIZE_BYTES
                    )

                    if not chunk:
                        break

                    total_size += len(chunk)

                    if total_size > max_size_bytes:
                        raise ValueError(
                            "Uploaded file exceeds the allowed size."
                        )

                    digest.update(chunk)
                    output.write(chunk)

        except Exception:
            if stored_path.exists():
                stored_path.unlink(missing_ok=True)

            if asset_directory.exists():
                try:
                    asset_directory.rmdir()
                except OSError:
                    pass

            raise

        finally:
            await upload.close()

        return (
            stored_path,
            total_size,
            digest.hexdigest(),
        )

    def delete_asset(self, asset_id: str) -> bool:
        asset_directory = self.root / asset_id

        if not asset_directory.exists():
            return False

        for path in asset_directory.rglob("*"):
            if path.is_file():
                path.unlink(missing_ok=True)

        directories = sorted(
            [
                path
                for path in asset_directory.rglob("*")
                if path.is_dir()
            ],
            reverse=True,
        )

        for directory in directories:
            try:
                directory.rmdir()
            except OSError:
                pass

        try:
            asset_directory.rmdir()
        except OSError:
            return False

        return True

    def find_asset_file(self, asset_id: str) -> Path | None:
        asset_directory = self.root / asset_id

        if not asset_directory.exists():
            return None

        for path in asset_directory.iterdir():
            if path.is_file():
                return path

        return None


multimodal_storage = MultimodalStorage()
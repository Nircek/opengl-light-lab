"""Texture loading and management for OpenGL."""

from pathlib import Path

from OpenGL.GL import (  # type: ignore
    GL_LINEAR,
    GL_RGB,
    GL_TEXTURE_2D,
    GL_TEXTURE_MAG_FILTER,
    GL_TEXTURE_MIN_FILTER,
    GL_UNSIGNED_BYTE,
    glBindTexture,
    glDeleteTextures,
    glGenTextures,
    glTexImage2D,
    glTexParameteri,
)
from PIL import Image


class TextureManager:
    """Manages OpenGL texture loading and lifecycle."""

    def __init__(self) -> None:
        self._texture_id: int | None = None
        self._loaded_path: str | None = None

    @property
    def texture_id(self) -> int | None:
        """Return the current OpenGL texture ID, or None if no texture loaded."""
        return self._texture_id

    @property
    def is_loaded(self) -> bool:
        """Return True if a texture is currently loaded."""
        return self._texture_id is not None

    def load_if_changed(self, texture_path: str | None) -> bool:
        """Load texture if the path has changed.

        Args:
            texture_path: Path to texture file, or None to unload.

        Returns:
            True if texture was loaded/changed, False otherwise.
        """
        if texture_path == self._loaded_path:
            return False

        self._unload()
        self._loaded_path = texture_path

        if texture_path is None:
            return True

        path = Path(texture_path)
        if not path.exists():
            return False

        try:
            self._load_from_file(path)
        except Exception as e:
            print(f"Failed to load texture: {e}")
            self._texture_id = None
            return False
        else:
            return True

    def _load_from_file(self, path: Path) -> None:
        """Load texture from file."""
        img = Image.open(path).transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        img_data = img.convert("RGB").tobytes()
        width, height = img.size

        self._texture_id = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self._texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, width, height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glBindTexture(GL_TEXTURE_2D, 0)

    def _unload(self) -> None:
        """Unload current texture if any."""
        if self._texture_id is not None:
            glDeleteTextures([self._texture_id])
            self._texture_id = None

    def cleanup(self) -> None:
        """Clean up OpenGL resources."""
        self._unload()
        self._loaded_path = None

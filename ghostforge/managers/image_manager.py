"""Image download and management."""

from __future__ import annotations
import gzip
import hashlib
import os
import shutil
import tarfile
import urllib.request
from urllib.parse import urlparse
from pathlib import Path
from typing import Optional

try:
    import lzma  # for .xz
except Exception:
    lzma = None


class ImageManager:
    """Manages VM base images."""
    
    def __init__(self, images_dir: Path):
        """Initialize image manager.
        
        Args:
            images_dir: Directory to store downloaded images
        """
        self.images_dir = images_dir
        self.images_dir.mkdir(parents=True, exist_ok=True)

    def _download(self, url: str, dest: Path):
        """Download a file from URL."""
        print(f"[download] {url} -> {dest}")
        with urllib.request.urlopen(url) as r, open(dest, "wb") as f:
            shutil.copyfileobj(r, f)

    def _verify_checksum(self, file_path: Path, checksum: str, algo: str):
        """Verify file checksum."""
        algo = algo.lower()
        h = getattr(hashlib, algo, None)
        if h is None:
            raise ValueError(f"Unsupported checksum algorithm: {algo}")
        
        print(f"[checksum] {algo} {file_path}")
        hasher = h()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(1024 * 1024), b""):
                hasher.update(chunk)
        
        digest = hasher.hexdigest()
        if digest != checksum.lower():
            raise SystemExit(
                f"Checksum mismatch for {file_path}: expected {checksum}, got {digest}"
            )
        print("[checksum] OK")

    def _decompress_if_needed(self, src: Path) -> Path:
        """Decompress image if compressed."""
        name = src.name
        
        # Handle .xz compression
        if name.endswith(".xz") and lzma:
            out = src.with_suffix("")
            print(f"[decompress] xz -> {out}")
            with lzma.open(src, "rb") as fin, open(out, "wb") as fout:
                shutil.copyfileobj(fin, fout)
            return out
        
        # Handle .gz compression
        if name.endswith(".gz"):
            out = src.with_suffix("")
            print(f"[decompress] gz -> {out}")
            with gzip.open(src, "rb") as fin, open(out, "wb") as fout:
                shutil.copyfileobj(fin, fout)
            return out
        
        # Handle tar archives
        if name.endswith(".tar") or name.endswith(".tar.gz") or name.endswith(".tgz"):
            print(f"[extract] tar -> {self.images_dir}")
            with tarfile.open(src, "r:*") as tf:
                tf.extractall(self.images_dir)
            qcows = list(self.images_dir.glob("*.qcow2"))
            if qcows:
                return qcows[0]
        
        return src

    def obtain_image(
        self,
        image_url: Optional[str],
        image_path: Optional[Path],
        checksum: Optional[str],
        checksum_algo: Optional[str],
        preset: Optional[str]
    ) -> Path:
        """Obtain a base image from URL, path, or preset.
        
        Args:
            image_url: URL to download image from
            image_path: Local path to existing image
            checksum: Optional checksum for verification
            checksum_algo: Checksum algorithm (md5, sha256, etc.)
            preset: Preset name to use
            
        Returns:
            Path to the base image
        """
        from ghostforge.core.presets import PRESETS
        
        if preset:
            preset = preset.lower()
            if preset not in PRESETS:
                raise SystemExit(f"Unknown --image-preset: {preset}")
            image_url = PRESETS[preset]
            print(f"[preset] {preset} -> {image_url}")
        
        if image_path:
            path = Path(image_path)
            if not path.exists():
                raise SystemExit(f"Image path does not exist: {path}")
            return path
        
        if not image_url:
            raise SystemExit("Provide --image-url or --image-path or --image-preset")
        
        file_name = os.path.basename(urlparse(image_url).path) or "base-image"
        dest = self.images_dir / file_name
        
        if not dest.exists():
            self._download(image_url, dest)
        else:
            print(f"[cache] Using cached image: {dest}")
        
        if checksum and checksum_algo:
            self._verify_checksum(dest, checksum, checksum_algo)
        
        return self._decompress_if_needed(dest)
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.media_pack import ensure_media_pack


def main():
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manifest = ensure_media_pack(base_path)
    print(manifest.get("version", ""))
    print(manifest.get("visual_root", ""))
    print(manifest.get("audio_root", ""))


if __name__ == "__main__":
    main()

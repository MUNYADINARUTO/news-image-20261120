"""Make Fun bounty entry: news-image-20261120.

"Sum up 20 November's world news in one image" ($250).

This script is the entrypoint for the news-image-20261120 submission.
It does no generation itself: the front-page image was composed offline and
is bundled in this directory as ``entry.png``. The script validates the
bundled image (PNG structure, dimensions, size, clean IEND trailer), then
copies it atomically to ``/output/entry.png`` and verifies the copy's
SHA-256 against the known hash of the bundled image, so a corrupted or
partial output can never be mistaken for a valid entry.

Standard library only, no network access, fully deterministic.
"""

import hashlib
import os
import struct
import sys

# SHA-256 of the bundled entry.png, computed at build time.
EXPECTED_SHA256 = "0d4d41af09644250b2f1ff3b390338a535bd6861308eaed7c70eba8971c40dde"
SOURCE_NAME = "entry.png"
OUTPUT_DIR = "/output"
MAX_DIMENSION = 1024
MAX_FILE_SIZE = 1_048_576  # 1 MiB

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
IEND_CHUNK = b"\x00\x00\x00\x00IEND\xaeB`\x82"


def validate_png(data: bytes) -> tuple[int, int]:
    """Validate the bundled PNG bytes; return (width, height).

    Checks: PNG magic bytes, a well-formed IHDR chunk with dimensions
    within limits, and a clean 12-byte IEND chunk at the end of the file.
    """
    if len(data) < len(PNG_MAGIC):
        raise ValueError("file is shorter than the PNG magic bytes")
    if data[: len(PNG_MAGIC)] != PNG_MAGIC:
        raise ValueError("missing PNG magic bytes")

    # First chunk after the magic must be IHDR: 4-byte length, 4-byte type,
    # 13 bytes of data (width, height, bit depth, colour type, compression,
    # filter, interlace), 4-byte CRC.
    offset = len(PNG_MAGIC)
    if len(data) < offset + 8 + 13 + 4:
        raise ValueError("file is too short to contain an IHDR chunk")
    ihdr_length, ihdr_type = struct.unpack_from(">I4s", data, offset)
    if ihdr_type != b"IHDR":
        raise ValueError("first chunk is not IHDR")
    if ihdr_length != 13:
        raise ValueError(f"IHDR has unexpected length {ihdr_length} (expected 13)")

    width, height = struct.unpack_from(">II", data, offset + 8)
    if width == 0 or height == 0:
        raise ValueError(f"IHDR declares zero dimension ({width}x{height})")
    if width > MAX_DIMENSION or height > MAX_DIMENSION:
        raise ValueError(
            f"dimensions {width}x{height} exceed the "
            f"{MAX_DIMENSION}x{MAX_DIMENSION} limit"
        )

    # Validate the declared bit depth / colour type combination against the
    # PNG spec: only certain pairs are legal, and a mismatch means the file
    # is not a decodable image even if its dimensions look fine.
    bit_depth, colour_type = struct.unpack_from(">BB", data, offset + 8 + 8)
    legal_bit_depths = {
        0: (1, 2, 4, 8, 16),  # greyscale
        2: (8, 16),  # truecolour (RGB)
        3: (1, 2, 4, 8),  # indexed colour
        4: (8, 16),  # greyscale with alpha
        6: (8, 16),  # truecolour with alpha (RGBA)
    }
    if colour_type not in legal_bit_depths:
        raise ValueError(f"IHDR declares unknown colour type {colour_type}")
    if bit_depth not in legal_bit_depths[colour_type]:
        raise ValueError(
            f"IHDR declares illegal bit depth {bit_depth} "
            f"for colour type {colour_type}"
        )
    return width, height


def validate_iend(data: bytes) -> None:
    """Require a clean 12-byte IEND chunk (zero-length, type IEND) at EOF."""
    if len(data) < len(IEND_CHUNK) or data[-len(IEND_CHUNK):] != IEND_CHUNK:
        raise ValueError("file does not end with a clean 12-byte IEND chunk")


def main() -> int:
    script_dir = os.path.dirname(os.path.abspath(__file__))
    source_path = os.path.join(script_dir, SOURCE_NAME)
    output_path = os.path.join(OUTPUT_DIR, SOURCE_NAME)

    try:
        with open(source_path, "rb") as handle:
            data = handle.read()
    except OSError as exc:
        print(f"error: cannot read bundled image {source_path}: {exc}", file=sys.stderr)
        return 1

    if len(data) > MAX_FILE_SIZE:
        print(
            f"error: bundled image is {len(data)} bytes, "
            f"over the {MAX_FILE_SIZE} byte limit",
            file=sys.stderr,
        )
        return 1

    try:
        width, height = validate_png(data)
        validate_iend(data)
    except ValueError as exc:
        print(f"error: bundled image failed validation: {exc}", file=sys.stderr)
        return 1

    # Write atomically: temp file in the output directory, fsync, rename.
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    temp_path = os.path.join(OUTPUT_DIR, f".{SOURCE_NAME}.tmp")
    try:
        with open(temp_path, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_path, output_path)
    except OSError as exc:
        print(f"error: cannot write output {output_path}: {exc}", file=sys.stderr)
        try:
            os.unlink(temp_path)
        except OSError:
            pass
        return 1

    # Verify the written file's SHA-256 matches the bundled image exactly.
    digest = hashlib.sha256()
    try:
        with open(output_path, "rb") as handle:
            for block in iter(lambda: handle.read(65536), b""):
                digest.update(block)
    except OSError as exc:
        print(f"error: cannot read back output {output_path}: {exc}", file=sys.stderr)
        return 1
    output_sha256 = digest.hexdigest()
    if output_sha256 != EXPECTED_SHA256:
        print(
            f"error: output SHA-256 mismatch: got {output_sha256}, "
            f"expected {EXPECTED_SHA256}",
            file=sys.stderr,
        )
        return 1

    print(
        f"wrote {output_path} ({len(data)} bytes, {width}x{height}, "
        f"sha256 {output_sha256})"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

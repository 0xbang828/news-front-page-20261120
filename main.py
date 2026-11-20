"""Submission program for the make.fun bounty news-image-20261120.

The image that sits beside this file, entry.png, is a one-day newspaper front page
drawn for Friday, 20 November 2026: "THE WORLD IN ONE DAY", edition 20, seven stories
from six continents (Cyclone Akvan's landfall in Odisha, COP31 closing in Antalya
without a fossil-fuel pledge, the postponed decision on strikes on Iran, North
Korea's enlarged Yongbyon plant, Sudan on the Security Council agenda, the real's
slide as Lula's fiscal plan clears the Senate, and Argentina joining the patent
treaty).

This program's only job is to hand those exact bytes to the grader. The page was
drawn once, offline, and is shipped in the repository; nothing is rendered again
here, nothing is fetched, and no third-party code runs. The sandbox gives the
program no network and only the Python 3.13 standard library, so re-drawing the
page at grading time could only make the entry worse: the safest reproduction of a
fixed image is a byte-for-byte copy of it.

Before copying, the image is checked against the rules the sealed scorer applies:
PNG signature, IHDR width and height within 1024 by 1024, at most 1 MiB of file, and
every chunk carrying a valid CRC. A malformed or oversized image makes the case
invalid, and an invalid entry is listed with a Valid column of 0 and takes no prize,
so every failure here aborts loudly instead of shipping a broken file.
"""

import hashlib
import os
import shutil
import struct
import sys
import zlib
from pathlib import Path

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
MAX_SIDE = 1024
CHUNK_OVERHEAD = 12  # 4-byte length, 4-byte type, 4-byte CRC
IEND = b"IEND"
IHDR = b"IHDR"


def fail(message):
    """Abort with a message a human can act on. Exit code 1, nothing else written."""
    raise SystemExit(f"main.py: refusing to submit entry.png: {message}")


def check_signature(data):
    """The judge tells a PNG from a JPEG by the first bytes; this must be a PNG."""
    if not data.startswith(PNG_SIGNATURE):
        found = data[:8]
        fail(f"bad PNG signature {found!r}, expected {PNG_SIGNATURE!r}")


def check_chunks(data):
    """Walk the chunk list, verifying each CRC, and require IHDR first and IEND last.

    The rules ask for a whole image: every PNG chunk with its checksum and the image
    data its header describes. A chunk whose CRC disagrees with its bytes means the
    file was truncated or edited in place, which the scorer reads as a broken image.
    """
    types = []
    offset = len(PNG_SIGNATURE)
    total = len(data)

    while offset < total:
        if offset + 8 > total:
            fail(f"truncated chunk header at byte {offset}")

        length, ctype = struct.unpack(">I4s", data[offset : offset + 8])
        payload_start = offset + 8
        payload_end = payload_start + length
        chunk_end = payload_end + 4
        if chunk_end > total:
            fail(
                f"chunk {ctype!r} at byte {offset} claims {length} data bytes "
                f"but the file ends at {total}"
            )

        stored_crc = struct.unpack(">I", data[payload_end:chunk_end])[0]
        computed_crc = zlib.crc32(data[payload_start:payload_end], zlib.crc32(ctype))
        if computed_crc & 0xFFFFFFFF != stored_crc:
            fail(
                f"chunk {ctype!r} at byte {offset} has CRC "
                f"{stored_crc:#010x}, but its bytes give {computed_crc & 0xFFFFFFFF:#010x}"
            )

        if not types and ctype != IHDR:
            fail(f"first chunk is {ctype!r}, expected IHDR")
        types.append(ctype)
        offset = chunk_end

        if ctype == IEND:
            break

    if not types or types[-1] != IEND:
        fail("no IEND chunk, the image data is cut short")
    if offset != total:
        fail(f"{total - offset} stray bytes after IEND")
    if IHDR not in types:
        fail("no IHDR chunk, the header is missing")
    return types


def read_ihdr(data):
    """Return (width, height) from the IHDR payload, the first 8 bytes after its length."""
    if len(data) < len(PNG_SIGNATURE) + CHUNK_OVERHEAD + 13:
        fail("file is too short to hold an IHDR chunk")

    length = struct.unpack(">I", data[8:12])[0]
    if length < 13:
        fail(f"IHDR chunk holds {length} bytes, needs at least 13")

    width, height, bit_depth, color_type, compression, filter_method, interlace = (
        struct.unpack(">IIBBBBB", data[16:29])
    )

    if width == 0 or height == 0:
        fail(f"header says the image is {width} by {height} pixels")
    if compression != 0 or filter_method != 0 or interlace not in (0, 1):
        fail(
            "header asks for an unknown compression, filter or interlace method "
            f"({compression}, {filter_method}, {interlace})"
        )
    if not (1 <= bit_depth <= 16):
        fail(f"header says bit depth {bit_depth}")
    if color_type not in (0, 2, 3, 4, 6):
        fail(f"header says colour type {color_type}")
    return width, height


def check_size(data):
    """Cap the file at 1 MiB, the scorer's own limit; the cheapest guard, so it runs first."""
    size = len(data)
    if size > MAX_BYTES:
        fail(f"{size} bytes is over the 1 MiB limit of {MAX_BYTES}")


def check_dimensions(width, height):
    """Cap the image at 1024 by 1024, the other half of the scorer's size rule."""
    if width > MAX_SIDE or height > MAX_SIDE:
        fail(f"{width} by {height} pixels is over the {MAX_SIDE} by {MAX_SIDE} limit")


def main():
    # The grader mounts the repository read-only at /bot and a writable /output; the
    # input directory is read from the environment too, but nothing in it is needed
    # here, since the page is part of the repository and not derived from any input.
    input_dir = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
    output_dir = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

    source = Path(__file__).resolve().parent / "entry.png"
    if not source.is_file():
        fail(f"{source} is missing from the repository")

    # The input directory is read because the harness defines it, but the page ships in
    # the repository: nothing is drawn from an input, so a missing /input is no problem
    # and a path that is not a directory is worth saying out loud.
    if input_dir.exists() and not input_dir.is_dir():
        fail(f"{input_dir} is not a directory")

    data = source.read_bytes()
    check_size(data)
    check_signature(data)
    chunk_types = check_chunks(data)
    width, height = read_ihdr(data)
    check_dimensions(width, height)

    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / "entry.png"
    shutil.copyfile(source, target)

    # Read the copy back: an interrupted or short write would hand the judge a
    # different file than the one just validated, and the entry would fail the gate.
    written = target.read_bytes()
    digest = hashlib.sha256(data).digest()
    if len(written) != len(data) or hashlib.sha256(written).digest() != digest:
        fail(f"the copy at {target} differs from {source}")

    # Deterministic summary only: the file's own numbers, never a timestamp, a random
    # value or the absolute output path, so two runs into different directories print
    # the same lines and two runs into the same directory write the same bytes.
    print(
        f"entry.png: {width}x{height}, {len(data)} bytes, {len(chunk_types)} chunks, "
        f"every CRC ok, sha256 {digest.hex()}"
    )
    print(f"copied bit for bit to {target.name} in the output directory")
    print(f"read nothing from the input directory ({input_dir.name or input_dir})")
    return 0


if __name__ == "__main__":
    sys.exit(main())

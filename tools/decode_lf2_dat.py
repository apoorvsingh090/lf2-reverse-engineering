#!/usr/bin/env python3
"""Decode (and encode) Little Fighter 2 data files (.dat).

Format (verified against LF2 v2.0a `data/*.dat`, `bg/**/bg.dat`):
  - first 123 bytes: ignored header/padding
  - rest: each byte is plaintext `wrapping_add` a repeating Caesar key

Key: b"odBearBecauseHeIsVeryGoodSiuHungIsAGo"
(see https://github.com/azriel91/lf2_codec for the equivalent Rust codec)

Usage:
    python decode_lf2_dat.py decode data/davis.dat decoded.txt
    python decode_lf2_dat.py encode plain.txt out.dat
"""
import sys

CAESAR_CIPHER = b"odBearBecauseHeIsVeryGoodSiuHungIsAGo"
HEADER_LEN = 123
DATA_HEADER = (b"This is sample data as bytes. "
               b"The first 123 bytes are ignored during decoding, "
               b"the rest are decoded using a caesar cipher. ")
assert len(DATA_HEADER) == HEADER_LEN, len(DATA_HEADER)


def decode(data: bytes) -> bytes:
    body = data[HEADER_LEN:]
    return bytes((b - CAESAR_CIPHER[i % len(CAESAR_CIPHER)]) % 256
                 for i, b in enumerate(body))


def encode(plain: bytes) -> bytes:
    return (DATA_HEADER + bytes((b + CAESAR_CIPHER[i % len(CAESAR_CIPHER)]) % 256
                                for i, b in enumerate(plain)))


def main(argv):
    if len(argv) != 4 or argv[1] not in ("decode", "encode"):
        print(__doc__)
        return 2
    mode, src, dst = argv[1], argv[2], argv[3]
    with open(src, "rb") as f:
        data = f.read()
    out = decode(data) if mode == "decode" else encode(data)
    with open(dst, "wb") as f:
        f.write(out)
    print(f"{mode}d {src} -> {dst} ({len(out)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

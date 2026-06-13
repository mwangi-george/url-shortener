from app.core.base62 import decode_base62, encode_base62


def test_base62_round_trip() -> None:
    for value in [0, 1, 61, 62, 3844, 1_000_000, 1_825_000_000]:
        assert decode_base62(encode_base62(value)) == value

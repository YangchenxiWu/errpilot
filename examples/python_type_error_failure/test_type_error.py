def increment(value: int) -> int:
    return value + 1


def test_increment_rejects_wrong_type() -> None:
    increment("1")

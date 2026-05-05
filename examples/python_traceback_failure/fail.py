def parse_retry_count(raw_value: str) -> int:
    retry_count = int(raw_value)
    if retry_count < 0:
        raise ValueError("retry count must be non-negative")
    return retry_count


def main() -> None:
    parse_retry_count("-1")


if __name__ == "__main__":
    main()

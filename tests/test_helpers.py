from helpers import format_koins, format_cooldown, random_password, create_progress_bar


class TestFormatKoins:
    def test_small_number(self) -> None:
        assert format_koins(1000) == "1.000"

    def test_large_number(self) -> None:
        assert format_koins(1000000) == "1.000.000"

    def test_zero(self) -> None:
        assert format_koins(0) == "0"

    def test_negative(self) -> None:
        assert format_koins(-500) == "-500"

    def test_single_digit(self) -> None:
        assert format_koins(5) == "5"


class TestFormatCooldown:
    def test_seconds_only(self) -> None:
        assert format_cooldown(30) == "30s"

    def test_minutes_and_seconds(self) -> None:
        assert format_cooldown(90) == "1m 30s"

    def test_hours_minutes_seconds(self) -> None:
        assert format_cooldown(3661) == "1h 1m 1s"

    def test_zero(self) -> None:
        assert format_cooldown(0) == "0s"

    def test_exact_hour(self) -> None:
        assert format_cooldown(3600) == "1h 0s"


class TestRandomPassword:
    def test_default_length(self) -> None:
        assert len(random_password()) == 12

    def test_custom_length(self) -> None:
        assert len(random_password(20)) == 20

    def test_all_alphanumeric(self) -> None:
        pwd = random_password(100)
        assert pwd.isalnum()


class TestProgressBar:
    def test_empty(self) -> None:
        bar = create_progress_bar(0, 100, 10)
        assert "█" not in bar
        assert len(bar) == 10

    def test_full(self) -> None:
        bar = create_progress_bar(100, 100, 10)
        assert bar == "█" * 10

    def test_half(self) -> None:
        bar = create_progress_bar(50, 100, 10)
        assert bar.count("█") == 5

    def test_zero_maximum(self) -> None:
        bar = create_progress_bar(0, 0, 10)
        assert len(bar) == 10
from config import Settings


class TestSettings:
    def test_default_values(self) -> None:
        settings = Settings(
            TOKEN="test-token",
            MONGODB="mongodb://localhost:27017",
        )
        assert settings.command_prefix == "!"
        assert settings.daily_min == 1567
        assert settings.daily_max == 5456
        assert settings.rob_success_chance == 45

    def test_rank_thresholds(self) -> None:
        settings = Settings(
            TOKEN="test-token",
            MONGODB="mongodb://localhost:27017",
        )
        assert 1000000 in settings.rank_thresholds
        assert 0 in settings.rank_thresholds
        rank, color = settings.rank_thresholds[1000000]
        assert "MAGNATA" in rank

    def test_custom_values(self) -> None:
        settings = Settings(
            TOKEN="test-token",
            MONGODB="mongodb://localhost:27017",
            daily_min=100,
            daily_max=200,
        )
        assert settings.daily_min == 100
        assert settings.daily_max == 200
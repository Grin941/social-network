import dataclasses
import typing

import locust


@dataclasses.dataclass
class Stage:
    users: int
    spawn_rate: int
    duration: int


class DynamicUserShape(locust.LoadTestShape):
    # Define your stages with (user_count, spawn_rate, duration_in_seconds)
    stages: list[Stage] = []

    def tick(self) -> typing.Optional[tuple[int, int]]:
        run_time = self.get_run_time()

        for stage in self.stages:
            if run_time < stage.duration:
                return (stage.users, stage.spawn_rate)
            run_time -= stage.duration

        return None  # Stop the test when all stages are complete

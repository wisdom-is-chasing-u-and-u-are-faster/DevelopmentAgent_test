"""
QA Persona v2 -- auto-generated tests
Service: redis
Suite:   performance
Source:  test_strategy/plans/redis__performance.json
Generated: 2024-07-24T14:38:20.910363Z
"""

import os
from locust import HttpUser, events, task, between

SERVICE_URL = os.environ.get("SERVICE_URL", "").strip()
P95_MS_THRESHOLD = float(os.environ.get("PERF_P95_MS_THRESHOLD", "500"))
FAIL_RATIO_THRESHOLD = 0.01

class TargetUser(HttpUser):
    """
    Simulates a user accessing the service. The host is configured via the
    SERVICE_URL environment variable. Since no endpoints were specified, this
    user hits the root endpoint only.
    """
    host = SERVICE_URL
    wait_time = between(0.5, 1.5)

    @task
    def get_root(self):
        """Task to hit the root endpoint of the service."""
        self.client.get("/")

@events.test_stop.add_listener
def enforce_thresholds(environment, **kwargs):
    """
    Checks if the test run meets the performance thresholds.
    Fails the test run (by setting a non-zero exit code) if the failure ratio
    or the P95 response time is above the defined thresholds.
    """
    stats = environment.stats.total
    fail_ratio = stats.fail_ratio
    p95_ms = stats.get_response_time_percentile(0.95)

    if fail_ratio > FAIL_RATIO_THRESHOLD:
        environment.process_exit_code = 1
    
    if p95_ms and p95_ms >= P95_MS_THRESHOLD:
        environment.process_exit_code = 1

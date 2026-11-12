"""
Challenge lifecycle management and enrollment validation service.
Enforces participant capacity caps, eligibility, and state transitions.
"""

from app.models import repo

class ChallengeService:
    @staticmethod
    def get_challenges(sport_type=None, status=None, page=1, page_size=10):
        with repo._lock:
            filtered = repo.challenges
            if sport_type and sport_type.lower() != "all":
                filtered = [c for c in filtered if c["sport_type"].lower() == sport_type.lower()]
            if status and status.lower() != "all":
                filtered = [c for c in filtered if c["status"].lower() == status.lower()]

            total_count = len(filtered)
            start_idx = (page - 1) * page_size
            end_idx = start_idx + page_size
            items = filtered[start_idx:end_idx]

            return {
                "challenges": items,
                "total_count": total_count,
                "page": page,
                "page_size": page_size
            }

    @staticmethod
    def get_challenge_by_id(challenge_id: int):
        with repo._lock:
            for c in repo.challenges:
                if c["id"] == challenge_id:
                    return c
            return None

    @staticmethod
    def create_challenge(data: dict):
        with repo._lock:
            new_id = max([c["id"] for c in repo.challenges], default=0) + 1
            
            try:
                target_val = float(data.get("target_value", 100.0))
            except (ValueError, TypeError):
                target_val = 100.0
                
            try:
                cap = int(data.get("capacity_cap", 1000))
            except (ValueError, TypeError):
                cap = 1000

            challenge = {
                "id": new_id,
                "title": data.get("title", f"Challenge {new_id}"),
                "description": data.get("description", ""),
                "sport_type": data.get("sport_type", "Running"),
                "goal_metric": data.get("goal_metric", "distance_km"),
                "target_value": target_val,
                "start_date": data.get("start_date", "2026-06-01T00:00:00Z"),
                "end_date": data.get("end_date", "2026-06-30T23:59:59Z"),
                "capacity_cap": cap,
                "enrolled_count": 0,
                "is_team_based": bool(data.get("is_team_based", False)),
                "status": "UPCOMING"
            }
            repo.challenges.append(challenge)
            return challenge

    @staticmethod
    def enroll_participant(challenge_id: int, user_id: int, team_code: str = None) -> tuple[dict, int, str]:
        """
        Enrolls a participant enforcing strict capacity limits.
        Returns (enrollment_data, http_status_code, error_message).
        """
        with repo._lock:
            target_challenge = None
            for c in repo.challenges:
                if c["id"] == challenge_id:
                    target_challenge = c
                    break

            if not target_challenge:
                return None, 404, "Challenge not found"

            # Check capacity limits
            if target_challenge["enrolled_count"] >= target_challenge["capacity_cap"]:
                return None, 409, "Challenge Enrollment Cap Reached"

            # Check existing enrollment
            for e in repo.enrollments:
                if e["challenge_id"] == challenge_id and e["user_id"] == user_id:
                    return e, 200, ""

            target_challenge["enrolled_count"] += 1
            new_enroll_id = max([e["id"] for e in repo.enrollments], default=0) + 1
            enrollment = {
                "enrollment_id": str(new_enroll_id),
                "challenge_id": str(challenge_id),
                "user_id": str(user_id),
                "team_code": team_code,
                "status": "ENROLLED",
                "enrolled_at": "2026-06-10T12:00:00Z"
            }
            repo.enrollments.append(enrollment)
            return enrollment, 200, ""

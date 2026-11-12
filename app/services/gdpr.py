"""
Automated GDPR and CCPA cascading data erasure service.
Permanently purges or anonymizes all personal telemetry, profile, and enrollment records.
"""

from app.models import repo
from datetime import datetime

class GDPRService:
    @staticmethod
    def execute_cascading_deletion(user_id: int, confirm_email: str, reason: str = "") -> tuple[dict, int, str]:
        with repo._lock:
            # Verify user exists
            user = next((u for u in repo.users if u["id"] == user_id), None)
            if not user:
                return None, 404, "User not found"

            if user.get("email", "").lower() != confirm_email.strip().lower():
                return None, 400, "Email confirmation does not match authenticated user"

            records_purged = 0

            # 1. Purge profile
            if user_id in repo.profiles:
                del repo.profiles[user_id]
                records_purged += 1

            # 2. Purge enrollments
            initial_enroll_len = len(repo.enrollments)
            repo.enrollments = [e for e in repo.enrollments if e["user_id"] != user_id]
            records_purged += (initial_enroll_len - len(repo.enrollments))

            # 3. Purge privacy zones
            if user_id in repo.privacy_settings:
                del repo.privacy_settings[user_id]
                records_purged += 1

            # 4. Anonymize social posts
            for post in repo.social_posts:
                if post.get("user_id") == user_id:
                    post["screen_name"] = "Anonymized Athlete"
                    post["avatar_url"] = ""
                    post["masked_gps_points"] = []
                    records_purged += 1

            # 5. Remove user from active roster
            repo.users = [u for u in repo.users if u["id"] != user_id]
            records_purged += 1

            deletion_result = {
                "request_id": f"del_{user_id}_{int(datetime.now().timestamp())}",
                "status": "COMPLETED",
                "records_purged": records_purged,
                "anonymized_at": datetime.utcnow().isoformat() + "Z"
            }
            return deletion_result, 200, ""

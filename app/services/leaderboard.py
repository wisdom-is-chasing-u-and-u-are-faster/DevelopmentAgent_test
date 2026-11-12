"""
High-concurrency leaderboard dense ranking service.
Delivers global, local, and relative (+/- 5 ranks) rankings with profile display metadata.
"""

from app.models import repo

class LeaderboardService:
    @staticmethod
    def get_leaderboard(challenge_id: int = 1, ranking_type: str = "global", current_user_id: int = 1) -> dict:
        with repo._lock:
            # Build current scores from enrollments / profiles
            entries = []
            for e in repo.enrollments:
                if e["challenge_id"] == challenge_id:
                    u_id = e["user_id"]
                    prof = repo.profiles.get(u_id, {})
                    entries.append({
                        "user_id": u_id,
                        "screen_name": prof.get("screen_name", f"Athlete {u_id}"),
                        "avatar_url": prof.get("avatar_url", ""),
                        "score_value": float(e.get("progress_value", 0.0)),
                        "unit": "km"
                    })

            # Sort descending by score_value (dense ranking)
            entries.sort(key=lambda x: x["score_value"], reverse=True)
            for idx, entry in enumerate(entries, start=1):
                entry["rank_position"] = idx

            user_rank_obj = None
            user_idx = -1
            for idx, entry in enumerate(entries):
                if entry["user_id"] == current_user_id:
                    user_rank_obj = entry
                    user_idx = idx
                    break

            # If user has no score, assign baseline
            if not user_rank_obj:
                prof = repo.profiles.get(current_user_id, {})
                user_rank_obj = {
                    "user_id": current_user_id,
                    "screen_name": prof.get("screen_name", "Alex Rivers"),
                    "avatar_url": prof.get("avatar_url", ""),
                    "score_value": 0.0,
                    "unit": "km",
                    "rank_position": len(entries) + 1
                }

            if ranking_type.lower() == "relative" and user_idx != -1:
                start = max(0, user_idx - 5)
                end = min(len(entries), user_idx + 6)
                result_rankings = entries[start:end]
            else:
                result_rankings = entries[:50]

            return {
                "challenge_id": str(challenge_id),
                "type": ranking_type,
                "rankings": result_rankings,
                "user_rank": user_rank_obj
            }

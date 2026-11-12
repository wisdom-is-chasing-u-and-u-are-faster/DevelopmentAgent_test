"""
Timezone-aware streak continuity and dynamic badge evaluation service.
Calculates daily and weekly workout streaks and unlocks milestone badges.
"""

from datetime import datetime, date, timedelta

class StreakService:
    @staticmethod
    def calculate_streaks(user_id: int, current_streak: dict, new_activity_date: date) -> dict:
        """
        Updates consecutive daily and weekly streaks for an athlete.
        """
        last_date_str = current_streak.get("last_activity_date")
        daily = current_streak.get("consecutive_days", 1)
        weekly = current_streak.get("consecutive_weeks", 1)

        if not last_date_str:
            return {
                "consecutive_days": 1,
                "consecutive_weeks": 1,
                "last_activity_date": new_activity_date.isoformat()
            }

        last_date = datetime.strptime(str(last_date_str)[:10], "%Y-%m-%d").date()
        diff = (new_activity_date - last_date).days

        if diff == 0:
            # Same day workout; streak maintained
            pass
        elif diff == 1:
            daily += 1
            if daily % 7 == 0:
                weekly += 1
        elif diff > 1:
            # Streak broken; reset
            daily = 1

        return {
            "consecutive_days": daily,
            "consecutive_weeks": weekly,
            "last_activity_date": new_activity_date.isoformat()
        }

    @staticmethod
    def evaluate_badges(profile: dict, badges_list: list) -> list:
        """
        Evaluates badge criteria against athlete metrics.
        """
        daily_streak = profile.get("daily_streak", 0)
        total_workouts = profile.get("total_workouts", 0)

        updated_badges = []
        for b in badges_list:
            key = b.get("badge_key", "")
            unlocked = b.get("unlocked", False)

            if key == "streak_7" and daily_streak >= 7:
                unlocked = True
            elif key == "early_bird" and total_workouts >= 10:
                unlocked = True
            elif key == "century_rider" and total_workouts >= 20:
                unlocked = True

            b_copy = dict(b)
            b_copy["unlocked"] = unlocked
            updated_badges.append(b_copy)

        return updated_badges

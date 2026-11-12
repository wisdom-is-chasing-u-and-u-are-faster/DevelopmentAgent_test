"""
Zero-knowledge residential geofence masking service.
Automatically masks raw GPS coordinates within a 500-meter radius of
user-designated sensitive locations (Home, Office) prior to sharing on social feeds.
"""

import math

class PrivacyService:
    @staticmethod
    def haversine_distance_meters(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculates great-circle distance between two GPS coordinates in meters."""
        r = 6371000.0 # Earth radius in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
        c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
        return r * c

    @classmethod
    def mask_gps_track(cls, gps_points: list, sensitive_zones: list, default_radius: int = 500) -> tuple[list, int]:
        """
        Masks any GPS coordinates falling within sensitive location radii.
        Returns (masked_points, count_masked).
        """
        if not gps_points or not sensitive_zones:
            return gps_points, 0

        masked_track = []
        masked_count = 0

        for pt in gps_points:
            lat = float(pt.get("lat") or pt.get("latitude", 0.0))
            lng = float(pt.get("lng") or pt.get("longitude", 0.0))

            is_sensitive = False
            for zone in sensitive_zones:
                z_lat = float(zone.get("latitude") or zone.get("lat", 0.0))
                z_lng = float(zone.get("longitude") or zone.get("lng", 0.0))
                radius = int(zone.get("radius") or zone.get("radius_meters", default_radius))

                dist = cls.haversine_distance_meters(lat, lng, z_lat, z_lng)
                if dist <= radius:
                    is_sensitive = True
                    break

            if is_sensitive:
                masked_count += 1
                # Coordinate is obscured for privacy
                masked_track.append({"lat": round(lat, 2), "lng": round(lng, 2), "masked": True})
            else:
                masked_track.append({"lat": lat, "lng": lng, "masked": False})

        return masked_track, masked_count

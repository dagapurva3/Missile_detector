import math


def classify_threat(velocity, altitude):
    """Determine threat type based on characteristics"""
    if velocity > 2500:  # Hypersonic
        return "missile"
    elif altitude < 1000 and velocity < 300:
        return "drone"
    else:
        return "aircraft"


def calculate_intercept_point(start_x, start_y, target, speed):
    """Predict intercept point using relative velocity"""
    # Simple prediction: assume target continues on current vector
    dist = math.sqrt((target.x - start_x) ** 2 + (target.y - start_y) ** 2)
    time_to_intercept = dist / speed

    # Predict future position
    future_x = target.x + target.vx * time_to_intercept
    future_y = target.y + target.vy * time_to_intercept

    return future_x, future_y

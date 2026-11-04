def classify_status(water_level_mm: float, pipe_diameter_mm: float) -> str:
    ratio = water_level_mm / pipe_diameter_mm  # d/D
    if ratio >= 0.75:
        return "red"       # overflow risk
    elif ratio >= 0.45:
        return "yellow"    # caution
    elif ratio <= 0.05:
        return "yellow"    # possible underflow / sensor fault / blockage upstream
    else:
        return "green"     # normal
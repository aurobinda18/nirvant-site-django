from datetime import datetime, timedelta

def to_minutes(t):
    h, m = map(int, t.split(":"))
    return h * 60 + m

def to_time(m):
    return f"{m//60:02d}:{m%60:02d}"


def generate_slots(window_start, window_end, breaks, call_duration=20, gap=5):
    slots = []

    start = to_minutes(window_start)
    end = to_minutes(window_end)

    break_ranges = [(to_minutes(b[0]), to_minutes(b[1])) for b in breaks]

    t = start
    while t + call_duration <= end:
        blocked = False
        for b_start, b_end in break_ranges:
            if not (t + call_duration <= b_start or t >= b_end):
                blocked = True
                t = b_end
                break

        if not blocked:
            slots.append((t, t + call_duration))
            t += call_duration + gap

    return slots
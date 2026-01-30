
from .slot_generator import generate_slots, to_time


def build_weekly_slots(mentor):
    week = {}

    # Mon–Sat
    for day in ["mon","tue","wed","thu","fri","sat"]:
        week[day] = generate_slots(
            mentor["weekday_window"][0],
            mentor["weekday_window"][1],
            mentor["breaks"],
            gap=mentor["gap_minutes"]
        )

    # Sunday
    sunday_slots = []
    for win in mentor["sunday_windows"]:
        sunday_slots += generate_slots(
            win[0], win[1],
            mentor["breaks"],
            gap=mentor["gap_minutes"]
        )
    week["sun"] = sunday_slots

    return week

def schedule_week(students, mentors):
    # Prepare mentors
    mentor_state = {}
    for m in mentors:
        mentor_state[m["mentor_id"]] = {
            "type": m["type"],
            "slots": build_weekly_slots(m),
            "load": 0
        }

    calls = []
    days = ["mon","tue","wed","thu","fri","sat","sun"]

    for student in students:
        calls_needed = ["normal", "normal", "academic"]
        used_days = set()   # ✅ NEW

        for call_type in calls_needed:
            assigned = False

            eligible = sorted(
                [m for m in mentor_state.items() if m[1]["type"] == call_type],
                key=lambda x: x[1]["load"]
            )

            for mentor_id, data in eligible:
                for day in days:

                    # ✅ NEW RULE: only one call per day per student
                    if day in used_days:
                        continue

                    if data["slots"][day]:
                        slot = data["slots"][day].pop(0)

                        calls.append({
                            "student": student["user_id"],
                            "mentor": mentor_id,
                            "day": day,
                            "start": to_time(slot[0]),
                            "end": to_time(slot[1]),
                            "type": call_type
                        })

                        data["load"] += 1
                        used_days.add(day)   # ✅ REMEMBER DAY
                        assigned = True
                        break

                if assigned:
                    break

            if not assigned:
                raise Exception(f"No available {call_type} mentor slots")

    return calls

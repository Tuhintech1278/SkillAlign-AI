from collections import Counter


def analyze_skills(jobs):

    skill_counter = Counter()

    for job in jobs:

        skills = job["skills"].split(",")

        for skill in skills:

            skill = skill.strip()

            if skill:
                skill_counter[skill] += 1

    result = []

    for skill, count in skill_counter.most_common():

        result.append({
            "skill": skill,
            "demand": count
        })

    return result


def get_skill_gaps(jobs, courses):

    demanded_skills = Counter()

    for job in jobs:

        skills = job["skills"].split(",")

        for skill in skills:

            demanded_skills[
                skill.strip()
            ] += 1

    available_skills = set()

    for course in courses:

        skills = course["skills"].split(",")

        for skill in skills:

            available_skills.add(
                skill.strip().lower()
            )

    gaps = []

    for skill, demand in demanded_skills.items():

        if skill.lower() not in available_skills:

            gaps.append({
                "skill": skill,
                "demand": demand,
                "status": "Skill Gap"
            })

    return gaps
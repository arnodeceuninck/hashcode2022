from dataclasses import dataclass
from typing import Optional
from copy import deepcopy
from operator import attrgetter

@dataclass
class Developer:
    skills: dict[str, int]
    name: str
    available: int = 0


@dataclass
class Project:
    points: int
    deadline: int
    duration: int
    requirements: list[str, int, Optional[Developer]]  # (skill type, skill level)
    name: str


@dataclass
class ScheduledProject:
    project_name: str
    developers: list[str]

def get_line(file):
    return file.readline().rstrip("\n")

def parse(file: str) -> tuple[list[Project], list[Developer]]:
    f = open(f"input/{file}.in.txt")

    # This is all you need for most problems.
    num_contributors, num_projects = [int(s) for s in get_line(f).split(" ")]  # read a line with a single integer

    # Read all contributor info
    contributors = list()
    for contrib_specification in range(num_contributors):
        name, num_skills = [str(s) for s in get_line(f).split(" ")]
        num_skills = int(num_skills)

        skills = dict()
        for skill_specification in range(num_skills):
            skill_name, skill_level = [str(s) for s in get_line(f).split(" ")]
            skill_level = int(skill_level)
            skills[skill_name] = skill_level

        contributor = Developer(skills=skills, name=name)
        contributors.append(contributor)

    # Read all project info
    projects = list()
    for project_specification in range(num_projects):
        project_name, project_duration_days, project_score, project_best_before, project_num_roles = [str(s) for s in
                                                                                                      get_line(f).split(
                                                                                                          " ")]
        project_duration_days = int(project_duration_days)
        project_score = int(project_score)
        project_best_before = int(project_best_before)
        project_num_roles = int(project_num_roles)

        requirements = []
        for skill_specification in range(project_num_roles):
            skill_name, skill_level = [str(s) for s in get_line(f).split(" ")]
            skill_level = int(skill_level)
            requirements.append([skill_name, skill_level, None])

        project = Project(points=project_score, deadline=project_best_before, requirements=requirements, duration=project_duration_days, name=project_name)
        projects.append(project)

    f.close()
    return projects, contributors

def write_output(file, scheduled_projects:list):
    f = open(f'output/{file}.out.txt', 'w')
    f.write(f"{len(scheduled_projects)}\n")
    for scheduled_project in scheduled_projects:
        f.write(f'{scheduled_project.project_name}\n')
        f.write(f'{" ".join(scheduled_project.developers)}\n')
    f.close()


# def big_dumdum(projects: list[Project], developers: list[Developer]):
#     scheduled_projects = []
#     for project in projects:
#         indices = get_devs_for_project_simple(0, project, developers, None)
#         if indices is None:
#             continue
#         # indices = indices[::-1]
#         # for idx in indices:
#         #     print(f"{developers[idx].name} assign to project {project.name}")
#         #     del developers[idx]
#
#         scheduled_devs = []
#         for idx in indices:
#             scheduled_devs.append(developers[idx].name)
#
#         i = 0
#         for idx in indices:
#             del developers[idx-i]
#             i += 1
#
#         scheduled_projects.append(ScheduledProject(project.name, scheduled_devs))
#
#     return scheduled_projects

def get_developer_skill_map(developers: list[Developer]):
    skill_map = {}
    for developer in developers:
        for skill, level in developer.skills.items():
            if skill in skill_map:
                skill_map[skill].append(developer)
            else:
                skill_map[skill] = [developer]

    for item in skill_map:
        skill_map[item].sort(key=lambda x: x.skills[item])

    return skill_map


def search_skill_map(skill_map, skill: str, level: int, exclude: list[Developer], start_day):
    if level == 0:
        for sk, item in skill_map.items():
            if sk == skill:
                continue
            for dev in item:
                if dev.available < start_day or dev in exclude:
                    continue
                return dev

    for dev in skill_map[skill]:
        if dev.available < start_day or dev in exclude:
            continue
        if dev.skills[skill] >= level:
            return dev
    return None


def small_dumdum(projects: list[Project], developers: list[Developer]):
    scheduled_projects = []
    finish_dates = [0]  # Projects still working on (days they will be finished)
    available = [0]*len(developers)  # When all of the devs will be available again
    current_day = 0

    skill_map = get_developer_skill_map(developers)

    while True:
        step = min(finish_dates)  # project that's finished earliest
        current_day += step
        finish_dates = [t - step for t in finish_dates if step > t]
        to_remove = []

        for p_idx, project in enumerate(projects):
        # loop over projects with heuristic
        # to_check = deepcopy(projects)
        # while to_check:
        #     project, remove_idx = get_least_contributors_project(to_check)
        #     to_check.pop(remove_idx)
            devs = get_devs_for_project_multiple(current_day, project, skill_map)

            if devs is None:
                continue

            to_remove.append(p_idx)
            scheduled_devs = []
            for s_idx, dev in enumerate(devs):
                dev.available = current_day + project.duration
                project.requirements[s_idx][2] = dev
                scheduled_devs.append(dev.name)
                try_learn(dev, project)

            finish_dates.append(current_day + project.duration)
            scheduled_projects.append(ScheduledProject(project.name, scheduled_devs))

        # remove all projects in progress as they are of no use in the system
        for idx in to_remove[::-1]:
            del projects[idx]

        # remove all projects past their deadline
        for idx, project in enumerate(projects):
            if current_day + project.duration > project.deadline + 10:
                del projects[idx]

        if len(finish_dates) == 0:
            break

    return scheduled_projects


def get_devs_for_project_multiple(start_day: int, project: Project, skill_map) -> Optional[list[Developer]]:
    devs = []
    count = 0
    aggregate = {}

    # TODO: check for 1 skill level
    for s_idx, (skill, level, _) in enumerate(project.requirements):

        if skill in aggregate and aggregate[skill] > level:
            level = level - 1

        dev = search_skill_map(skill_map, skill, level, devs, start_day)
        if dev is not None:

            for n_skill, n_level in dev.skills.items():
                if n_skill in aggregate:
                    aggregate[n_skill] = max(aggregate[n_skill], n_level)
                else:
                    aggregate[n_skill] = n_level

            devs.append(dev)
            count += 1

    return devs if len(project.requirements) == count else None


def preproces(developers: list[Developer]) -> dict[str, list[int]]:
    skills = {}
    for developer in developers:
        for skill, level in developer.skills:
            if skill in skills:
                for lv in range(level):  # Off by one err?
                    skills[skill][lv] += 1
            else:
                skills = [0] * 10

def most_constrained_heuristic(project: Project, data: dict[str, list[int]]):
    minimum = 0
    for skill, level, _ in project.requirements:
        minimum = min(data[skill][level], minimum)

# find project that requires most contributors
def get_most_contributors_project(all_projects: list[Project]):
    return max(all_projects, key=len(attrgetter('requirements')))

# find project that requires least contributors
def get_least_contributors_project(all_projects: list[Project]):
    least = all_projects[0]
    index = 0
    for idx, project in enumerate(all_projects):
        if len(project.requirements) < len(least.requirements):
            least = project
            index = idx
    return least, index
# find project that requires least contributors
def get_least_contributors_project(all_projects: list[Project]):
    least = all_projects[0]
    index = 0
    for idx, project in enumerate(all_projects):
        if len(project.requirements) < len(least.requirements):
            least = project
            index = idx
    return least, index
def try_learn(dev: Developer, project: Project):
    requirements = project.requirements
    for entry in requirements:
        if entry[2] is not None and entry[2].name == dev.name:
            skill = entry[0]
            level = entry[1]
            if skill not in dev.skills:
                dev.skills[skill] = 1
            if dev.skills[skill] <= level:
                dev.skills[skill] += 1
            break

files = ["a_an_example", "b_better_start_small", "c_collaboration", "d_dense_schedule", "e_exceptional_skills", "f_find_great_mentors"]
# files = ["a_an_example"]
# files = ["b_better_start_small"]
# files = ["c_collaboration"]
# files = ["d_dense_schedule"]
# files = ["e_exceptional_skills"]
# files = ["f_find_great_mentors"]

for file in files:

    print(f"Generating output for {file}")
    projects, developers = parse(file)

    if file in ["e_exceptional_skills"]:
        projects = sorted(projects, key=lambda project: project.deadline)  # Integer sort
    if file in ["c_collaboration"]:
        projects = sorted(projects, key=lambda project: project.points, reverse=True)  # Integer sort
    if file in ["f_find_great_mentors"]:
        projects = sorted(projects, key=lambda project: project.duration)  # Integer sort
    # projects = sorted(projects, key=lambda project: len(project.requirements))  # Integer sort

    developers = sorted(developers, key=lambda developer: len(developer.skills))

    # scheduled_projects = big_dumdum(projects, developers)
    scheduled_projects = small_dumdum(projects, developers)
    write_output(file, scheduled_projects)
    # break
pass
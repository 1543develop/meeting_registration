from openpyxl import load_workbook
import os

PATH = os.path.dirname(os.path.realpath(__file__))
SCHEDULE_PATH = PATH + "/teachers_schedule.xlsx"


def parse_row(row):
    set_of_grades = set()
    for i in range(3, len(row)):
        if row[i] is None:
            continue
        set_of_grades.add(row[i].replace(" ", ""))
    name = row[1].replace(". ", ".").replace(".", ". ", 1)
    list_of_grades = list(set_of_grades)
    list_of_grades.sort()
    info = {"name": name, "subject": row[2], "list_of_grades": list_of_grades}
    return info


def parse_teachers():
    wb = load_workbook(SCHEDULE_PATH)
    ws = wb.active

    teachers_list = []
    for row in ws.values:
        if row[0] is None:
            continue
        teachers_list.append(parse_row(row))

    return teachers_list


def get_teachers_by_class(teachers_list, _class):
    teachers_of_class = []
    for teacher in teachers_list:
        if _class in teacher["list_of_grades"]:
            teachers_of_class.append(teacher)
    return teachers_of_class


if __name__ == '__main__':
    teachers = parse_teachers()
    _class = input().upper()
    class_teachers = get_teachers_by_class(teachers, _class)
    for t in class_teachers:
        print(t)

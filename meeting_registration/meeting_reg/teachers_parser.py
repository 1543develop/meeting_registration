from openpyxl import load_workbook
import os

PATH = os.path.dirname(os.path.realpath(__file__))
SCHEDULE_PATH = PATH + "/teachers_schedule.xlsx"


def parse_grade_name(grade_name):
    num = ""
    grade_letters = []
    for letter in grade_name:
        if letter.isnumeric():
            num += letter
        elif letter.isalpha():
            grade_letters.append(letter)
    return num, grade_letters


def parse_row(row):
    set_of_grades = get_set_of_grades_in_row(row)
    name = row[1].replace(". ", ".").replace(".", ". ", 1)
    list_of_grades = list(set_of_grades)
    list_of_grades.sort()
    info = {"name": name, "subject": row[2], "list_of_grades": list_of_grades}
    return info


def get_set_of_grades_in_row(row):
    set_of_grades = set()
    for i in range(3, len(row)):
        if row[i] is None:
            continue
        num, grade_letters = parse_grade_name(row[i].replace(" ", ""))
        for grade_letter in grade_letters:
            set_of_grades.add(num + grade_letter)
    return set_of_grades


# def all_grades():
#     wb = load_workbook(SCHEDULE_PATH)
#     ws = wb.active
#
#     grades = set()
#     for row in ws.values:
#         if row[0] is None:
#             continue
#         grades.add(get_set_of_grades_in_row(row))
#
#     return grades


def parse_teachers():
    wb = load_workbook(SCHEDULE_PATH)
    ws = wb.active

    teachers_list = []
    for row in ws.values:
        if row[0] is None:
            continue
        teachers_list.append(parse_row(row))

    return teachers_list


def switch_latin_to_cyrillic(string: str):
    return string.replace("A", "А").replace("B", "В")


def filter_teachers_by_grade(teachers_list, grade_raw):
    grade = switch_latin_to_cyrillic(grade_raw)
    teachers_of_grade = []
    for teacher in teachers_list:
        if grade in teacher["list_of_grades"]:
            teachers_of_grade.append(teacher)
    return teachers_of_grade


# def is_valid_grade(request, grade):
#     if grade in get_set_of_grades_in_row():
#         return True
#     else:
#         return False


if __name__ == '__main__':
    teachers = parse_teachers()
    grade_ = input().upper()
    class_teachers = filter_teachers_by_grade(teachers, grade_)
    print(class_teachers)

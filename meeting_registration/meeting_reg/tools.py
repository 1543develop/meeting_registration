months_genitive = {
    0: "января",
    1: "февраля",
    2: "марта",
    3: "апреля",
    4: "мая",
    5: "июня",
    6: "июля",
    7: "августа",
    8: "сентября",
    9: "октября",
    10: "ноября",
    11: "декабря",
}


def parse_date(date):
    """
    Args:
        date:
            "04/05/2020"
    Returns:
        tuple(4, 5, 2020)
    """
    return int(date[:2]), int(date[3:5]), int(date[6:])


def beautiful_date(day=None, month=None, year=None):
    return " ".join([str(x) for x in (day, months_genitive[month - 1], year) if x is not None])


if __name__ == '__main__':
    print(beautiful_date(1, 2))

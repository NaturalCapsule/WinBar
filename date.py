from datetime import date
import calendar


def get_calendar():
    today = date.today()
    date1 = today.strftime('%d/%m/%Y')
    splits = date1.split('/')

    day = splits[0]

    month = splits[1]
    year = splits[2]

    year = int(year)
    month = int(month)

    return f"Current day of the month: {day}th.\n\n{calendar.month(year, month)}"
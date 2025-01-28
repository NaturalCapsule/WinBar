import calendar
from datetime import datetime


def load_css():
    with open("config/style.css", "r") as f:
        return f"<style>{f.read()}</style>"


def get_calendar_html():
    today = datetime.today()
    current_year = today.year
    current_month = today.month
    current_day = today.day

    css = load_css()

    html = f"""
    {css}
    <div id="SideDate">
        <h2 style="text-align:center;">{calendar.month_name[current_month]} {current_year}</h2>
        <table>
            <thead>
                <tr>
                    {"".join([f"<th>{day}</th>" for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']])}
                </tr>
            </thead>
            <tbody>
    """

    cal = calendar.Calendar()
    month_days = cal.monthdayscalendar(current_year, current_month)
    for week in month_days:
        html += "<tr>"
        for day in week:
            if day == 0:
                html += "<td></td>"
            elif day == current_day:
                html += f"<td class='current-day'>{day}</td>"
            else:
                html += f"<td>{day}</td>"
        html += "</tr>"
    html += """
            </tbody>
        </table>
    </div>
    """

    return html
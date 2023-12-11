from flask import Blueprint, current_app, render_template, request, redirect, url_for
import datetime
import uuid
from collections import defaultdict

pages = Blueprint("habits", __name__, template_folder="templates", static_folder="static")
# habits = ["test habit"]
# completions = defaultdict(list)

@pages.context_processor
def add_calc_date_range():
    def date_range(start: datetime.datetime):
        dates = [start+datetime.timedelta(days=diff) for diff in range(-3,4)]
        #date in range +3 days -3 days
        return dates
    return {"date_range":date_range}

def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)

@pages.route("/")
def index():
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        # selected_date = datetime.datetime.today()
        selected_date = today_at_midnight()

    habits_on_date = current_app.db.habits.find({"added":{"$lte":selected_date}})

    completions = [
        habit["habit"]
        for habit in current_app.db.completions.find({"date": selected_date})
    ]

    return render_template("index.html", habits=habits_on_date, title="Habit Tracker - Home", selected_date=selected_date,completions=completions)

@pages.route("/add", methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()
    if request.form:
        # habits.append(request.form.get("habit"))
        current_app.db.habits.insert_one(
            {"id":uuid.uuid4().hex, "added":today, "name":request.form.get("habit")}
        )
    return render_template("add_habit.html", title="Habit Tracker - Add Habit", selected_date=today,)

@pages.route("/complete/", methods=["POST"])
def complete():
    date_string = request.form.get("date")
    habit = request.form.get("habitId")
    date = datetime.datetime.fromisoformat(date_string)
    # completions[date].append(habit)
    habit = request.form.get("habitId")

    current_app.db.completions.insert_one({"date":date, "habit":habit})

    return redirect(url_for(".index", date=date_string))
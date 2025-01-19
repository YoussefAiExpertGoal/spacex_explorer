from flask import Blueprint, render_template, abort
from app.models.spacex_models import DataManager
from app import cache

main = Blueprint('main', __name__)
data_manager = DataManager()

@main.route('/')
@cache.cached(timeout=300)
def index():
    try:
        latest_mission = data_manager.fetch_latest_mission()
        return render_template('index.html', mission=latest_mission)
    except Exception as e:
        return render_template('index.html', error=str(e))

@main.route('/missions')
@cache.cached(timeout=300)
def missions():
    try:
        all_missions = data_manager.fetch_all_missions()
        return render_template('missions.html', missions=all_missions)
    except Exception as e:
        return render_template('missions.html', error=str(e))

@main.route('/crew')
@cache.cached(timeout=300)
def crew():
    try:
        crew_members = data_manager.fetch_all_crew()
        return render_template('crew.html', crew_members=crew_members)
    except Exception as e:
        print(f"Error in crew route: {str(e)}")  # This will show in your Flask console
        return render_template('crew.html', error=str(e))
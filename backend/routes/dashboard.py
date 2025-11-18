from flask import Blueprint, render_template
from database.db_init import get_session
from database.models import Sensor, Measurement

dashboard_bp = Blueprint('dashboard', __name__, template_folder='../templates')


@dashboard_bp.route('/')
def dashboard():
    session = get_session()
    sensors = session.query(Sensor).all()
    return render_template('dashboard.html', sensors=sensors)


@dashboard_bp.route('/sensors/<int:sensor_id>')
def sensor_table(sensor_id):
    session = get_session()
    measurements = session.query(Measurement).filter(Measurement.sensor_id == sensor_id).order_by(Measurement.timestamp.desc()).all()
    return render_template('sensor_table.html', measurements=measurements)

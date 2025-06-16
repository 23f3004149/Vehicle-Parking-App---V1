from flask import Blueprint, render_template,request,redirect,flash,url_for
from flask_login import login_required,current_user
from decorators import user_required

from models import db, ParkingLot, Reservation
from datetime import datetime

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@user_required
def dashboard():
    # Filters
    state = request.args.get('state')
    city = request.args.get('city')
    search = request.args.get('search')

    lots_query = ParkingLot.query

    if state:
        lots_query = lots_query.filter(ParkingLot.state.ilike(f'%{state}%'))
    if city:
        lots_query = lots_query.filter(ParkingLot.city.ilike(f'%{city}%'))
    if search:
        lots_query = lots_query.filter(
            (ParkingLot.prime_location_name.ilike(f'%{search}%')) |
            (ParkingLot.pin_code.ilike(f'%{search}%'))
        )

    filtered_lots = lots_query.all()

    # Get active reservation (if any)
    active_reservation = Reservation.query.filter_by(user_id=current_user.id, leaving_timestamp=None).first()

    return render_template(
        'user/dashboard.html',
        user=current_user,
        lots=filtered_lots,
        active_reservation=active_reservation,
        filters={'state': state, 'city': city, 'search': search}
    )

@user_bp.route('/release/<int:reservation_id>', methods=['POST'])
@login_required
def release_spot(reservation_id):
    # 1. Get the reservation
    reservation = Reservation.query.get(reservation_id)

    # 2. Handle missing reservation
    if not reservation:
        flash("Reservation not found.", "warning")
        return redirect(url_for('user.dashboard'))

    # 3. Make sure it belongs to the current user
    if reservation.user_id != current_user.id:
        flash("Unauthorized access.", "danger")
        return redirect(url_for('user.dashboard'))

    # 4. Mark the reservation as released
    reservation.leaving_timestamp = datetime.utcnow()
    reservation.spot.status = 'A'  # Mark the spot as available
    db.session.commit()

    flash("Spot released successfully!", "success")
    return redirect(url_for('user.dashboard'))

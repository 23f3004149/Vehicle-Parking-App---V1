from flask import Blueprint, render_template,request,redirect,flash,url_for
from flask_login import login_required,current_user
from decorators import user_required

from models import db, ParkingLot, Reservation,ParkingSpot,City
from datetime import datetime
from sqlalchemy import or_

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/dashboard', methods=['GET'])
@login_required
@user_required
def dashboard():
    search = request.args.get('search', '').strip().lower()
    state = request.args.get('state', '').strip().lower()
    city = request.args.get('city', '').strip().lower()

    # Base query
    query = ParkingLot.query.join(City).filter(True)

    # Apply filters
    if search:
        query = query.filter(
            or_(
                ParkingLot.prime_location_name.ilike(f"%{search}%"),
                ParkingLot.pin_code.ilike(f"%{search}%")
            )
        )
    if state:
        query = query.filter(City.state.ilike(f"%{state}%"))
    if city:
        query = query.filter(City.name.ilike(f"%{city}%"))

    lots = query.all()

    # Fetch all states and cities for filter dropdowns
    states = [row[0] for row in db.session.query(City.state).distinct().all()]
    cities = [row[0] for row in db.session.query(City.name).distinct().all()]

    return render_template(
        'user/dashboard.html',
        lots=lots,
        user=current_user,
        filters={
            'search': search,
            'state': state,
            'city': city
        },
        states=states,
        cities=cities
    )

@user_bp.route('/reserve/<int:lot_id>', methods=['POST'])
@login_required
@user_required
def reserve_spot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)

    # Step 1: Get and sanitize vehicle number
    vehicle_number = request.form.get('vehicle_number', '').strip().upper()
    if not vehicle_number:
        flash("Please enter a vehicle number.", "danger")
        return redirect(url_for('user.dashboard'))

    # Step 2: Check for same vehicle already booked in this lot
    duplicate_reservation = (
        db.session.query(Reservation)
        .join(ParkingSpot)
        .filter(
            Reservation.user_id == current_user.id,
            Reservation.vehicle_number == vehicle_number,
            Reservation.is_active == True,
            ParkingSpot.lot_id == lot_id
        )
        .first()
    )
    if duplicate_reservation:
        flash("This vehicle already has an active reservation in this lot.", "warning")
        return redirect(url_for('user.dashboard'))

    # Step 3: Find available spot
    spot = ParkingSpot.query.filter_by(lot_id=lot.id, status='A').first()
    if not spot:
        flash("No available spots in this lot.", "danger")
        return redirect(url_for('user.dashboard'))

    # Step 4: Reserve
    spot.status = 'O'
    reservation = Reservation(
        spot_id=spot.id,
        user_id=current_user.id,
        vehicle_number=vehicle_number,
        parking_timestamp=datetime.utcnow(),
        is_active=True
    )
    db.session.add(reservation)
    db.session.commit()

    flash(f"Spot {spot.id} reserved successfully for vehicle {vehicle_number}.", "success")
    return redirect(url_for('user.dashboard'))


@user_bp.route('/release/<int:reservation_id>', methods=['POST'])
@login_required
@user_required
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
    reservation.is_active = False  # ✅ Mark reservation as inactive
    
    duration = reservation.leaving_timestamp - reservation.parking_timestamp
    hours = duration.total_seconds() / 3600
    hourly_rate = reservation.spot.lot.price_per_hour
    reservation.parking_cost = round(hours * hourly_rate, 2)

    db.session.commit()

    flash("Spot released successfully!", "success")
    return redirect(url_for('user.my_reservations'))


@user_bp.route('/my-reservations')
@login_required
@user_required
def my_reservations():
    active_reservations = (
        Reservation.query
        .join(ParkingSpot)
        .join(ParkingLot)
        .filter(
            Reservation.user_id == current_user.id,
            Reservation.is_active == True,
            Reservation.leaving_timestamp == None
        )
        .order_by(Reservation.parking_timestamp.desc())
        .all()
    )

    now = datetime.utcnow()
    active_data = []
    for res in active_reservations:
        duration = now - res.parking_timestamp
        total_minutes = int(duration.total_seconds() // 60)
        hours = total_minutes // 60
        minutes = total_minutes % 60

        # Minimum 1 hour charge, then per minute after
        price_per_hour = res.spot.lot.price_per_hour
        if hours == 0 and minutes <= 60:
            cost = price_per_hour
        else:
            per_minute_rate = price_per_hour / 60
            cost = round(total_minutes * per_minute_rate)

        duration_str = f"{hours} hour(s) {minutes} minute(s)"
        active_data.append({
            'reservation': res,
            'duration_str': duration_str,
            'final_cost': cost
        })

    # Completed Reservations
    completed_reservations = (
        Reservation.query
        .filter_by(user_id=current_user.id, is_active=False)
        .order_by(Reservation.leaving_timestamp.desc())
        .all()
    )

    return render_template(
        'user/my_reservations.html',
        active_data=active_data,
        completed_reservations=completed_reservations
    )


    # Completed Reservations
    completed_reservations = (
        Reservation.query
        .join(ParkingSpot)
        .join(ParkingLot)
        .filter(
            Reservation.user_id == current_user.id,
            Reservation.is_active == False,
            Reservation.leaving_timestamp != None
        )
        .order_by(Reservation.leaving_timestamp.desc())
        .all()
    )

    return render_template(
        'user/my_reservations.html',
        active_data=active_data,
        completed_reservations=completed_reservations
    )

@user_bp.route('/summary')
@login_required
@user_required
def summary():
    reservations = Reservation.query.filter_by(user_id=current_user.id).order_by(Reservation.parking_timestamp.desc()).all()

    total_reservations = len(reservations)
    active_reservations = sum(1 for r in reservations if r.is_active)
    total_spent = sum(r.parking_cost for r in reservations if r.parking_cost)

    # Revenue by lot (for this user)
    from sqlalchemy import func
    lot_revenue_data = (
        db.session.query(
            ParkingLot.prime_location_name,
            func.sum(Reservation.parking_cost)
        )
        .join(ParkingSpot, ParkingSpot.id == Reservation.spot_id)
        .join(ParkingLot, ParkingLot.id == ParkingSpot.lot_id)
        .filter(Reservation.user_id == current_user.id)
        .filter(Reservation.is_active == False)
        .group_by(ParkingLot.prime_location_name)
        .all()
    )

    lot_names = [lot for lot, _ in lot_revenue_data]
    lot_revenues = [round(revenue or 0, 2) for _, revenue in lot_revenue_data]

    return render_template('user/summary.html',
                           reservations=reservations,
                           total_reservations=total_reservations,
                           active_reservations=active_reservations,
                           total_spent=total_spent,
                           lot_names=lot_names,
                           lot_revenues=lot_revenues)

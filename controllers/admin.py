from flask import Blueprint, render_template, request, redirect, flash, url_for
from flask_login import login_required, current_user
from models import db, ParkingLot, ParkingSpot, User, Reservation, City
from decorators import admin_required
from datetime import datetime
from sqlalchemy import func,or_

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
@admin_required
def dashboard():
    search = request.args.get('search', '').strip().lower()
    state = request.args.get('state', '').strip().lower()
    city = request.args.get('city', '').strip().lower()

    # Base query with join to City
    query = ParkingLot.query.join(City).filter(True)

    # Search by prime location or pincode
    if search:
        query = query.filter(
            db.or_(
                ParkingLot.prime_location_name.ilike(f"%{search}%"),
                ParkingLot.pin_code.ilike(f"%{search}%")
            )
        )

    # Filter by state
    if state:
        query = query.filter(City.state.ilike(f"%{state}%"))

    # Filter by city
    if city:
        query = query.filter(City.name.ilike(f"%{city}%"))

    lots = query.all()

    # Get list of all states and cities for dropdowns
    states = [row[0] for row in db.session.query(City.state).distinct().all()]
    cities = [row[0] for row in db.session.query(City.name).distinct().all()]

    return render_template(
        'admin/dashboard.html',
        lots=lots,
        filters={
            'search': search,
            'state': state,
            'city': city
        },
        states=states,
        cities=cities
    )

# Create a new parking lot
@admin_bp.route('/create-lot', methods=['GET', 'POST'])
@login_required
@admin_required
def create_lot():
    cities = City.query.all()

    if request.method == 'POST':
        name = request.form['prime_location_name']
        address = request.form['address']
        city_id = request.form['city_id']
        pin_code = request.form['pin_code']
        price = float(request.form['price_per_hour'])
        max_spots = int(request.form['max_spots'])

        # Create the parking lot
        new_lot = ParkingLot(
            prime_location_name=name,
            address=address,
            city_id=city_id,
            pin_code=pin_code,
            price_per_hour=price,
            max_spots=max_spots
        )

        db.session.add(new_lot)
        db.session.flush()  # Get new_lot.id before commit

        # Auto-create empty spots
        for _ in range(max_spots):
            new_spot = ParkingSpot(lot_id=new_lot.id)
            db.session.add(new_spot)

        db.session.commit()
        flash('Parking lot created successfully with spots!')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/create_lot.html', cities=cities)


# Edit Parking Lot
@admin_bp.route('/edit-lot/<int:lot_id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    cities = City.query.all()

    if request.method == 'POST':
        lot.prime_location_name = request.form['prime_location_name']
        lot.address = request.form['address']
        lot.pin_code = request.form['pin_code']
        lot.price_per_hour = float(request.form['price_per_hour'])
        lot.max_spots = int(request.form['max_spots'])
        lot.city_id = int(request.form['city_id'])

        db.session.commit()
        flash('Parking lot updated successfully!', 'success')
        return redirect(url_for('admin.dashboard'))

    return render_template('admin/edit_lot.html', lot=lot, cities=cities)

# Delete Parking Lot
@admin_bp.route('/lots/<int:lot_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)


    active_reservation = (
        db.session.query(Reservation)
        .join(ParkingSpot)
        .filter(ParkingSpot.lot_id == lot.id, Reservation.leaving_timestamp == None)
        .first()
    )

    if active_reservation:
        flash("Cannot delete lot: some spots have active reservations.", "danger")
        return redirect(url_for('admin.dashboard'))

    db.session.delete(lot)
    db.session.commit()

    flash("Lot deleted successfully.")
    return redirect(url_for('admin.dashboard'))

# View spots under a lot
@admin_bp.route('/lots/<int:lot_id>/spots')
@login_required
@admin_required
def view_lot(lot_id):
    lot = ParkingLot.query.get_or_404(lot_id)
    filter_type = request.args.get('filter')

    all_spots = ParkingSpot.query.filter_by(lot_id=lot.id).all()

    if filter_type == 'available':
        spots = [spot for spot in all_spots if not spot.reservation]
    elif filter_type == 'occupied':
        spots = [spot for spot in all_spots if spot.reservation]
    else:
        spots = all_spots

    now = datetime.utcnow()
    return render_template('admin/view_spots.html', lot=lot, spots=spots, now=now, filter=filter_type)

# View all registered users

@admin_bp.route('/users')
@login_required
@admin_required
def view_users():
    search = request.args.get('search', '').strip().lower()

    query = User.query
    if search:
        query = query.filter(
            or_(
                User.full_name.ilike(f"%{search}%"),
                User.username.ilike(f"%{search}%"),
                User.email.ilike(f"%{search}%")
            )
        )

    users = query.all()
    return render_template('admin/user_list.html', users=users, search=search)

@admin_bp.route('/summary')
@login_required
@admin_required
def summary():
    # Count Data
    total_lots = ParkingLot.query.count()
    total_spots = ParkingSpot.query.count()
    total_users = User.query.filter_by(role='user').count()

    # Revenue by Parking Lot
    revenue_data = (
        db.session.query(
            ParkingLot.prime_location_name,
            func.coalesce(func.sum(Reservation.parking_cost), 0)
        )
        .join(ParkingSpot, ParkingSpot.lot_id == ParkingLot.id)
        .join(Reservation, Reservation.spot_id == ParkingSpot.id)
        .filter(Reservation.is_active == False)
        .group_by(ParkingLot.prime_location_name)
        .all()
    )

    chart_labels = [lot for lot, _ in revenue_data]
    chart_values = [revenue for _, revenue in revenue_data]

    # Spot availability summary
    total_available = ParkingSpot.query.filter_by(status='A').count()
    total_occupied = ParkingSpot.query.filter_by(status='O').count()

    # All reservations (with duration & status)
    reservations = Reservation.query.order_by(Reservation.parking_timestamp.desc()).all()

    return render_template(
        'admin/summary.html',
        total_lots=total_lots,
        total_spots=total_spots,
        total_users=total_users,
        chart_labels=chart_labels,
        chart_values=chart_values,
        available=total_available,
        occupied=total_occupied,
        reservations=reservations
    )

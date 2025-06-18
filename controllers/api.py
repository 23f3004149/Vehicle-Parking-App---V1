from flask import Blueprint, jsonify
from models import db, ParkingLot, ParkingSpot, Reservation

api_bp = Blueprint('api', __name__, url_prefix='/api')

def error_response(message, code=404):
    return jsonify({'error': message}), code

@api_bp.route('/lots', methods=['GET'])
def get_all_lots():
    lots = ParkingLot.query.all()
    if not lots:
        return error_response("No parking lots found.")

    data = []
    for lot in lots:
        data.append({
            'id': lot.id,
            'prime_location_name': lot.prime_location_name,
            'address': lot.address,
            'pin_code': lot.pin_code,
            'city': {
                'name': lot.city.name,
                'state': lot.city.state
            },
            'price_per_hour': lot.price_per_hour,
            'max_spots': lot.max_spots,
            'available_spots': lot.available_spots(),
            'occupied_count': lot.occupied_count()
        })
    return jsonify({'lots': data}), 200


@api_bp.route('/lots/<int:lot_id>/spots', methods=['GET'])
def get_spots(lot_id):
    lot = ParkingLot.query.get(lot_id)
    if not lot:
        return error_response(f"Parking lot with ID {lot_id} not found.", 404)

    if not lot.spots:
        return error_response(f"No parking spots found in lot ID {lot_id}.", 404)

    data = []
    for spot in lot.spots:
        data.append({
            'id': spot.id,
            'status': 'Occupied' if spot.is_occupied else 'Available',
            'lot_id': lot.id,
            'lot_name': lot.prime_location_name,
            'created_at': spot.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'is_reserved': spot.reservation is not None
        })
    
    return jsonify({
        'lot_id': lot.id,
        'lot_name': lot.prime_location_name,
        'total_spots': len(lot.spots),
        'spots': data
    }), 200



@api_bp.route('/reservations', methods=['GET'])
def get_all_reservations():
    reservations = Reservation.query.all()
    if not reservations:
        return error_response("No reservations found.")

    data = []
    for res in reservations:
        data.append({
            'id': res.id,
            'user_id': res.user_id,
            'username': res.user.username,
            'spot_id': res.spot_id,
            'lot_id': res.spot.lot_id,
            'lot_name': res.spot.lot.prime_location_name,
            'vehicle_number': res.vehicle_number,
            'is_active': res.is_active,
            'parked_at': res.parking_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'left_at': res.leaving_timestamp.strftime('%Y-%m-%d %H:%M:%S') if res.leaving_timestamp else None,
            'cost': res.parking_cost
        })
    return jsonify({'reservations': data}), 200

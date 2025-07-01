from flask import Flask, render_template, render_template_string, request, redirect, url_for, flash

from datetime import datetime
from models import db, Room, Booking

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///meeting_rooms.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

def setup_database():
    """Create tables and default rooms if they don't exist."""
    db.create_all()
    if Room.query.count() == 0:
        for room_name in ["Room A", "Room B", "Room C"]:
            db.session.add(Room(name=room_name))
        db.session.commit()

with app.app_context():
    setup_database()

def is_overlapping(room_id, date, start, end):
    start_time = datetime.strptime(start, "%H:%M").time()
    end_time   = datetime.strptime(end, "%H:%M").time()
    bookings   = Booking.query.filter_by(room_id=room_id, date=date).all()
    for b in bookings:
        b_start = datetime.strptime(b.start, "%H:%M").time()
        b_end   = datetime.strptime(b.end,   "%H:%M").time()
        if start_time < b_end and end_time > b_start:
            return True
    return False

@app.route('/')
def index():
    rooms    = Room.query.all()
    bookings = {r.id: Booking.query.filter_by(room_id=r.id).all() for r in rooms}
    return render_template('index.html', rooms=rooms, bookings=bookings)

@app.route('/book/<int:room_id>', methods=['GET', 'POST'])
def book(room_id):
    room    = Room.query.get_or_404(room_id)
    preview = None

    if request.method == 'POST':
        date            = request.form.get('date')
        start           = request.form.get('start')
        end             = request.form.get('end')
        booked_by_input = request.form.get('booked_by')
        action          = request.form.get('action')  # "preview" or "confirm"

        # basic validation
        if not all([date, start, end, booked_by_input]):
            flash("All fields are required.", "error")
            return redirect(url_for('book', room_id=room.id))

        if start >= end:
            flash("End time must be after start time.", "error")
            return redirect(url_for('book', room_id=room.id))

        if action == 'preview':
            try:
                rendered_name = render_template_string(booked_by_input)
            except Exception as e:
                rendered_name = f"[Error rendering name: {e}]"

            preview = {
                'date':       date,
                'start':      start,
                'end':        end,
                'booked_by':  rendered_name
            }

            return render_template(
                'book.html',
                room=room,
                preview=preview,
                form_data=request.form
            )

        elif action == 'confirm':
            if is_overlapping(room.id, date, start, end):
                flash("This time slot is already booked.", "error")
                return redirect(url_for('book', room_id=room.id))

            booking = Booking(
                room_id=room.id,
                date=date,
                start=start,
                end=end,
                booked_by=booked_by_input
            )
            db.session.add(booking)
            db.session.commit()

            flash(f"Room {room.name} booked successfully!", "success")
            return redirect(url_for('index'))

    return render_template('book.html', room=room)

@app.route('/reset')
def reset():
    # WARNING: this will erase *all* bookings (and rooms) and start fresh
    db.drop_all()
    db.create_all()

    # re-seed the default rooms
    for room_name in ["Room A", "Room B", "Room C"]:
        db.session.add(Room(name=room_name))
    db.session.commit()

    flash("Database has been reset to its initial state.", "success")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

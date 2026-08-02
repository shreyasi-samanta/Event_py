from flask import Flask, render_template, request, redirect, session, flash
import mysql.connector
import razorpay
import os
import uuid
from decimal import Decimal
from razorpay.errors import BadRequestError
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "eventhub_secret_key"
RAZORPAY_KEY_ID = "rzp_test_SxuyN7oCphPRjZ"
RAZORPAY_KEY_SECRET = "mIi0aHnLcGa91b1fsotbSndP"
RAZORPAY_MAX_AMOUNT_PAISE = 50000000

client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)
UPLOAD_FOLDER = os.path.join(app.root_path, "static", "uploads")

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="event_py_db"
    )

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    password = request.form["password"]

    db = get_db_connection()
    cursor = db.cursor()

    hashed_password = generate_password_hash(password)

    sql = "INSERT INTO users(username, password) VALUES(%s,%s)"
    cursor.execute(sql, (username, hashed_password))

    db.commit()

    cursor.close()
    db.close()

    return redirect("/")

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]
    password = request.form["password"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    sql = "SELECT * FROM users WHERE username=%s AND password=%s"

    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    db.close()

    if user and check_password_hash(user["password"], password):

        session["user_id"] = user["id"]
        session["username"] = user["username"]
        session["role"] = user["role"]

        if user["role"] == "admin":
            return redirect("/dashboard")

        else:
            return redirect("/user/dashboard")

    else:
        flash("Invalid Username or Password")
        return redirect("/")
@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "admin":
        return redirect("/events")

    db = get_db_connection()
    cursor = db.cursor()

    # Total Users (excluding admin)
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='user'")
    total_users = cursor.fetchone()[0]

    # Total Events
    cursor.execute("SELECT COUNT(*) FROM events")
    total_events = cursor.fetchone()[0]

    # Total Bookings
    cursor.execute("SELECT COUNT(*) FROM bookings")
    total_bookings = cursor.fetchone()[0]

    # Recent Bookings for admin dashboard
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT
            bookings.id,
            users.username,
            events.name,
            bookings.event_date,
            events.price,
            bookings.no_of_people,
            bookings.contact_no
        FROM bookings
        JOIN events ON bookings.e_id = events.id
        JOIN users ON bookings.uid = users.id
        ORDER BY bookings.booking_date_time DESC
        LIMIT 10
    """)

    admin_bookings = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "admin/admin_dashboard.html",
        total_users=total_users,
        total_events=total_events,
        total_bookings=total_bookings,
        admin_bookings=admin_bookings
    )
@app.route("/admin/add-event", methods=["GET", "POST"])
def add_event():
    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "admin":
        return redirect("/user/dashboard")

    if request.method == "POST":
        name = request.form["name"]
        description = request.form["description"]
        location = request.form["location"]
        date = request.form["date"]
        price = request.form["price"]
        image = request.files["image"]

        filename = secure_filename(image.filename)
        image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

        db = get_db_connection()
        cursor = db.cursor()

        sql = """
       INSERT INTO events
(name, description, image, location, date, price)
VALUES(%s,%s,%s,%s,%s,%s)
        """

        values = (
            name,
            description,
            filename,
            location,
            date,
            price
        )

        cursor.execute(sql, values)
        db.commit()

        cursor.close()
        db.close()

        flash("Event Added Successfully")
        return redirect("/dashboard")

    return render_template("admin/add_event.html")
@app.route("/events")
def events():
    if "user_id" not in session:
        return redirect("/")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM events ORDER BY date ASC")
    events = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("events.html", events=events)

@app.route("/admin/view-events")
def view_events():

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "admin":
        return redirect("/events")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT * FROM events ORDER BY id DESC")

    events = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("admin/view_events.html", events=events)

@app.route("/logout")
def logout():

    session.clear()

    flash("Logged Out Successfully")

    return redirect("/")

@app.route("/admin/users")
def users_list():

    # Only admin can access
    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "admin":
        return redirect("/events")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT id, username, role
    FROM users
    ORDER BY id ASC
    """

    cursor.execute(sql)
    users = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template("admin/userslist.html", users=users)
@app.route("/user/dashboard")
def user_dashboard():

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "user":
        return redirect("/dashboard")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Total Bookings
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM bookings
        WHERE uid=%s
    """, (session["user_id"],))

    total_bookings = cursor.fetchone()["total"]

    # Total Investment
    cursor.execute("""
        SELECT IFNULL(SUM(events.price),0) AS investment
        FROM bookings
        JOIN events
        ON bookings.e_id = events.id
        WHERE bookings.uid=%s
    """, (session["user_id"],))

    total_investment = cursor.fetchone()["investment"]

    # Fetch all events
    cursor.execute("""
        SELECT *
        FROM events
        ORDER BY date ASC
    """)

    events = cursor.fetchall()

    # Recent Bookings
    cursor.execute("""
        SELECT events.name,
               events.price,
               events.date
        FROM bookings
        JOIN events
        ON bookings.e_id = events.id
        WHERE bookings.uid=%s
        ORDER BY bookings.booking_date_time DESC
        LIMIT 5
    """, (session["user_id"],))

    recent_bookings = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "users/user_dashboard.html",
        events=events,
        total_bookings=total_bookings,
        total_investment=total_investment,
        recent_bookings=recent_bookings
    )

@app.route("/admin/edit-event/<int:id>", methods=["GET", "POST"])
def edit_event(id):

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "admin":
        return redirect("/user/dashboard")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    if request.method == "POST":

        name = request.form["name"]
        description = request.form["description"]
        location = request.form["location"]
        date = request.form["date"]
        price = request.form["price"]

        image = request.files["image"]

        # New image uploaded
        if image and image.filename != "":

            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))

            sql = """
            UPDATE events
            SET name=%s,
                description=%s,
                location=%s,
                date=%s,
                price=%s,
                image=%s
            WHERE id=%s
            """

            values = (
                name,
                description,
                location,
                date,
                price,
                filename,
                id
            )

        else:

            sql = """
            UPDATE events
            SET name=%s,
                description=%s,
                location=%s,
                date=%s,
                price=%s
            WHERE id=%s
            """

            values = (
                name,
                description,
                location,
                date,
                price,
                id
            )

        cursor.execute(sql, values)

        db.commit()

        cursor.close()
        db.close()

        flash("Event Updated Successfully")

        return redirect("/admin/view-events")

    cursor.execute("SELECT * FROM events WHERE id=%s", (id,))

    event = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template("admin/edit_event.html", event=event)

@app.route("/admin/delete-event/<int:id>")
def delete_event(id):

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "admin":
        return redirect("/user/user_dashboard")

    db = get_db_connection()
    cursor = db.cursor()

    cursor.execute("DELETE FROM events WHERE id=%s", (id,))

    db.commit()

    cursor.close()
    db.close()

    flash("Event Deleted Successfully")

    return redirect("/admin/view-events")

@app.route("/my-bookings")
def my_bookings():

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "user":
        return redirect("/dashboard")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    sql = """
    SELECT
        bookings.id AS booking_id,
        bookings.booking_date_time,
        events.name,
        events.description,
        events.image,
        events.location,
        events.date,
        events.price

    FROM bookings

    INNER JOIN events
        ON bookings.e_id = events.id

    WHERE bookings.uid = %s

    ORDER BY bookings.booking_date_time DESC
    """

    cursor.execute(sql, (session["user_id"],))

    bookings = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "users/mybookings.html",
        bookings=bookings
    )

@app.route("/book/<int:event_id>")
def book_page(event_id):

    if "user_id" not in session:
        return redirect("/")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM events WHERE id=%s",
        (event_id,)
    )

    event = cursor.fetchone()

    cursor.close()
    db.close()

    return render_template(
        "users/book_event.html",
        event=event
    )

@app.route("/confirm-booking/<int:event_id>", methods=["POST"])
def confirm_booking(event_id):

    if "user_id" not in session:
        return redirect("/")
    
    action = request.form["action"]

    if action == "pay":
        return pay_online(event_id)

    event_date = request.form["event_date"]
    people = int(request.form["people"])
    contact = request.form["contact"]

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT price FROM events WHERE id=%s",
        (event_id,)
    )

    event = cursor.fetchone()

    total = float(event["price"])

    sql = """
    INSERT INTO bookings
    (
        uid,
        e_id,
        event_date,
        no_of_people,
        total_amount,
        contact_no
    )
    VALUES
    (%s,%s,%s,%s,%s,%s)
    """

    values = (
        session["user_id"],
        event_id,
        event_date,
        people,
        total,
        contact
    )

    cursor.execute(sql, values)

    db.commit()

    cursor.close()
    db.close()

    flash("Booking Successful!")

    return redirect("/my-bookings")

@app.route("/pay-online/<int:event_id>", methods=["POST"])
def pay_online(event_id):

    if "user_id" not in session:
        return redirect("/")

    event_date = request.form.get("event_date", "")
    people = int(request.form.get("people", 1))
    contact = request.form.get("contact", "")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM events WHERE id=%s",
        (event_id,)
    )

    event = cursor.fetchone()

    cursor.close()
    db.close()

    if not event:
        flash("Event not found.")
        return redirect("/user/events")

    total = Decimal(str(event["price"]))
    amount_paise = int(total * 100)

    if amount_paise <= 0:
        flash("Payment amount must be greater than zero.")
        return redirect(f"/book/{event_id}")

    if amount_paise > RAZORPAY_MAX_AMOUNT_PAISE:
        max_amount_rupees = RAZORPAY_MAX_AMOUNT_PAISE / 100
        calculated_total = amount_paise / 100
        flash(f"Payment amount is too high for one Razorpay payment. Calculated total is Rs. {calculated_total:,.2f}. Please keep the total amount up to Rs. {max_amount_rupees:,.2f}.")
        return redirect(f"/book/{event_id}")

    try:
        order = client.order.create({
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"event_{event_id}_{session['user_id']}",
            "notes": {
                "event_id": str(event_id),
                "event_date": event_date,
                "people": str(people),
                "contact": contact,
                "user_id": str(session["user_id"])
            }
        })
    except Exception as error:
        # If Razorpay API is not reachable, create a mock order for testing
        order = {
            "id": f"order_{uuid.uuid4().hex[:12]}",
            "amount": amount_paise,
            "currency": "INR",
            "receipt": f"event_{event_id}_{session['user_id']}",
            "status": "created",
            "notes": {
                "event_id": str(event_id),
                "event_date": event_date,
                "people": str(people),
                "contact": contact,
                "user_id": str(session["user_id"])
            }
        }

    return render_template(
        "users/payment.html",
        event=event,
        order=order,
        amount=amount_paise,
        razorpay_key=RAZORPAY_KEY_ID,
        event_date=event_date,
        people=people,
        contact=contact
    )

@app.route("/payment-success/<int:event_id>")
def payment_success(event_id):

    if "user_id" not in session:
        uid = request.args.get("uid")
        if not uid:
            flash("Payment successful, but login session expired. Please login again to view bookings.")
            return redirect("/")

        session["user_id"] = int(uid)
        session["role"] = "user"

    event_date = request.args.get("event_date", "")
    people = int(request.args.get("people", 1))
    contact = request.args.get("contact", "")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT price FROM events WHERE id=%s", (event_id,))
    event = cursor.fetchone()

    if not event:
        cursor.close()
        db.close()
        flash("Event not found.")
        return redirect("/user/events")

    total = float(event["price"])

    sql = """
    INSERT INTO bookings
    (
        uid,
        e_id,
        event_date,
        no_of_people,
        total_amount,
        contact_no
    )
    VALUES
    (%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(sql, (
        session["user_id"],
        event_id,
        event_date,
        people,
        total,
        contact
    ))

    db.commit()
    cursor.close()
    db.close()

    flash("Payment successful! Booking confirmed.")
    return redirect("/my-bookings")

@app.route("/user/events")
def user_events():

    if "user_id" not in session:
        return redirect("/")

    if session["role"] != "user":
        return redirect("/dashboard")

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT *
        FROM events
        ORDER BY date ASC
    """)

    events = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        "users/event_details.html",
        events=events
    )
    
if __name__ == "__main__":
    app.run(debug=True)

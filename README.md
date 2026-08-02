# 🎉 EventHub - Flask Event Booking System

EventHub is a full-stack Event Booking and Management System developed using **Python Flask**, **MySQL**, **HTML**, **CSS**, and **Bootstrap 5**. The application provides separate dashboards for **Admin** and **Users**, allowing administrators to manage events while users can browse, book, and pay for events online.

## 🚀 Features

### 👤 User Module

* User Registration & Login
* Secure Password Hashing
* Browse Available Events
* View Event Details
* Book Events
* Online Payment Integration (Razorpay)
* View Booking History
* User Dashboard

  * Total Bookings
  * Total Investment
  * Recent Bookings
* Logout

### 🔐 Admin Module

* Admin Login
* Dashboard with Statistics

  * Total Users
  * Total Events
  * Total Bookings
* Add New Events
* Upload Event Images
* Edit Existing Events
* Delete Events
* View All Events
* View Registered Users
* View Booking Records

## 🛠️ Tech Stack

* Python
* Flask
* MySQL
* HTML5
* CSS3
* Bootstrap 5
* Jinja2
* Razorpay Payment Gateway
* Werkzeug (Password Hashing)

## 📂 Project Structure

```text
Event_py/
│
├── app.py
├── requirements.txt
│
├── static/
│   ├── css/
│   │   └── style.css
│   ├── uploads/
│   ├── images/
│   └── js/
│
├── templates/
│   ├── index.html
│   ├── events.html
│   │
│   ├── admin/
│   │   ├── admin_dashboard.html
│   │   ├── add_event.html
│   │   ├── edit_event.html
│   │   ├── view_events.html
│   │   └── userslist.html
│   │
│   └── users/
│       ├── user_dashboard.html
│       ├── event_details.html
│       ├── book_event.html
│       ├── payment.html
│       └── mybookings.html
│
└── README.md
```

## 🗄️ Database Tables

### Users

* id
* username
* password
* role

### Events

* id
* name
* description
* image
* location
* date
* price

### Bookings

* id
* booking_date_time
* uid
* e_id
* event_date
* no_of_people
* total_amount
* contact_no
* payment_status

## 💳 Payment Gateway

The project supports **Razorpay** for secure online payments. Users can either:

* Confirm booking without online payment
* Pay online using Razorpay Checkout

## 🔒 Authentication

* Flask Sessions
* Password Hashing using Werkzeug
* Role-Based Authentication (Admin/User)

## 📸 Main Pages

* Home Page
* Login & Registration
* User Dashboard
* Browse Events
* Book Event
* My Bookings
* Admin Dashboard
* Add Event
* View Events
* Edit/Delete Event
* Users List

## 📌 Future Enhancements

* Email Confirmation
* Booking Cancellation
* Event Search & Filters
* QR Code Ticket Generation
* Booking Invoice (PDF)
* Admin Analytics Dashboard
* Event Categories
* Seat Availability
* Notifications & Reminders
* User Profile Management

## 👩‍💻 Developed By

**Shreyasi Samanta**

B.Tech in Electronics & Communication Engineering

Python | Flask | MySQL | HTML | CSS | Bootstrap

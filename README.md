# The Grand Reservations — Hotel & Guided Tour Booking System

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-5.0%2B-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![Razorpay](https://img.shields.io/badge/Payment-Razorpay%20%7C%20Cashfree-0C2340?logo=razorpay&logoColor=blue)](https://razorpay.com/)
[![PDF Generator](https://img.shields.io/badge/PDF-ReportLab%20%26%20xhtml2pdf-red)](https://www.reportlab.com/)

> **The Grand Reservations** is a full-stack hospitality web application designed for seamless hotel room reservations and curated vacation tour bookings. Features real-time availability computation, dynamic package pricing, online payment gateway processing, automated PDF invoice generation, and an administrative staff management console.

---

## 🌟 Key Features

### 1. Room Reservation Engine
- **Dynamic Package Pricing**: Real-time rate calculation based on stay duration and meal plans:
  - *Room Only*
  - *Room + Breakfast*
  - *Room + Breakfast + Dinner*
- **Availability Verification**: Concurrency-safe date-range overlap checks using Django Q objects to prevent double-booking.
- Multi-image room gallery showcasing room amenities, categories (Single, Double, Deluxe, Suite), and specifications.

### 2. Guided Vacation Tour Booking
- Comprehensive destination packages (e.g., Goa, Ooty, Chikmagalur) with route itineraries, inclusions, and exclusions.
- Flexible pricing options for self-guided trips vs. expert guide accompanied packages.
- Staff allocation and tour scheduling.

### 3. Payment Gateway Integration
- Secure checkout supporting Razorpay / Cashfree sandbox payments (UPI, Cards, Net Banking).
- Webhook/callback validation verifying cryptographic order signatures and updating booking status to Paid.

### 4. Automated PDF Invoices & Email Notifications
- On-the-fly PDF invoice generation using eportlab and xhtml2pdf.
- Dispatch of confirmation emails with booking summaries and PDF invoice attachments directly to the guest.

### 5. Staff & Admin Control Center
- Dedicated portal for hotel staff and administrators.
- Live dashboard displaying occupied rooms, total revenue, pending arrivals, and tour guide assignments.
- CRUD controls for managing hotel properties, rooms, pricing, and tour itineraries.

---

## 🏗️ System Architecture

`
┌─────────────────────────────────────────────────────────────┐
│                      Client Browser                         │
│       (Responsive UI, Datepicker, Dynamic Pricing)          │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTP Form Submission / AJAX
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                    Django Application Core                  │
│  ┌────────────────────────┐  ┌────────────────────────────┐ │
│  │   Frontend & Booking   │  │    Admin & Staff Panel     │ │
│  │  - Date Overlap Checks │  │  - Room & Trip CRUD        │ │
│  │  - Package Pricing Calc│  │  - Staff Allocation        │ │
│  └───────────┬────────────┘  └─────────────┬──────────────┘ │
│              │                             │                │
│              ▼                             ▼                │
│  ┌────────────────────────┐  ┌────────────────────────────┐ │
│  │    Payment Gateway     │  │   Invoice & Mail Service   │ │
│  │   (Razorpay/Cashfree)  │  │  - ReportLab / xhtml2pdf   │ │
│  │   - Verification Hook  │  │  - SMTP Email Confirmation │ │
│  └────────────────────────┘  └────────────────────────────┘ │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Relational Database (SQLite)               │
│      Hotels • Rooms • Bookings • Payments • Trips           │
└─────────────────────────────────────────────────────────────┘
`

---

## 🛠️ Technology Stack

- **Backend**: Python 3.10+, Django 5.0+
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5, FontAwesome
- **Payment Gateway**: Razorpay & Cashfree API integration
- **Document Processing**: ReportLab, xhtml2pdf
- **Database**: SQLite (Development) / PostgreSQL (Production ready)

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10 or higher
- Git

### Installation Steps

1. **Clone the repository:**
   `ash
   git clone https://github.com/Lithishkumar33/The-Grand-Reservations-Hotel-Booking.git
   cd The-Grand-Reservations-Hotel-Booking
   `

2. **Create and activate a virtual environment:**
   `ash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux / macOS
   python3 -m venv venv
   source venv/bin/activate
   `

3. **Install required dependencies:**
   `ash
   pip install -r requirements.txt
   `

4. **Setup Environment Configuration:**
   `ash
   cp .env.example .env
   # Update .env with secret key and test payment credentials
   `

5. **Run Migrations:**
   `ash
   python manage.py makemigrations
   python manage.py migrate
   `

6. **Create Superuser (Staff Administrator):**
   `ash
   python manage.py createsuperuser
   `

7. **Launch Local Server:**
   `ash
   python manage.py runserver
   `
   Access the guest portal at http://127.0.0.1:8000/ and the admin portal at http://127.0.0.1:8000/adminpanel/login/.

---

## 📁 Repository Structure

`
hotelredcastle/
│── accounts/          # User authentication and profile flows
│── adminpanel/        # Custom staff/admin management dashboard
│── booking/           # Room, Hotel, Trip, Booking, and Payment models
│── frontend/          # Booking views, checkout, PDF invoice & email logic
│── hotelredcastle/    # Core project settings and URL configuration
│── templates/         # Modular HTML templates
│── static/            # CSS stylesheets, JS scripts, and static media
│── media/             # Uploaded room and hotel images
│── manage.py          # Django execution utility
└── requirements.txt   # Pinned package requirements
`

---

## 👨‍💻 Author

**Lithish Kumar G**  
- **Email:** [7760lithish@gmail.com](mailto:7760lithish@gmail.com)  
- **LinkedIn:** [linkedin.com/in/lithish-kumar-g-aa0b67279](https://www.linkedin.com/in/lithish-kumar-g-aa0b67279)  
- **GitHub:** [github.com/Lithishkumar33](https://github.com/Lithishkumar33)  
- **Location:** Bengaluru, Karnataka, India  

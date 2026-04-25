# Online Construction Machine Rental System

A Django web application for renting construction machinery online.

## Included Modules

- Authentication and user management with customer and equipment owner roles
- Machine management with categories, specifications, images, pricing, and availability
- Search and filtering by machine name, category, price, and availability
- Booking and reservation with rental duration and booking history
- Payment status, invoice generation, refund status, and transaction tracking
- Delivery requests, pickup/drop locations, rental status, and complaint handling
- Customer ratings and reviews
- Dashboard and report pages for bookings, revenue, and machine usage

## Demo Login

- Owner: `owner` / `owner123`
- Customer: `customer` / `customer123`

## Run

```powershell
python manage.py runserver 127.0.0.1:8000
```

Open `http://127.0.0.1:8000/`.

## Reset Demo Data

```powershell
python manage.py migrate
python manage.py seed_demo
```

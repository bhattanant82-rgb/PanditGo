# PanditGo - Professional Puja Booking Platform

A complete full-stack web application for booking pandits and performing pujas, built with Flask backend and Bootstrap frontend.

## Features

- **Role-based Authentication**: Admin, Pandit, Customer
- **Secure Payments**: Razorpay integration
- **Kundli Generation**: Vedic astrology calculations
- **Admin Dashboard**: Manage users, bookings, approvals
- **Responsive Design**: Mobile-friendly Bootstrap UI

## Project Structure

```
panditgo/
├── backend.py          # Flask API server
├── schema.sql          # Database schema
├── index.html          # Landing page
├── login.html          # User login
├── signup.html         # User registration
├── admin-login.html    # Admin login
├── admin dashboard/
│   └── admin.html      # Admin dashboard
├── pandit-login.html   # Pandit login
├── pandit-dashboard.html # Pandit dashboard
├── my-dashboard.html   # Customer dashboard
├── book-pandit.html    # Booking flow
├── current-booking.html # Active booking
├── pujas.html          # Puja listings
├── contact.html        # Contact page
├── style.css           # Global styles
├── script.js           # Shared JS
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.8+
- SQLite (built-in)
- XAMPP (for serving HTML files)

### Backend Setup
1. Install dependencies:
   ```bash
   pip install flask flask-cors PyJWT astropy requests
   ```

2. Run the backend:
   ```bash
   python backend.py
   ```
   Server starts on http://localhost:5000

### Frontend Setup
1. Start XAMPP Apache
2. Place project in `C:\xampp\htdocs\PanditGo\`
3. Access at http://localhost/PanditGo/

### Database
- SQLite database `bookmypandit.db` is auto-created
- Schema matches `schema.sql`
- Default admin: admin@bookmypandit.com / admin123

## API Endpoints

### Authentication
- `POST /api/signup` - User registration
- `POST /api/login` - User login
- `GET /api/check-auth` - Verify token

### Admin
- `GET /api/admin/dashboard` - Dashboard data
- `POST /api/admin/approve-pandit/<id>` - Approve pandit

### Bookings
- `GET /api/pujas` - List pujas
- `POST /api/bookings` - Create booking
- `GET /api/bookings` - User bookings

### Other
- `POST /generate-kundli` - Kundli generation
- `POST /refund` - Process refund

## Security Features

- JWT token authentication
- Password hashing with SHA256
- Role-based access control
- CORS enabled for frontend

## Deployment

For production:
1. Use MySQL instead of SQLite
2. Set environment variables for secrets
3. Use HTTPS
4. Configure proper CORS origins

## File Flow

1. **Entry**: index.html → signup.html/login.html
2. **Auth**: Login redirects to role-specific dashboard
3. **Booking**: my-dashboard.html → book-pandit.html → current-booking.html
4. **Admin**: admin-login.html → admin-dashboard (dynamic data)
5. **Pandit**: pandit-login.html → pandit-dashboard.html

## Missing Features for Production

- Email verification for signup
- File upload for pandit documents
- Real-time notifications
- Payment webhooks
- Advanced search/filtering
- Multi-language support
- Audit logging
- Rate limiting
- Backup system

## Technologies Used

- **Backend**: Flask, SQLite, JWT
- **Frontend**: HTML5, Bootstrap 5, JavaScript
- **Payments**: Razorpay
- **Astrology**: Astropy library

## Contact

For support: bhattanant82@gmail.com | +91 6359290705
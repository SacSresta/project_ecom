# BasanaBoutique - E-commerce Platform

A modern e-commerce platform built with Django, featuring a robust shopping cart system, payment integration, and product management.

## Features

- 🛍️ Product catalog with categories
- 🛒 Shopping cart functionality
- 💳 Secure payment integration
- 🏷️ Promo code system
- 👤 User authentication
- 📱 Responsive design
- 🖼️ Media file handling

## Tech Stack

- Python 3.11+
- Django
- SQLite3
- HTML/CSS/JavaScript
- Static file handling

## Project Structure

```
BasanaBoutique/
├── cart/               # Shopping cart functionality
├── ecom/               # Main project configuration
├── payment/            # Payment processing
├── store/              # Product and store management
├── media/              # User uploaded content
├── static/             # Static files (CSS, JS, assets)
└── staticfiles/        # Collected static files
```

## Getting Started

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone https://github.com/SacSresta/BasanaBoutique.git
cd BasanaBoutique
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Apply database migrations:
```bash
python manage.py migrate
```

5. Create a superuser (admin):
```bash
python manage.py createsuperuser
```

6. Run the development server:
```bash
python manage.py runserver
```

The application will be available at `http://127.0.0.1:8000/`

## Configuration

- Configure your environment variables in `ecom/settings.py`
- Set up your database configuration
- Configure your static and media file settings

## Usage

1. Access the admin interface at `/admin` to manage:
   - Products
   - Categories
   - Orders
   - Promo codes
   - User accounts

2. Browse the store as a customer to:
   - View products
   - Add items to cart
   - Apply promo codes
   - Complete checkout process

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contact

SacSresta - [GitHub Profile](https://github.com/SacSresta)

Project Link: [https://github.com/SacSresta/BasanaBoutique](https://github.com/SacSresta/BasanaBoutique)

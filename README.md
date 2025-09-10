# BasanaBoutique - E-commerce Platform

A modern e-commerce platform built with Django, featuring a robust shopping cart system, payment integration, and product management.

## 🌟 Features

- **Product Management**
  - 🛍️ Product catalog with categories
  - � Advanced search functionality
  - 📱 Product variants support
  - 📸 Multiple product images

- **Shopping Experience**
  - �🛒 Dynamic shopping cart
  - 🏷️ Promo code system
  - 💳 Multiple payment options (Stripe & PayPal)
  - 📦 Order tracking system

- **User Management**
  - 👤 User registration and authentication
  - 📝 Profile management
  - 🏠 Address management
  - 📊 Order history

- **Admin Features**
  - 📊 Order management dashboard
  - 🚚 Shipment tracking
  - 💰 Payment status monitoring
  - 📦 Product inventory management

## 🚀 Technology Stack

- **Backend**: Django 5.2.1
- **Database**: POSTGRESQL
- **Payment Integration**: 
  - Stripe
  - PayPal
- **Additional Features**:
  - Azure Storage for media files
  - Phone number verification
  - Gunicorn for production deployment

## 📋 Prerequisites

- Python 3.12 or higher
- pip package manager

## 🛠️ Installation

1. Clone the repository
```bash
git clone https://github.com/SacSresta/project_ecom.git
cd project_ecom
```

2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up the database
```bash
python manage.py migrate
```

5. Create a superuser
```bash
python manage.py createsuperuser
```

6. Run the development server
```bash
python manage.py runserver
```

## �️ Project Structure

```
project_ecom/
├── cart/               # Shopping cart functionality
├── ecom/               # Main project settings
├── payment/            # Payment processing
├── store/              # Product management
├── manage.py
└── requirements.txt
```

## 🔒 Environment Variables

Create a `.env` file in the root directory and add the following:

```env
SECRET_KEY=your_secret_key
DEBUG=True
STRIPE_PUBLIC_KEY=your_stripe_public_key
STRIPE_SECRET_KEY=your_stripe_secret_key
PAYPAL_CLIENT_ID=your_paypal_client_id
AZURE_STORAGE_CONNECTION_STRING=your_azure_storage_connection
```

## 🌐 API Endpoints

### Store
- `/` - Home page
- `/product/<id>/` - Product detail
- `/category/<name>/` - Category products
- `/search/` - Product search

### Cart
- `/cart/` - Cart summary
- `/cart/add/` - Add to cart
- `/cart/update/` - Update cart
- `/cart/delete/` - Remove from cart

### Payment
- `/payment/checkout/` - Checkout process
- `/payment/stripe_checkout/` - Stripe payment
- `/payment/payment_success/` - Success page
- `/payment/orders/<id>` - Order details

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Support

For support, email support@basanaboutique.com or create an issue in the repository.
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

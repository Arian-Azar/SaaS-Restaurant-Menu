# 🍽️ Restaurant SaaS Platform

> **A modern multi-tenant SaaS platform for creating, managing, and scaling digital restaurant websites and menus.**

![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square\&logo=python)
![Django](https://img.shields.io/badge/Django-6.x-green?style=flat-square\&logo=django)
![DRF](https://img.shields.io/badge/Django%20REST%20Framework-API-red?style=flat-square)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-316192?style=flat-square\&logo=postgresql)
![Redis](https://img.shields.io/badge/Redis-Cache%20%26%20Queue-red?style=flat-square\&logo=redis)
![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)

---

## 📌 Overview

**Restaurant SaaS Platform** is a scalable multi-tenant platform designed for restaurants, cafés, fast-food businesses, and food brands.

The platform allows each restaurant to create and manage its own digital presence without requiring a separate software installation or dedicated application.

Each restaurant receives:

* 🏪 Dedicated restaurant profile
* 📋 Digital menu
* 🍕 Product and category management
* 📱 Responsive restaurant website
* 🔳 Dedicated QR Code
* 🛒 Online ordering
* 💳 Online payment
* 📊 Business analytics
* 👤 Dedicated management account
* 🔐 Isolated access to its own data
* 💎 Subscription-based SaaS plan

The core philosophy of the project is:

> **Build once. Serve thousands of restaurants.**

---

# 🎯 Project Vision

Traditional restaurant websites usually require:

```text
Restaurant
     ↓
Hire Developer
     ↓
Build Website
     ↓
Buy Hosting
     ↓
Configure Server
     ↓
Maintain Website
```

This platform transforms the process into:

```text
Restaurant
     ↓
Register
     ↓
Choose a Plan
     ↓
Configure Restaurant
     ↓
Add Menu
     ↓
Generate QR Code
     ↓
Go Live 🚀
```

The restaurant does not need to understand web development, hosting, deployment, or database management.

Everything is managed through a centralized SaaS platform.

---

# 🏗️ Architecture

The platform follows a **Multi-Tenant Architecture**.

A single application can serve multiple restaurants while keeping each tenant's data isolated.

```text
                         RESTAURANT SaaS
                              │
               ┌──────────────┴──────────────┐
               │                             │
          Public Platform               Admin System
               │                             │
               │                    ┌────────┴────────┐
               │                    │                 │
               │              Super Admin      Restaurant Admin
               │                    │                 │
               │                    │                 │
        ┌──────┼──────┐             │          ┌──────┼──────┐
        │      │      │             │          │      │      │
        ▼      ▼      ▼             ▼          ▼      ▼      ▼
     Cafe A  Cafe B  Cafe C      All Data    Menu   Orders Settings
```

### Tenant Isolation

Every restaurant owns its own data:

```text
Restaurant A
├── Categories
├── Products
├── Orders
├── Customers
├── Images
└── Settings

Restaurant B
├── Categories
├── Products
├── Orders
├── Customers
├── Images
└── Settings
```

Restaurant A can never access Restaurant B's private data.

---

# ✨ Core Features

## 🏪 Restaurant Management

Each restaurant has a dedicated workspace containing:

* Restaurant name
* Logo
* Cover image
* Description
* Contact information
* Address
* Social media
* Business hours
* Location
* Restaurant status

---

## 📋 Digital Menu

Restaurant owners can manage their menu without developer intervention.

### Categories

Examples:

```text
🍕 Pizza
🍔 Burgers
🍝 Pasta
🥗 Salad
🥤 Drinks
🍰 Desserts
```

### Products

Each product can contain:

```text
Name
Description
Price
Discount Price
Image
Category
Availability
Display Order
```

---

# 📱 Responsive Restaurant Website

Every restaurant receives a mobile-friendly public page.

Example:

```text
platform.com/arian-cafe
```

The public page can include:

```text
┌───────────────────────────────┐
│           Restaurant          │
│          Logo / Cover         │
├───────────────────────────────┤
│       🍕 Categories           │
├───────────────────────────────┤
│                               │
│       🍕 Pizza Special        │
│       450,000 Toman           │
│                               │
├───────────────────────────────┤
│       🍔 Special Burger       │
│       320,000 Toman           │
│                               │
└───────────────────────────────┘
```

---

# 🔳 QR Menu

Every restaurant receives a unique QR Code.

```text
             ┌───────────┐
             │  QR CODE  │
             └─────┬─────┘
                   │
                   ▼
       platform.com/arian-cafe
                   │
                   ▼
             Digital Menu
```

The QR Code can be placed on:

* Restaurant tables
* Menus
* Counter displays
* Packaging
* Business cards
* Promotional materials

---

# 🛒 Online Ordering

Customers can browse the menu and create an order.

```text
Menu
  ↓
Product
  ↓
Add to Cart
  ↓
Checkout
  ↓
Payment
  ↓
Order Confirmation
```

Order lifecycle:

```text
PENDING
   ↓
CONFIRMED
   ↓
PREPARING
   ↓
READY
   ↓
COMPLETED
```

---

# 💳 Payment System

The platform is designed to support online payment gateways.

Payment lifecycle:

```text
Order Created
      ↓
Payment Pending
      ↓
Payment Gateway
      ↓
Payment Callback
      ↓
Verification
      ↓
Payment Successful
      ↓
Order Confirmed
```

Supported payment gateways can be integrated independently.

---

# 👤 User & Access Management

The system provides role-based access control.

### Super Admin

Platform owner:

```text
✓ All Restaurants
✓ All Users
✓ All Products
✓ All Orders
✓ Payments
✓ Subscriptions
✓ Analytics
✓ System Settings
```

### Restaurant Owner

Restaurant administrator:

```text
✓ Own Restaurant
✓ Own Products
✓ Own Categories
✓ Own Orders
✓ Own Customers
✓ Own Settings

✗ Other Restaurants
✗ Other Customers
✗ Platform Settings
```

---

# 💎 SaaS Subscription System

Restaurants can subscribe to different plans.

Example:

| Plan         | Digital Menu  | Website   | Ordering   | Payment  | Analytics |
| ------------ | ------------  | -------   | --------   | -------  | --------- |
| Starter      | ✅            | ✅       | ❌        | ❌       | Basic     |
| Business     | ✅            | ✅       | ✅        | ✅       | Advanced  |
| Professional | ✅            | ✅       | ✅        | ✅       | Full      |

Each subscription contains:

```text
Restaurant
Plan
Start Date
End Date
Status
```

Possible states:

```text
ACTIVE
TRIAL
EXPIRED
SUSPENDED
CANCELLED
```

---

# 🌐 Custom Domains

The platform is designed to support multiple URL strategies.

### Path-based

```text
platform.com/arian-cafe
```

### Subdomain

```text
arian-cafe.platform.com
```

### Custom Domain

```text
www.arian-cafe.com
```

This allows the platform to evolve from a simple digital menu system into a complete website-as-a-service platform.

---

# 📊 Analytics

Future analytics capabilities include:

* Menu views
* QR scans
* Product views
* Popular products
* Order statistics
* Revenue
* Customer activity
* Conversion rate

Example:

```text
Today's Overview

Menu Views       1,245
QR Scans           487
Orders             126
Revenue       42,500,000
```

---

# 🛠️ Technology Stack

## Backend

* Python
* Django
* Django REST Framework

## Database

* PostgreSQL

## Frontend

Initial version:

* HTML5
* CSS3
* JavaScript

Future:

* React
* Next.js

## Infrastructure

* Nginx
* Gunicorn / Uvicorn
* Redis
* Celery

## Development

* Git
* GitHub
* Virtual Environment
* Environment Variables

---

# 📦 Project Structure

```text
restaurant_saas/
│
├── config/
│   ├── settings/
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
│
├── accounts/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── restaurants/
│   ├── models.py
│   ├── admin.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── menu/
│   ├── models.py
│   ├── admin.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── orders/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
│
├── payments/
│   ├── models.py
│   ├── services.py
│   ├── views.py
│   └── urls.py
│
├── subscriptions/
│   ├── models.py
│   ├── services.py
│   └── views.py
│
├── customers/
│
├── notifications/
│
├── analytics/
│
├── core/
│
├── templates/
│
├── static/
│
├── media/
│
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

---

# 🔐 Security Architecture

Security is a fundamental requirement of the platform.

The system must enforce strict tenant isolation.

### Core security principles

* Authentication
* Authorization
* Role-Based Access Control
* Tenant Isolation
* CSRF Protection
* Secure Cookies
* Password Hashing
* Rate Limiting
* Input Validation
* File Upload Validation
* HTTPS
* Secure Headers
* Database Backups
* Audit Logging

A critical rule:

> **A restaurant must never be able to access, modify, or infer another restaurant's private data.**

---

# 🚀 Installation

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/restaurant-saas.git

cd restaurant-saas
```

## 2. Create Virtual Environment

### Windows

```powershell
python -m venv .venv

.venv\Scripts\activate
```

### Linux / macOS

```bash
python3 -m venv .venv

source .venv/bin/activate
```

## 3. Install Dependencies

```bash
pip install -r requirements.txt
```

## 4. Configure Environment Variables

Create:

```text
.env
```

Example:

```env
DEBUG=True

SECRET_KEY=your-secret-key

DATABASE_NAME=restaurant_saas
DATABASE_USER=postgres
DATABASE_PASSWORD=your-password
DATABASE_HOST=localhost
DATABASE_PORT=5432

REDIS_URL=redis://127.0.0.1:6379/1
```

> Never commit `.env` to Git.

## 5. Run Migrations

```bash
python manage.py migrate
```

## 6. Create Superuser

```bash
python manage.py createsuperuser
```

## 7. Run Development Server

```bash
python manage.py runserver
```

The application will be available at:

```text
http://127.0.0.1:8000/
```

Admin panel:

```text
http://127.0.0.1:8000/admin/
```

---

# 🧪 Testing

Run the complete test suite:

```bash
python manage.py test
```

Specific application:

```bash
python manage.py test accounts
```

---

# 🔄 Development Roadmap

## Phase 1 — Foundation

* [x] Django project
* [ ] Custom User
* [ ] Restaurant model
* [ ] Authentication
* [ ] Multi-Tenant foundation
* [ ] PostgreSQL

## Phase 2 — Menu

* [ ] Categories
* [ ] Products
* [ ] Product images
* [ ] Pricing
* [ ] Discounts
* [ ] Availability
* [ ] Sorting

## Phase 3 — Public Platform

* [ ] Restaurant public page
* [ ] Responsive menu
* [ ] Restaurant profile
* [ ] QR Code
* [ ] SEO

## Phase 4 — Ordering

* [ ] Cart
* [ ] Checkout
* [ ] Orders
* [ ] Order status
* [ ] Customer management

## Phase 5 — Payments

* [ ] Payment model
* [ ] Gateway integration
* [ ] Callback handling
* [ ] Payment verification
* [ ] Refund support

## Phase 6 — SaaS

* [ ] Subscription plans
* [ ] Billing
* [ ] Trial system
* [ ] Subscription expiration
* [ ] Feature limits
* [ ] Restaurant dashboard

## Phase 7 — Advanced

* [ ] Custom domains
* [ ] Subdomains
* [ ] Analytics
* [ ] Loyalty system
* [ ] Discount engine
* [ ] SMS notifications
* [ ] Email notifications
* [ ] Multiple branches
* [ ] Advanced reports

---

# 💰 Business Model

The platform follows a subscription-based SaaS model.

Example:

```text
Initial Setup
       +
Annual Subscription
       +
Optional Premium Features
```

Example pricing strategy:

| Plan         |  Setup | Annual |
| ------------ | -----: | -----: |
| Starter      |   5–8M |   3–5M |
| Business     | 10–15M |   6–8M |
| Professional | 15–25M |  9–15M |

Prices are configurable and can be adapted according to market conditions and included features.

---

# 📈 Scalability

The system is designed to scale from:

```text
1 Restaurant
      ↓
10 Restaurants
      ↓
100 Restaurants
      ↓
1,000 Restaurants
      ↓
10,000+ Restaurants
```

Scaling strategy:

```text
                 Load Balancer
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Django 1   Django 2    Django 3
          │           │           │
          └───────────┼───────────┘
                      │
                  PostgreSQL
                      │
                    Redis
                      │
                 Object Storage
```

---

# 🗺️ Product Evolution

The long-term goal is not simply to provide a digital menu.

The platform can evolve into a complete:

> **Restaurant Operating & Digital Commerce Platform**

Future ecosystem:

```text
Digital Menu
     +
QR Ordering
     +
Online Ordering
     +
Online Payment
     +
Customer Management
     +
Loyalty Program
     +
Analytics
     +
Marketing
     +
Restaurant Management
```

---

# 🎯 Target Customers

The platform is designed for:

* 🍽️ Restaurants
* ☕ Cafés
* 🍔 Fast-food businesses
* 🥐 Bakeries
* 🍕 Pizzerias
* 🧁 Dessert shops
* 🥤 Juice & beverage shops
* 🏪 Food chains
* 🏢 Multi-branch restaurants

---

# 🤝 Contributing

Contributions are welcome.

```bash
git checkout -b feature/new-feature

git add .

git commit -m "Add new feature"

git push origin feature/new-feature
```

Then open a Pull Request.

---

# 📄 License

This project is currently under development.

License and commercial usage terms will be defined before the production release.

---

# 👨‍💻 Project Status

🚧 **Active Development**

The project is currently being developed as a production-oriented SaaS platform.

The initial development priority is:

```text
Multi-Tenancy
      ↓
Authentication
      ↓
Restaurant Management
      ↓
Digital Menu
      ↓
QR Code
      ↓
Ordering
      ↓
Payment
      ↓
Subscription
      ↓
Analytics
```

---

## ⭐ Vision

> **One platform. Thousands of restaurants. One scalable architecture.**

The ultimate goal is to provide restaurants with a simple, powerful, and affordable digital infrastructure while allowing the platform to scale as a SaaS business.

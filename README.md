# Enterprise D2C Online Cosmetic Store Platform (AURA Cosmetics)

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Jira Reference:** `ARCH-1141` — UI Pages + Requirements: Enterprise D2C Online Cosmetic Store Platform

A modern, high-performance MACH (Microservices, API-first, Cloud-native, Headless) composable commerce platform designed for a direct-to-consumer (D2C) global beauty and cosmetics brand. The platform features hyper-personalized shade matching, 50+ shade variants, faceted catalog filtering, automated subscription replenishment with customer self-service (skip & swap), tokenized checkout, and a tiered loyalty program.

---

## 📑 Table of Contents

- [Overview & Architecture](#-overview--architecture)
- [Key Features](#-key-features)
- [Project Structure](#-project-structure)
- [Data Model & Schema](#-data-model--schema)
- [API Endpoints](#-api-endpoints)
- [Getting Started](#-getting-started)
- [Running the Application](#-running-the-application)
- [Running Tests & Quality Checks](#-running-tests--quality-checks)
- [Frontend User Interface](#-frontend-user-interface)
- [Acceptance Criteria Verification](#-acceptance-criteria-verification)

---

## 🏛 Overview & Architecture

The platform is designed following MACH principles:
- **API-First Architecture:** Built on FastAPI with strict Pydantic schemas and auto-generated OpenAPI / Swagger documentation.
- **Relational Data Layer:** SQLite-backed relational schema with foreign keys and ACID transactional integrity for orders, inventory, and subscriptions.
- **Headless Frontend:** Accessible, responsive UI utilizing Tailwind CSS and a modular client-side API SDK (`public/js/api.js`).
- **WCAG 2.1 AA Compliance:** High-contrast accessible color tokens, semantic markup, keyboard navigability, and ARIA attributes.

```
┌────────────────────────────────────────────────────────┐
│               Frontend Presentation Layer              │
│   (HTML5 SPA / Tailwind CSS / Vanilla JS SDK api.js)   │
└───────────────────────────┬────────────────────────────┘
                            │ HTTP / JSON
┌───────────────────────────▼────────────────────────────┐
│                  FastAPI Backend Server                │
│ ┌──────────────┬──────────────┬──────────────────────┐ │
│ │ Products API │ Shade Finder │ Cart & Checkout      │ │
│ ├──────────────┼──────────────┼──────────────────────┤ │
│ │ Subscriptions│ Account/Loyal│ Static Assets Router │ │
│ └──────────────┴──────────────┴──────────────────────┘ │
└───────────────────────────┬────────────────────────────┘
                            │ SQL / Session
┌───────────────────────────▼────────────────────────────┐
│                    SQLite Database                     │
│  users · products · product_shades · cart · orders     │
│             subscriptions · loyalty_accounts           │
└────────────────────────────────────────────────────────┘
```

---

## ✨ Key Features

### 1. 🎨 Hyper-Personalized Shade Matching Engine (`REQ-F-001`)
- Multi-factor algorithm matching user skin depth (*Fair, Light, Medium, Tan, Deep, Rich*) and undertone (*Warm, Cool, Neutral, Olive*).
- Returns recommended product shades with confidence scores and alternative recommendations.

### 2. 💄 50+ Shade Catalog & Faceted Search (`REQ-F-002`, `REQ-F-003`)
- Rich shade attributes including hex color code, undertone, finish (*Matte, Dewy, Satin, Natural*), and depth.
- Multi-criteria faceted filtering and full-text keyword search.

### 3. 🔄 Automated Replenishment & Subscriptions (`REQ-F-004`, `REQ-F-007`)
- Recurring delivery scheduling with 15% discount incentives.
- Self-service portal to **skip** upcoming delivery cycles or **swap** shade variants with zero friction.

### 4. 💳 Tokenized One-Click Checkout (`REQ-F-008`)
- Frictionless mock checkout with saved addresses and tokenized payment processing.
- Atomic order creation, cart clearance, and line-item generation.

### 5. 🏆 Tiered Loyalty Rewards Program (`REQ-F-019`)
- Point accrual system (10 points per dollar spent).
- Tier advancement (*Bronze, Silver, Gold*) with real-time balance tracking on the account dashboard.

---

## 📂 Project Structure

```
.
├── CHANGELOG.md                      # Release notes & version history
├── README.md                         # Project documentation
├── requirements.txt                  # Python dependencies
├── scaffolded_files.json             # Manifest of project artifacts
├── db/
│   ├── schema.sql                    # DDL database schema definitions
│   └── seed.sql                      # DML seed data (products, shades, users)
├── app/
│   ├── __init__.py
│   ├── main.py                       # FastAPI application entrypoint & static mount
│   ├── api/
│   │   ├── __init__.py
│   │   ├── account.py                # Dashboard & loyalty API routes
│   │   ├── cart.py                   # Cart management routes
│   │   ├── checkout.py               # Order placement & checkout routes
│   │   ├── products.py               # Catalog browse & filter routes
│   │   ├── shade_finder.py           # Shade matching quiz engine routes
│   │   └── subscriptions.py          # Subscription skip & swap routes
│   ├── db/
│   │   ├── __init__.py
│   │   ├── init_db.py                # Database initialization script
│   │   └── session.py                # SQLite connection provider & session manager
│   └── models/
│       ├── __init__.py
│       └── cosmetics.py              # Pydantic data schemas & request/response models
├── public/
│   ├── index.html                    # Single Page Application container
│   ├── js/
│   │   └── api.js                    # Client-side API wrapper for backend endpoints
│   └── pages/                        # Standalone high-fidelity HTML views
│       ├── account_dashboard.html
│       ├── account_orders.html
│       ├── account_subscriptions.html
│       ├── cart.html
│       ├── checkout.html
│       ├── home.html
│       ├── loyalty.html
│       ├── order_confirmation.html
│       ├── product_detail.html
│       ├── product_listing.html
│       └── shade_finder_quiz.html
└── tests/
    ├── test_api_cart_checkout.py     # Cart, checkout & account integration tests
    ├── test_api_products.py          # Product catalog & faceted filter tests
    ├── test_api_shade_finder.py      # Shade matching algorithm tests
    ├── test_db.py                    # Database schema & seed verification
    └── test_e2e.py                   # Full-journey customer smoke tests
```

---

## 🗄 Data Model & Schema

The relational database (`cosmetics.db`) consists of 7 interconnected tables:

| Table | Purpose |
|:---|:---|
| `users` | User accounts with authentication credentials and registration timestamp. |
| `loyalty_accounts` | Tier level (*Bronze*, *Silver*, *Gold*), current points, and lifetime points. |
| `products` | Core catalog: foundation, concealer, tint, and lipstick with pricing and ratings. |
| `product_shades` | Individual shade variants linked to products with hex codes, undertones, and finishes. |
| `cart_items` | Session and user carts supporting one-time and subscription quantities. |
| `orders` | Confirmed customer orders with total amounts, shipping addresses, and status. |
| `order_items` | Line items for completed orders referencing products and shades. |
| `subscriptions` | Active recurring replenishment subscriptions with delivery schedules and status. |

---

## 🔌 API Endpoints

### Products & Catalog
- `GET /api/v1/products` — List all products with optional filters (`category`, `undertone`, `finish`, `depth`, `search`).
- `GET /api/v1/products/{product_id}` — Get single product details with all associated shade variants.

### Shade Finder
- `POST /api/v1/shade-finder/match` — Match user skin quiz inputs to optimal shade recommendations.

### Cart & Checkout
- `GET /api/v1/cart?user_id={id}` — Fetch active cart items, subtotal, and count.
- `POST /api/v1/cart?user_id={id}` — Add a product/shade to the cart.
- `DELETE /api/v1/cart/{item_id}?user_id={id}` — Remove item from cart.
- `POST /api/v1/checkout` — Process tokenized checkout, create order, and award loyalty points.

### Subscriptions
- `GET /api/v1/subscriptions?user_id={id}` — List active customer replenishment subscriptions.
- `POST /api/v1/subscriptions/{id}/skip?user_id={id}` — Skip the next scheduled subscription shipment.
- `POST /api/v1/subscriptions/{id}/swap?user_id={id}` — Swap the subscription shade variant.

### Account & Loyalty
- `GET /api/v1/account/dashboard?user_id={id}` — Retrieve user profile, loyalty status, and order history.

### System
- `GET /health` — Service health check and status timestamp.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- `pip` or `uv` package manager

### 1. Clone & Setup Environment
```bash
# Clone the repository
git clone https://github.com/wisdom-is-chasing-u-and-u-are-faster/DevelopmentAgent_test.git
cd DevelopmentAgent_test

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Initialize Database
Initialize the SQLite database with schema tables and seed data:
```bash
python3 -m app.db.init_db
```

---

## 💻 Running the Application

Start the FastAPI application with Uvicorn:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Storefront UI:** [http://localhost:8000/](http://localhost:8000/)
- **Interactive Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Alternative ReDoc Docs:** [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Health Check:** [http://localhost:8000/health](http://localhost:8000/health)

---

## 🧪 Running Tests & Quality Checks

### Run Automated Test Suite
```bash
PYTHONPATH=. pytest -v
```

### Run Linter
```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
```

### Run Type Checker
```bash
mypy app
```

---

## 🎨 Frontend User Interface

The frontend is served directly through FastAPI static file mounting at `/`:
- **Home & Hero Section:** Brand presentation and featured collection overview.
- **Product Listing:** Interactive faceted filter sidebar with real-time grid view.
- **Product Detail:** Dynamic shade swatch picker and subscription toggle.
- **Shade Finder Quiz:** 4-step guided questionnaire with instant recommendation.
- **Cart & Checkout:** Order summary calculation and tokenized 1-click checkout.
- **Customer Dashboard:** Order history and subscription management (Skip/Swap).
- **Dark/Light Mode:** Instant theme switching with persistent local storage preference.

---

## 🎯 Acceptance Criteria Verification

| # | Jira Acceptance Criteria | Implementation / Verification Test | Status |
|---|---|---|:---:|
| 1 | Complete shade finder quiz & receive recommendation | `POST /api/v1/shade-finder/match` · `tests/test_api_shade_finder.py` | ✅ Passed |
| 2 | Browse products, filter by shade attributes, view PDP | `GET /api/v1/products` · `tests/test_api_products.py` | ✅ Passed |
| 3 | Add to cart, checkout, complete mock purchase | `POST /api/v1/cart`, `POST /api/v1/checkout` · `tests/test_api_cart_checkout.py` | ✅ Passed |
| 4 | Log in, view account dashboard and order history | `GET /api/v1/account/dashboard` · `tests/test_api_cart_checkout.py` | ✅ Passed |
| 5 | View active subscriptions and perform 'skip' or 'swap' | `POST /api/v1/subscriptions/{id}/skip|swap` · `tests/test_api_cart_checkout.py` | ✅ Passed |
| 6 | WCAG 2.1 AA compliance & full customer journey E2E | `tests/test_e2e.py` · Full stack smoke tests | ✅ Passed |

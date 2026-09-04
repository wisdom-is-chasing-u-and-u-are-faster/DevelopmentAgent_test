# Sustainable Clothing Marketplace - Carbon Footprint Engine & Core Platform

An enterprise-grade green digital commerce platform paired with a mathematically rigorous, auditable carbon accounting engine and immutable transaction ledger.

## Features & Microservices
- **Automated Cradle-to-Gate Carbon Baseline Engine**: Calculates product emission baselines based on material composition percentages mapped to verified LCA databases (Ecoinvent, Higg Index).
- **Dynamic Shipping Carbon Calculator**: Computes checkout logistics carbon footprints based on origin/destination coordinates and package weight.
- **Offset-at-Checkout Integration**: Direct integration with Patch API with automated fallback and retry dead-letter queuing.
- **Immutable Transactional Carbon Ledger**: Cryptographically chained SHA-256 block ledger tracking all product baselines and customer offset transactions.
- **Interactive Frontend UI**: 16 standalone HTML screens covering Shopper experience, Vendor onboarding portal, and Admin compliance audit queue.

## Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Test Suite
```bash
pytest tests/ -v
```

### 3. Start Development Server
```bash
uvicorn app.main:app --reload --port 8000
```
API Documentation: `http://localhost:8000/docs`

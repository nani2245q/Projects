# E-Commerce Platform with User Behavior Analytics

A full-stack ecommerce application with integrated user behavior tracking, conversion funnel analysis, marketing attribution, and a real-time analytics dashboard. Built to demonstrate end-to-end commerce data modeling, KPI definition, and self-service analytics.

## Key Analytics Features

- **Conversion Funnel Tracking** — Page View → Product View → Add to Cart → Checkout → Purchase with drop-off rates at each stage
- **Marketing Attribution** — Revenue, sessions, and conversion rates broken down by acquisition channel (organic, paid search, social, email, referral, direct)
- **Revenue KPIs** — Daily/weekly/monthly revenue trends, AOV, order count, and growth metrics
- **Category Performance** — View-to-cart rate, cart-to-purchase rate, and revenue by product category
- **Customer Cohort Analysis** — Retention and revenue by acquisition month
- **Real-time Event Tracking** — Client-side SDK captures page views, product views, cart activity, and checkout events

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Node.js, Express.js |
| Database | MongoDB, Mongoose ODM |
| Frontend | Vanilla JavaScript, HTML5, CSS3 |
| Visualization | Chart.js |
| Authentication | JWT, bcrypt |

## Data Model

```
Users ──────── acquisition channel, first seen, last active
Products ───── category, price, view/cart/purchase counters, conversion rates
Orders ──────── items, totals, attribution channel, session ID
BehaviorEvents ─ event type, session, product, metadata, attribution, device
Carts ───────── user items with timestamps
```

## Setup & Run

### Prerequisites
- Node.js 18+
- MongoDB running locally (or a MongoDB Atlas URI)

### Installation

```bash
cd backend
npm install

# Configure environment
cp .env.example .env
# Edit .env with your MongoDB URI

# Seed the database with demo data (50 users, 20 products, ~1000+ events, 100+ orders)
npm run seed

# Start the server
npm start
```

### Access

- **Store**: http://localhost:5000
- **Analytics Dashboard**: http://localhost:5000/pages/analytics.html
- **Admin Login**: `admin@ecommerce.com` / `admin123`

## API Endpoints

### Commerce
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register with acquisition channel |
| POST | `/api/auth/login` | Login |
| GET | `/api/products` | List products (filter, sort, paginate) |
| GET | `/api/products/:id` | Product detail (auto-tracks view) |
| POST | `/api/cart/add` | Add to cart (tracks event) |
| POST | `/api/orders` | Checkout (tracks funnel events) |

### Analytics (Admin)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/dashboard` | KPI summary + top products |
| GET | `/api/analytics/funnel` | Conversion funnel with drop-off rates |
| GET | `/api/analytics/revenue` | Revenue time series (day/week/month) |
| GET | `/api/analytics/attribution` | Marketing channel attribution |
| GET | `/api/analytics/cohorts` | Customer cohort retention |
| GET | `/api/analytics/categories` | Category performance metrics |

### Event Tracking
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/track/event` | Track single behavior event |
| POST | `/api/track/batch` | Batch track multiple events |

## Analytics Dashboard Sections

1. **KPI Cards** — 30-day revenue, orders, AOV, customers, events tracked
2. **Conversion Funnel** — Visual funnel with drop-off percentages
3. **Revenue Chart** — Dual-axis bar/line chart (revenue + order count over time)
4. **Attribution Report** — Doughnut chart + conversion bar chart + detailed table
5. **Category Performance** — Table with view→cart and cart→purchase rates
6. **Top Products** — Horizontal bar chart comparing views vs purchases

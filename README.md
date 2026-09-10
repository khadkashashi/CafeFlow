# CafeFlow 

**CafeFlow** is a full-stack cafe management and online ordering system built with Django - covering everything from a waiter taking a dine-in order to a customer paying online with Khalti and tracking it in real time.

It was built from scratch as a learning project, milestone by milestone, with an emphasis on realistic business logic (not just CRUD): role-based staff permissions, financial data integrity, automatic inventory deduction, and a unified order pipeline that treats a walk-in table order and an online delivery order as the same underlying object.

---

## What it does

CafeFlow runs the full loop of a real cafe:

**For customers:**
- Browse the menu, add to cart, and check out with delivery/pickup options
- Pay with cash-on-delivery or **Khalti** (sandbox integration)
- Scan a table's QR code to order directly from where they're sitting
- Track an order's status in real time (Pending → Preparing → Ready → Completed)
- Earn and redeem loyalty points, leave reviews, reserve a table (with an optional food pre-order)
- Check loyalty points by phone number with no login required

**For staff, split by role:**
- **Waiters** manage tables and build orders incrementally, sending them to the kitchen when ready
- **Chefs** work a live kitchen queue (Queued → In Progress → Done)
- **Front Desk** handles billing, discounts, payments (with change calculation), refunds, and daily cash closing
- **Managers** get full oversight: reports, profit/loss, inventory, menu management, staff accounts, attendance, and shift tracking

Every feature above is reachable through its own UI - no step in daily operations requires opening the Django admin.

---

## Feature list

| Area | What's built |
|---|---|
| **Table management** | Full lifecycle (Available → Occupied → Cleaning → Available), location grouping, QR code auto-generation per table, merge/transfer between tables |
| **Ordering** | Persistent per-table draft orders, incremental add/remove, explicit "Send to Kitchen" step, unified `Order` model for dine-in/online/pickup |
| **Kitchen** | Real-time queue with start/complete actions that cascade order status automatically |
| **Billing & Payments** | Discounts, bill generation, cash payment with change calculation, Khalti online payment (sandbox), refunds, printable receipts |
| **Inventory** | Ingredients, recipes (linking menu items to ingredients), suppliers, purchase history, automatic stock deduction on every order, low-stock alerts |
| **Reports** | Revenue, best-sellers, payment method breakdown, profit & loss, daily cash closing reconciliation |
| **Customers** | Signup/login via username, email, or phone; profile pictures; order history; loyalty points (earn + redeem); public phone-based points lookup |
| **Reviews** | Order-linked and standalone reviews, shown on the public homepage |
| **Reservations** | Public reservation form with optional food pre-order, staff confirmation with table assignment, same-day availability checks |
| **Staff & HR** | Employee accounts created by managers, shift clock-in/out, attendance dashboard (present/completed/absent), expense tracking |
| **Access control** | Role-based permissions enforced at both the view level and the navigation UI — a role never sees a link it can't use |
| **Chatbot** | A locally-hosted (Ollama) assistant grounded in the real menu/hours data, answering customer questions on the public site |

---

## Tech stack

- **Backend:** Django 6, Python 3.13
- **Database:** SQLite (development)
- **Frontend:** Django templates, Bootstrap 5 (internal dashboards), custom CSS (public-facing pages)
- **Payments:** Khalti ePayment API (sandbox)
- **AI:** Ollama (local LLM) for the customer-facing chatbot
- **Auth:** Custom `User` model with role-based permissions, custom authentication backend for email/phone login

---

## Architecture highlights

A few design decisions worth calling out, since they came from real debugging, not just following a tutorial:

- **One `Order` model for every order source.** Dine-in, online, and pickup orders all flow through the same `Order`/`OrderItem` models with a `source` field. The kitchen, billing, and inventory systems have zero special-case logic for where an order came from.
- **Signals for cross-app decoupling.** Inventory deduction and kitchen ticket creation happen via Django signals — the `orders` app has no direct knowledge that `inventory` or `kitchen` exist.
- **Snapshotting for financial integrity.** `OrderItem.price` and `Invoice` totals are captured at the moment of the transaction, not read live from the menu — so a price change tomorrow doesn't rewrite yesterday's receipts.
- **Defense in depth on every restricted action.** UI hides buttons a role shouldn't use, but the backend view independently re-checks and blocks the same action — hiding a button is never the only protection.
- **Explicit state machines.** Every model with a lifecycle (`Order`, `Table`, `Reservation`, `KitchenOrder`, `Invoice`) has methods that own their own transitions (`mark_occupied()`, `send_to_kitchen()`, `check_fully_paid()`) rather than views reaching in and setting fields directly.

---

## Project structure

```
cafeflow/
├── accounts/        # Custom User model, roles, auth backends, signup
├── menu/            # Categories, food items, reviews
├── tables/          # Table lifecycle, waiter order screen, reception dashboard
├── orders/          # Order/OrderItem models, tracking
├── kitchen/         # Kitchen queue and ticket workflow
├── billing/         # Invoices, bill generation, receipts
├── payments/        # Payment records, Khalti integration, cash closing, refunds
├── inventory/       # Ingredients, recipes, suppliers, purchases
├── customers/       # Customer profiles, loyalty points, account page
├── reservations/    # Table reservations with optional pre-orders
├── employees/       # Staff accounts, shifts, attendance
├── notifications/   # Low-stock and payment alerts
├── reports/         # Revenue, profit/loss, reporting dashboards
├── expenses/        # Non-inventory expense tracking
├── cart/            # Session-based shopping cart
├── landing/         # Public homepage, menu, public review form
├── chatbot/         # Ollama-powered customer assistant
└── config/          # Project settings and URL routing
```

---

## Setup

```bash
git clone <this-repo>
cd cafeflow
python -m venv .venv
.venv\Scripts\activate        # Windows
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**Environment variables needed:**

```
KHALTI_SECRET_KEY=your_khalti_sandbox_key
```

Set `TIME_ZONE` in `config/settings.py` to your local timezone (defaults to `Asia/Kathmandu`).

For the chatbot, install and run [Ollama](https://ollama.com) locally with a model pulled (e.g. `ollama pull gemma2:2b`).

---

## Known limitations

Being upfront about what this project doesn't handle, rather than overselling it:

- QR-code table ordering doesn't lock a table at scan time - a stale scan combined with a fast second customer could theoretically both reach checkout before the table's status is rechecked.
- Split-bill and per-role discount limits (e.g., "waiters can discount up to X%") aren't implemented.
- Profit/loss is calculated on a cash basis (money spent vs. earned this period), not full accrual accounting against ingredients actually consumed per sale.
- No automated test suite yet - testing was done manually, end-to-end, through the actual UI.

---

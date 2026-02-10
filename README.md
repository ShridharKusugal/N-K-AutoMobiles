# NK AUTOMOBILES

Online Two-Wheeler Spare Parts Management System for NK AUTOMOBILES.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Setup Database:
   - Create a MySQL database named `nk_automobiles`.
   - Update `app.py` with your database credentials.
   - Import `database.sql` to create tables and seed data.

3. Run Application:
   ```bash
   python app.py
   ```

## Technology Stack
- Frontend: HTML, CSS, Bootstrap, JS
- Backend: Python (Flask)
- Database: MySQL

## User Workflow
The following diagram illustrates the customer journey on the NK Automobiles website:

```mermaid
graph LR
    A[Start <br> Home Page] --> B[Browse / <br> Search Products]
    B --> C[Add to Cart / <br> View Details]
    C --> D[Login / <br> Register]
    D --> E[Checkout <br> Address]
    E --> F[Payment <br> UPI/COD]
    F --> G[Order Confirmed]

    style A fill:#f9f,stroke:#333,stroke-width:2px
    style G fill:#4dff4d,stroke:#333,stroke-width:4px
```

For a more detailed and interactive visualization, see [website_flowchart_v2.html](./website_flowchart_v2.html).

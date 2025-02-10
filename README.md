# Airflow DAG: Product Status Tracking Pipeline 🚀

This project sets up an **ETL pipeline** using **Apache Airflow** and **PostgreSQL 15** to regularly load and process order status data for business users. The pipeline extracts data from `orders.csv`, `order_items.csv`, and `products.csv`, stores it in the **staging schema**, and creates a **view (`v_product_status_track`)** for business analysis.

## 📌 Business Requirements
- Business users want **real-time tracking** of product order statuses.
- PostgreSQL **traindb.staging** schema will store the raw data.
- A view (`v_product_status_track`) under **traindb.serving** schema will be available for analysts.
- **Data refresh frequency:** **Hourly** (Fresh data every hour).

## 📁 Repository Structure
- `dags/product_status_pipeline.py` → **Airflow DAG for ETL process**
- `sql/create_tables.sql` → **DDL script to create tables**
- `sql/load_data.sql` → **SQL script for data ingestion**
- `sql/create_view.sql` → **SQL script for creating the view**

## 🏗️ PostgreSQL Schema & Table Structure

### **1. Create Tables in PostgreSQL (`traindb.staging`)**
```sql
CREATE SCHEMA IF NOT EXISTS traindb.staging;

CREATE TABLE IF NOT EXISTS traindb.staging.orders (
    order_id INT PRIMARY KEY,
    order_date TIMESTAMP,
    customer_id INT,
    order_status VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS traindb.staging.order_items (
    order_item_id INT PRIMARY KEY,
    order_id INT NOT NULL REFERENCES traindb.staging.orders(order_id),
    product_id INT NOT NULL,
    quantity INT,
    subtotal NUMERIC(10, 2),
    total NUMERIC(10, 2)
);

CREATE TABLE IF NOT EXISTS traindb.staging.products (
    product_id INT PRIMARY KEY,
    product_category_id INT,
    product_name TEXT
);
```

### **2. Load Data into Tables**
```sql
COPY traindb.staging.orders FROM '/tmp/orders.csv' DELIMITER ',' CSV HEADER;
COPY traindb.staging.order_items FROM '/tmp/order_items.csv' DELIMITER ',' CSV HEADER;
COPY traindb.staging.products FROM '/tmp/products.csv' DELIMITER ',' CSV HEADER;
```

### **3. Create View in `traindb.serving` Schema**
```sql
CREATE SCHEMA IF NOT EXISTS traindb.serving;

CREATE OR REPLACE VIEW traindb.serving.v_product_status_track AS
SELECT 
    o.order_id,
    o.order_date,
    oi.product_id,
    p.product_name,
    p.product_category_id,
    oi.quantity,
    oi.subtotal,
    oi.total AS total_price,
    o.order_status
FROM traindb.staging.orders o
JOIN traindb.staging.order_items oi ON o.order_id = oi.order_id
JOIN traindb.staging.products p ON oi.product_id = p.product_id;
```

---

## 🚀 Setting Up Airflow & Running the DAG

### **1. Configure PostgreSQL Connection in Airflow**
- Go to **Airflow UI > Admin > Connections**
- Add a new connection:
  - **Conn ID:** `postgresql_conn`
  - **Conn Type:** `Postgres`
  - **Host:** `postgres`
  - **Schema:** `traindb`
  - **Login:** `airflow`
  - **Password:** `airflow`
  - **Port:** `5432`

### **2. Deploy & Run DAG**

1. **Copy the DAG file into Airflow:**
   ```bash
   docker cp product_status_pipeline.py airflow-webserver:/opt/airflow/dags/
   ```

2. **Trigger DAG in Airflow UI:**
   - Open **Airflow Web UI** (`http://localhost:8080`).
   - Locate `product_status_pipeline` DAG.
   - Click **Trigger DAG**.

3. **Check Logs:** Monitor logs in **Airflow UI** or using:
   ```bash
   docker logs airflow-webserver
   ```

### **3. Automate Data Refresh Every Hour**
The DAG is scheduled to **run hourly (`@hourly`)** to keep the view updated.

---

## 📌 Summary
- **Airflow DAG** processes & loads order data every hour.
- **PostgreSQL staging schema (`traindb.staging`)** holds raw data.
- **Business users query `v_product_status_track` from `traindb.serving` schema**.
- **Pipeline ensures up-to-date insights on order & product status**.


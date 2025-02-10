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

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

COPY traindb.staging.orders FROM '/tmp/orders.csv' DELIMITER ',' CSV HEADER;
COPY traindb.staging.order_items FROM '/tmp/order_items.csv' DELIMITER ',' CSV HEADER;
COPY traindb.staging.products FROM '/tmp/products.csv' DELIMITER ',' CSV HEADER;

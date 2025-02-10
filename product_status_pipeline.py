from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 11, 20),
    'retries': 1,
    'retry_delay': timedelta(seconds=5)
}

with DAG('product_status_pipeline', default_args=default_args, schedule_interval='@hourly', catchup=False) as dag:

    truncate_tables = PostgresOperator(
        task_id='truncate_tables',
        postgres_conn_id='postgresql_conn',
        sql="""
        TRUNCATE traindb.staging.orders, traindb.staging.order_items, traindb.staging.products RESTART IDENTITY;
        """
    )

    create_tables = PostgresOperator(
        task_id='create_tables',
        postgres_conn_id='postgresql_conn',
        sql="""
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
        """
    )

    load_orders = PostgresOperator(
        task_id='load_orders',
        postgres_conn_id='postgresql_conn',
        sql="COPY traindb.staging.orders FROM '/tmp/orders.csv' DELIMITER ',' CSV HEADER;"
    )

    load_order_items = PostgresOperator(
        task_id='load_order_items',
        postgres_conn_id='postgresql_conn',
        sql="COPY traindb.staging.order_items FROM '/tmp/order_items.csv' DELIMITER ',' CSV HEADER;"
    )

    load_products = PostgresOperator(
        task_id='load_products',
        postgres_conn_id='postgresql_conn',
        sql="COPY traindb.staging.products FROM '/tmp/products.csv' DELIMITER ',' CSV HEADER;"
    )

    create_view = PostgresOperator(
        task_id='create_view',
        postgres_conn_id='postgresql_conn',
        sql="""
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
        """
    )

    truncate_tables >> create_tables >> [load_orders, load_order_items, load_products] >> create_view

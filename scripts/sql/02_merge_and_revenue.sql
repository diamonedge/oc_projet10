-- Fusion des données ERP, liaison et web
CREATE OR REPLACE TABLE products_merged AS
SELECT
    e.product_id,
    l.id_web,
    w.clean_sku AS sku,
    e.onsale_web,
    e.price,
    e.stock_quantity,
    e.stock_status,
    w.total_sales,
    w.post_title,
    w.post_name,
    w.post_type,
    w.post_date,
    w.post_modified
FROM erp_clean e
INNER JOIN liaison_clean l
    ON e.product_id = l.product_id
INNER JOIN web_clean w
    ON l.id_web = w.clean_sku
WHERE l.id_web IS NOT NULL;


-- Calcul du chiffre d'affaires par produit
CREATE OR REPLACE TABLE revenue_by_product AS
SELECT
    product_id,
    sku,
    post_title,
    price,
    total_sales,
    ROUND(price * total_sales, 2) AS revenue
FROM products_merged;


-- Calcul du chiffre d'affaires total
CREATE OR REPLACE TABLE total_revenue AS
SELECT
    ROUND(SUM(revenue), 2) AS total_revenue
FROM revenue_by_product;

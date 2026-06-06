-- Nettoyage ERP
CREATE OR REPLACE TABLE erp_clean AS
SELECT
    CAST(product_id AS INTEGER) AS product_id,
    CAST(onsale_web AS INTEGER) AS onsale_web,
    CAST(price AS DOUBLE) AS price,
    CAST(stock_quantity AS INTEGER) AS stock_quantity,
    CAST(stock_status AS VARCHAR) AS stock_status
FROM raw_erp
WHERE product_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY product_id
    ORDER BY product_id
) = 1;


-- Nettoyage liaison
CREATE OR REPLACE TABLE liaison_clean AS
SELECT
    CAST(product_id AS INTEGER) AS product_id,
    NULLIF(TRIM(CAST(id_web AS VARCHAR)), '') AS id_web
FROM raw_liaison
WHERE product_id IS NOT NULL
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY product_id
    ORDER BY product_id
) = 1;


-- Étape intermédiaire attendue par l'énoncé :
-- web après suppression des SKU manquants = 1428 lignes
CREATE OR REPLACE TABLE web_without_missing_sku AS
SELECT
    NULLIF(TRIM(CAST(sku AS VARCHAR)), '') AS sku,
    *
FROM raw_web
WHERE sku IS NOT NULL
  AND NULLIF(TRIM(CAST(sku AS VARCHAR)), '') IS NOT NULL;


-- Nettoyage web final :
-- on conserve une seule ligne par SKU,
-- en priorisant les lignes post_type = 'product' plutôt que les pièces jointes.
CREATE OR REPLACE TABLE web_clean AS
SELECT *
EXCLUDE (row_num)
FROM (
    SELECT
        NULLIF(TRIM(CAST(sku AS VARCHAR)), '') AS clean_sku,
        CAST(virtual AS INTEGER) AS virtual,
        CAST(downloadable AS INTEGER) AS downloadable,
        CAST(rating_count AS INTEGER) AS rating_count,
        CAST(average_rating AS DOUBLE) AS average_rating,
        CAST(total_sales AS INTEGER) AS total_sales,
        CAST(tax_status AS VARCHAR) AS tax_status,
        CAST(tax_class AS VARCHAR) AS tax_class,
        CAST(post_author AS INTEGER) AS post_author,
        post_date,
        post_date_gmt,
        CAST(post_content AS VARCHAR) AS post_content,
        CAST(post_title AS VARCHAR) AS post_title,
        CAST(post_excerpt AS VARCHAR) AS post_excerpt,
        CAST(post_status AS VARCHAR) AS post_status,
        CAST(comment_status AS VARCHAR) AS comment_status,
        CAST(ping_status AS VARCHAR) AS ping_status,
        CAST(post_password AS VARCHAR) AS post_password,
        CAST(post_name AS VARCHAR) AS post_name,
        post_modified,
        post_modified_gmt,
        CAST(post_content_filtered AS VARCHAR) AS post_content_filtered,
        CAST(post_parent AS INTEGER) AS post_parent,
        CAST(guid AS VARCHAR) AS guid,
        CAST(menu_order AS INTEGER) AS menu_order,
        CAST(post_type AS VARCHAR) AS post_type,
        CAST(post_mime_type AS VARCHAR) AS post_mime_type,
        CAST(comment_count AS INTEGER) AS comment_count,
        ROW_NUMBER() OVER (
            PARTITION BY NULLIF(TRIM(CAST(sku AS VARCHAR)), '')
            ORDER BY
                CASE WHEN post_type = 'product' THEN 0 ELSE 1 END,
                post_modified DESC
        ) AS row_num
    FROM raw_web
    WHERE sku IS NOT NULL
      AND NULLIF(TRIM(CAST(sku AS VARCHAR)), '') IS NOT NULL
)
WHERE row_num = 1;

with source_orders as (
    select * from {{ ref('raw_orders') }}
)

select
    order_id,
    ordered_at,
    customer_key,
    region,
    currency,
    net_amount,
    tax_amount,
    gross_amount as gross_revenue,
    gross_amount,
    order_status
from source_orders

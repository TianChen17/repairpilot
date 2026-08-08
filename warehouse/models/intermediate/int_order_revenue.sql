select
    order_id,
    ordered_at,
    region,
    currency,
    gross_revenue,
    gross_revenue as gross_amount,
    order_status
from {{ ref('stg_orders') }}
where order_status = 'completed'

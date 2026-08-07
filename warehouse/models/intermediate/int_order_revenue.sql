select
    order_id,
    ordered_at,
    region,
    currency,
    gross_amount,
    order_status
from {{ ref('stg_orders') }}
where order_status = 'completed'


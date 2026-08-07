select
    ordered_at::date as revenue_date,
    region,
    currency,
    count(*) as completed_orders,
    sum(gross_amount) as gross_amount
from {{ ref('int_order_revenue') }}
group by 1, 2, 3

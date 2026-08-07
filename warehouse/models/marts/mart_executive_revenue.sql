select
    revenue_date,
    region,
    currency,
    completed_orders,
    gross_amount,
    sum(gross_amount) over (
        partition by currency order by revenue_date
        rows between 6 preceding and current row
    ) as seven_day_gross_amount
from {{ ref('fct_daily_revenue') }}


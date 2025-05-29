# ✅ app/services/prompt_builder.py

few_shot_examples = [
    {
        "question": "Show total revenue by region",
        "sql": "SELECT region, SUM(quantity * price) FROM orders GROUP BY region;"
    },
    {
        "question": "List all orders from the year 2024",
        "sql": "SELECT * FROM orders WHERE EXTRACT(YEAR FROM order_date) = 2024;"
    },
    {
        "question": "What is the average order value by product?",
        "sql": "SELECT product_name, AVG(quantity * price) FROM orders GROUP BY product_name;"
    },
    {
        "question": "Show total revenue by month for 2024",
        "sql": "SELECT DATE_TRUNC('month', order_date), SUM(quantity * price) FROM orders WHERE EXTRACT(YEAR FROM order_date) = 2024 GROUP BY DATE_TRUNC('month', order_date);"
    },
    {
        "question": "Profit margin analysis",
        "sql": "/* Error: Missing columns. Available: id, customer_name, product_name, quantity, price, order_date, region */"
    }
]

def build_prompt(user_question: str, schema: str) -> str:
    prompt = (
        "Generate PostgreSQL SQL using ONLY THESE COLUMNS:\n"
        f"{schema}\n\n"
        "RULES:\n"
        "- No column aliases (AS)\n"
        "- No table prefixes\n"
        "- Use EXTRACT()/DATE_TRUNC() for dates\n"
        "- Do not include markdown or explanation\n\n"
    )

    for ex in few_shot_examples:
        prompt += f"Question: {ex['question']}\nSQL: {ex['sql']}\n\n"

    prompt += f"Question: {user_question}\nSQL:"
    return prompt

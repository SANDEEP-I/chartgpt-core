# ✅ app/services/response_formatter.py

def format_response_for_frontend(columns: list[str], rows: list[list]) -> dict:
    # Case 1: Return KPI for single row, single value
    if len(columns) == 1 and len(rows) == 1:
        return {
            "type": "kpi",
            "data": {
                "label": columns[0].replace("_", " ").title(),
                "value": str(rows[0][0])
            }
        }

    # Case 2: Return chart if first column is label-like
    if len(columns) == 2:
        label_col, value_col = columns
        data = [
            {"name": str(row[0]), "value": row[1]}
            for row in rows
        ]
        return {
            "type": "chart",
            "chartType": "bar",
            "data": data
        }

    # Fallback: return raw table structure
    return {
        "type": "table",
        "data": {
            "columns": columns,
            "rows": rows
        }
    }

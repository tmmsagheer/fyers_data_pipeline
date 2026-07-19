import os
import pandas as pd
from jinja2 import Template

def generate_dashboard(data_dir="data", output_file="dashboard.html"):
    stats = []
    
    if not os.path.exists(data_dir):
        print("Data directory not found.")
        return
        
    for file in os.listdir(data_dir):
        if file.endswith(".parquet"):
            symbol = file.replace(".parquet", "")
            filepath = os.path.join(data_dir, file)
            
            # Read only datetime column for speed
            df = pd.read_parquet(filepath, columns=['datetime'])
            
            if df.empty:
                continue
                
            min_date = df['datetime'].min()
            max_date = df['datetime'].max()
            total_rows = len(df)
            
            # Estimate missing data (Assuming ~252 trading days/year, 375 trading minutes/day)
            days_span = (max_date - min_date).days
            estimated_trading_days = int(days_span * (252 / 365))
            expected_rows = max(1, estimated_trading_days * 375) 
            missing_estimate = max(0, expected_rows - total_rows)
            health_pct = min(100.0, round((total_rows / expected_rows) * 100, 2))
            
            stats.append({
                "Symbol": symbol,
                "Start Date": min_date.strftime("%Y-%m-%d"),
                "End Date": max_date.strftime("%Y-%m-%d"),
                "Rows": f"{total_rows:,}",
                "Expected Missing": f"{missing_estimate:,}",
                "Health": f"{health_pct}%",
                "StatusClass": "healthy" if health_pct > 95 else "warning"
            })
            
    # Sort alphabetically by symbol
    stats = sorted(stats, key=lambda x: x['Symbol'])

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>NSE500 1-Min Data Dashboard</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 30px; background-color: #f4f7f6; }
            h2 { color: #333; }
            table { border-collapse: collapse; width: 100%; background: white; box-shadow: 0 1px 3px rgba(0,0,0,0.2); }
            th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
            th { background-color: #2c3e50; color: white; position: sticky; top: 0; }
            tr:nth-child(even) { background-color: #f9f9f9; }
            tr:hover { background-color: #f1f1f1; }
            .healthy { color: #27ae60; font-weight: bold; }
            .warning { color: #e67e22; font-weight: bold; }
        </style>
    </head>
    <body>
        <h2>Data Lake Pipeline Dashboard</h2>
        <table>
            <tr>
                <th>Symbol</th><th>Start Date</th><th>End Date</th>
                <th>Actual Rows</th><th>Est. Missing Rows</th><th>Data Health</th>
            </tr>
            {% for row in stats %}
            <tr>
                <td>{{ row['Symbol'] }}</td>
                <td>{{ row['Start Date'] }}</td>
                <td>{{ row['End Date'] }}</td>
                <td>{{ row['Rows'] }}</td>
                <td>{{ row['Expected Missing'] }}</td>
                <td class="{{ row['StatusClass'] }}">{{ row['Health'] }}</td>
            </tr>
            {% endfor %}
        </table>
    </body>
    </html>
    """
    
    template = Template(html_template)
    with open(output_file, "w") as f:
        f.write(template.render(stats=stats))
    print(f"Dashboard generated successfully at {output_file}")
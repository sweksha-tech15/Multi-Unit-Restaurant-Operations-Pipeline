import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sqlalchemy import create_engine  

# 1. Update these details based on your SSMS connection setup
SERVER = '.\\SQLEXPRESS'
DATABASE = 'PIZZA DB'

try:
    # Create the backend connection bridge
    connection_string = f"mssql+pyodbc://@{SERVER}/{DATABASE}?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    engine = create_engine(connection_string)
    print(" Successfully connected to SQL Server 2025!")
except Exception as e:
    print(f"Database Connection Failed: {e}")

# 2. Extract Data via Advanced SQL Queries
print("Extracting supply chain & operational metrics...")

# Query A: Kitchen Capacity Peak Load Analysis
# Query A: Kitchen Capacity Peak Load Analysis (Using explicit database and schema tracking)
hourly_query = """
WITH HourlySales AS (
    SELECT 
        DATEPART(HOUR, order_time) AS order_hour,
        COUNT(DISTINCT order_id) AS orders_handled,
        SUM(quantity) AS pizzas_baked  -- If your DB uses 'quanlity', change this line to SUM(quanlity)
    FROM [PIZZA DB].dbo.pizza_sales
    GROUP BY DATEPART(HOUR, order_time)
)
SELECT 
    order_hour,
    orders_handled,
    pizzas_baked,
    RANK() OVER (ORDER BY pizzas_baked DESC) as kitchen_stress_rank
FROM HourlySales;
"""

# Query B: High-Contribution Menu Matrix (Using explicit database and schema tracking)
menu_query = """
SELECT 
    pizza_name,
    SUM(quantity) as units_sold,  -- If your DB uses 'quanlity', change this line to SUM(quanlity)
    SUM(total_price) as total_revenue
FROM [PIZZA DB].dbo.pizza_sales
GROUP BY pizza_name;

"""

# Read SQL tables directly into Pandas DataFrames
df_hourly = pd.read_sql(hourly_query, engine)
df_menu = pd.read_sql(menu_query, engine)

# 3. Render the Visual Analytics Dashboard
print("Generating visualization dashboard windows...")
sns.set_theme(style="whitegrid")
fig, axes = plt.subplots(1, 2, figsize=(16, 6))

# Plot 1: Operational Capacity Peak Hours (Left Chart)
sns.barplot(
    data=df_hourly.sort_values('order_hour'), 
    x='order_hour', 
    y='pizzas_baked', 
    ax=axes[0], 
    palette="YlOrRd"
)
axes[0].set_title('Operational Peak Load: Pizzas Baked Per Hour', fontsize=13, fontweight='bold', pad=15)
axes[0].set_xlabel('Hour of the Day (24h format)')
axes[0].set_ylabel('Total Units Fabricated')

# Plot 2: Top 10 High-Revenue Menu Drivers (Right Chart)
top_10_menu = df_menu.sort_values(by='total_revenue', ascending=False).head(10)
sns.barplot(
    data=top_10_menu, 
    x='total_revenue', 
    y='pizza_name', 
    ax=axes[1], 
    palette="Blues_r"
)
axes[1].set_title('Top 10 High-Contribution Menu Items ($)', fontsize=13, fontweight='bold', pad=15)
axes[1].set_xlabel('Total Generated Revenue')
axes[1].set_ylabel('')


plt.tight_layout()
print("Saving dashboard plot...")

#  high-res PNG file
plt.savefig('dashboard_output.png', dpi=300, bbox_inches='tight')

print("Displaying dashboard popup...")
plt.show()
plt.show()
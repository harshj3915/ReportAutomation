import pandas as pd
import dash
from dash import dcc, html, dash_table, Input, Output, callback
import plotly.express as px
from datetime import datetime, date
import os
import glob
import calendar

# Automated Path Configuration Functions
def get_month_year_combinations(latest_month_year):
    """
    Get the latest month, last month, and last year combinations
    """
    # Parse the latest month-year
    month_name, year = latest_month_year.split('-')
    year = int(year)
    month_num = list(calendar.month_name).index(month_name)
    
    # Calculate last month
    if month_num == 1:  # January
        last_month_num = 12
        last_month_year_num = year - 1
    else:
        last_month_num = month_num - 1
        last_month_year_num = year
    
    # Calculate last year same month
    last_year_month_num = month_num
    last_year_year_num = year - 1
    
    # Convert back to names
    last_month_name = calendar.month_name[last_month_num]
    last_year_month_name = calendar.month_name[last_year_month_num]
    
    return {
        'latest': {'month': month_name, 'year': year, 'folder': f"{month_name}-{year}"},
        'last_month': {'month': last_month_name, 'year': last_month_year_num, 'folder': f"{last_month_name}-{last_month_year_num}"},
        'last_year': {'month': last_year_month_name, 'year': last_year_year_num, 'folder': f"{last_year_month_name}-{last_year_year_num}"}
    }

def find_file_by_keyword(folder_path, keyword):
    """
    Find a file in the folder that contains the keyword in its name
    """
    if not os.path.exists(folder_path):
        return None
    
    files = os.listdir(folder_path)
    for file in files:
        if keyword.lower() in file.lower() and file.endswith('.xlsx'):
            return os.path.join(folder_path, file)
    return None

def setup_automated_paths(latest_month_year, dsr_folder_path=None):
    """
    Setup all paths automatically based on the latest month-year input
    
    Parameters:
    latest_month_year: str - Format: "June-2025"
    dsr_folder_path: str - Full path to DSR folder (e.g., "C:/Users/Username/Documents/DSR")
                           If None, defaults to "DSR" in current directory
    
    Returns:
    dict containing all the required paths and configurations
    """
    
    # Get month-year combinations
    dates = get_month_year_combinations(latest_month_year)
    
    # Base DSR folder path - use provided path or default to current directory
    if dsr_folder_path is None:
        dsr_path = os.path.join(os.getcwd(), "DSR")
    else:
        dsr_path = os.path.abspath(dsr_folder_path)
        
    print(f"🔍 Looking for DSR folder at: {dsr_path}")
    
    # Prepare results
    sheet_info = []
    
    # Process each period (last_month, last_year, latest)
    periods = ['last_month', 'last_year', 'latest']
    display_names = [
        f"{dates['last_month']['month']} {dates['last_month']['year'] % 100}",  # May 25
        f"{dates['last_year']['month']} {dates['last_year']['year'] % 100}",   # June 24
        f"{dates['latest']['month']} {dates['latest']['year'] % 100}"          # June 25
    ]
    
    for i, period in enumerate(periods):
        period_data = dates[period]
        folder_path = os.path.join(dsr_path, period_data['folder'])
        
        # Find invoice file
        invoice_file = find_file_by_keyword(folder_path, 'invoice')
        if invoice_file:
            # Get the first sheet (since invoice files have only one sheet)
            try:
                xl = pd.ExcelFile(invoice_file)
                sheet_name = xl.sheet_names[0] if xl.sheet_names else 'Sheet1'
            except:
                sheet_name = 'Sheet1'
            
            # Make path relative to current working directory
            rel_path = os.path.relpath(invoice_file, os.getcwd())
            sheet_info.append((rel_path, sheet_name, display_names[i]))
    
    return {
        'sheet_info': sheet_info,
        'dates': dates
    }

# AUTOMATED PATH CONFIGURATION
print("Dashboard.py - Automated Path Configuration")
print("==========================================")

# Try automated configuration first
try:
    # You can modify these lines to directly set the month and DSR path
    # For dashboard.py, we'll use defaults or you can uncomment the input lines below
    
    # latest_month_year = input("Enter the latest month-year (e.g., 'June-2025'): ").strip()
    # dsr_path = input("Enter full path to DSR folder (or press Enter for default './DSR'): ").strip() or None
    
    latest_month_year = "June-2025"  # Default for dashboard - change this as needed
    dsr_path = None  # Default - change this to your DSR folder path if needed
    # Example: dsr_path = r"C:\Users\91843\Documents\MyData\DSR"
    
    # Setup all paths automatically
    config = setup_automated_paths(latest_month_year, dsr_path)
    sheet_info = config['sheet_info']
    
    print(f"✅ Configuration successful for {latest_month_year}!")
    print(f"📁 Found {len(sheet_info)} invoice files:")
    for i, (path, sheet, display) in enumerate(sheet_info):
        print(f"   {i+1}. {display}: {path} -> {sheet}")
    
    
except Exception as e:
    print(f"❌ Error in automated setup: {e}")
    print("🔄 Falling back to manual configuration...")
      # Fallback to manual configuration
    sheet_info = [
        ('test2/may25-final.xlsx', 'Sheet1', 'May 25'),   # Last month raw sheet
        ('test2/June24_Invoice.xlsx', 'Raw data June 24', 'June 24'),        # Last year raw sheet
        ('test2/June25.xlsx', 'Sheet1', 'June 25')                # Latest month raw sheet
    ]

# Read the session data with specific columns
important_columns = [
    'Day',
    'Channel',
    'Sessions',
    'Purchases',
    'Purchase revenue',
    'CG',
    'Category'
]

# Collect day-wise and TYPE-wise sums for each sheet
results = []
type_results = []
dfs = []  # Store the processed dataframes for each sheet

# First, process each sheet and store the dataframe, day sum, and type sum
for idx, (path, sheet, display_name) in enumerate(sheet_info):
    df = pd.read_excel(path, sheet_name=sheet)
    filtered_df = df[~df['idg'].isin(['FOC', 'Remove', 'WRT'])].copy()
    filtered_df['InvoiceDay'] = pd.to_datetime(filtered_df['InvoiceDate'], dayfirst=True, errors='coerce').dt.day
      # Map CC to Jumbo.ae in the TYPE column
    filtered_df['TYPE'] = filtered_df['TYPE'].replace('CC', 'Jumbo.ae')
    
    # Group by ProductDesc and sum both Amount Invoiced W.O. VAT and QtyOrdered
    product_totals = filtered_df.groupby('ProductDesc').agg({
        'Amount Invoiced W.O. VAT': 'sum',
        'QtyOrdered': 'sum'
    }).sort_values(by='Amount Invoiced W.O. VAT', ascending=False)
    
    type_results.append((idx, product_totals))  # Store the index instead of sheet name    # Store the processed dataframe
    dfs.append(filtered_df)

# Initialize Dash app
app = dash.Dash(__name__)

# Get unique values for filters from all dataframes
all_days = []
all_brands = []
all_idgs = []
all_types = []

for df in dfs:
    # Get unique invoice days (1-31)
    days = df['InvoiceDay'].dropna().unique()
    all_days.extend(days)
    all_brands.extend(df['Brand'].dropna().unique())
    all_idgs.extend(df['idg'].dropna().unique())
    all_types.extend(df['TYPE'].dropna().unique())

# Remove duplicates and sort
unique_days = sorted(list(set(all_days)))
unique_brands = sorted(list(set(all_brands)))
unique_idgs = sorted(list(set(all_idgs)))
unique_types = sorted(list(set(all_types)))

# Create options for dropdowns
day_options = [{'label': f'Day {int(day)}', 'value': day} for day in unique_days if not pd.isna(day)]
brand_options = [{'label': brand, 'value': brand} for brand in unique_brands]
idg_options = [{'label': idg, 'value': idg} for idg in unique_idgs]
type_options = [{'label': type_val, 'value': type_val} for type_val in unique_types]

# Weekday options for first day of month selection
weekday_options = [
    {'label': 'Monday', 'value': 0},
    {'label': 'Tuesday', 'value': 1},
    {'label': 'Wednesday', 'value': 2},
    {'label': 'Thursday', 'value': 3},
    {'label': 'Friday', 'value': 4},
    {'label': 'Saturday', 'value': 5},
    {'label': 'Sunday', 'value': 6}
]

# Week calculation function
def calculate_week_number(day, first_day_of_month_weekday):
    """
    Calculate week number based on first day of month logic
    first_day_of_month_weekday: 0=Monday, 1=Tuesday, ..., 6=Sunday
    """
    if day == 1:
        return 1
    
    # Days in week 1 (from 1st to first Sunday)
    if first_day_of_month_weekday == 6:  # If 1st is Sunday
        days_in_week1 = 1
    else:  # If 1st is Monday-Saturday
        days_in_week1 = 7 - first_day_of_month_weekday
    
    if day <= days_in_week1:
        return 1
    
    # For remaining days, calculate which week
    remaining_days = day - days_in_week1
    return 2 + (remaining_days - 1) // 7

# Function to add week calculation to dataframes based on selected first day
def add_week_calculation(dfs, selected_weekday):
    """Add week calculation to all dataframes based on selected first day of month"""
    for i, df in enumerate(dfs):
        if 'Week' in df.columns:
            df.drop('Week', axis=1, inplace=True)
        
        # Calculate week for each row based on selected weekday
        df['Week'] = df['InvoiceDay'].apply(lambda x: calculate_week_number(x, selected_weekday) if pd.notna(x) else None)

# Initialize with Monday as default (weekday 0)
add_week_calculation(dfs, 0)

# Get unique weeks for filter (will be updated dynamically)
def get_week_options(dfs):
    all_weeks = []
    for df in dfs:
        if 'Week' in df.columns:
            weeks = df['Week'].dropna().unique()
            all_weeks.extend(weeks)
    
    unique_weeks = sorted(list(set(all_weeks))) if all_weeks else []
    return [{'label': f'Week {int(week)}', 'value': week} for week in unique_weeks if not pd.isna(week)]

week_options = get_week_options(dfs)

# Function to filter and aggregate data
def filter_and_aggregate_data(df, invoice_days, weeks, brands, idgs, types):
    filtered_df = df.copy()
    
    if invoice_days:
        filtered_df = filtered_df[filtered_df['InvoiceDay'].isin(invoice_days)]
    if weeks and 'Week' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Week'].isin(weeks)]
    if brands:
        filtered_df = filtered_df[filtered_df['Brand'].isin(brands)]
    if idgs:
        filtered_df = filtered_df[filtered_df['idg'].isin(idgs)]
    if types:
        filtered_df = filtered_df[filtered_df['TYPE'].isin(types)]
    
    # Always group by ProductDesc (product view)
    product_totals = filtered_df.groupby('ProductDesc').agg({
        'Amount Invoiced W.O. VAT': 'sum',
        'QtyOrdered': 'sum'
    }).sort_values(by='Amount Invoiced W.O. VAT', ascending=False)
    
    # Reset index and format
    df_display = product_totals.reset_index()
    df_display['Amount Invoiced W.O. VAT'] = df_display['Amount Invoiced W.O. VAT'].round(2)
    df_display['QtyOrdered'] = df_display['QtyOrdered'].round(0)
    
    return df_display.to_dict('records')

# Function to calculate summary metrics
def calculate_summary_metrics(dfs, invoice_days, weeks, brands, idgs, types, selected_weekday):
    if selected_weekday is not None:
        add_week_calculation(dfs, selected_weekday)
    
    summaries = []
    for i, df in enumerate(dfs):
        filtered_df = df.copy()
        
        if invoice_days:
            filtered_df = filtered_df[filtered_df['InvoiceDay'].isin(invoice_days)]
        if weeks and 'Week' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Week'].isin(weeks)]
        if brands:
            filtered_df = filtered_df[filtered_df['Brand'].isin(brands)]
        if idgs:
            filtered_df = filtered_df[filtered_df['idg'].isin(idgs)]
        if types:
            filtered_df = filtered_df[filtered_df['TYPE'].isin(types)]
        
        total_revenue = filtered_df['Amount Invoiced W.O. VAT'].sum()
        total_qty = filtered_df['QtyOrdered'].sum()
        unique_products = filtered_df['ProductDesc'].nunique()
        avg_order_value = total_revenue / total_qty if total_qty > 0 else 0
        
        summaries.append({
            'period': sheet_info[i][2],
            'total_revenue': total_revenue,
            'total_qty': total_qty,
            'unique_products': unique_products,
            'avg_order_value': avg_order_value
        })
    
    return summaries

# Function to create comparison analysis
def create_comparison_analysis(summaries):
    if len(summaries) < 3:
        return []
    
    current = summaries[2]  # Latest month (index 2)
    last_month = summaries[0]  # Last month (index 0)
    last_year = summaries[1]  # Last year (index 1)
    
    # Month-over-month comparison (current vs last month)
    mom_revenue_change = ((current['total_revenue'] - last_month['total_revenue']) / last_month['total_revenue'] * 100) if last_month['total_revenue'] > 0 else 0
    mom_qty_change = ((current['total_qty'] - last_month['total_qty']) / last_month['total_qty'] * 100) if last_month['total_qty'] > 0 else 0
    
    # Year-over-year comparison (current vs last year)
    yoy_revenue_change = ((current['total_revenue'] - last_year['total_revenue']) / last_year['total_revenue'] * 100) if last_year['total_revenue'] > 0 else 0
    yoy_qty_change = ((current['total_qty'] - last_year['total_qty']) / last_year['total_qty'] * 100) if last_year['total_qty'] > 0 else 0
    
    comparison_data = [
        {
            'Metric': 'Revenue (W.O. VAT)',
            f'Last Month ({sheet_info[0][2]})': f"AED {last_month['total_revenue']:,.2f}",
            f'Last Year ({sheet_info[1][2]})': f"AED {last_year['total_revenue']:,.2f}",
            f'Current ({sheet_info[2][2]})': f"AED {current['total_revenue']:,.2f}",
            'YoY Change %': f"{yoy_revenue_change:+.1f}%",
            'MoM Change %': f"{mom_revenue_change:+.1f}%"
        },
        {
            'Metric': 'Quantity Ordered',
            f'Last Month ({sheet_info[0][2]})': f"{last_month['total_qty']:,.0f}",
            f'Last Year ({sheet_info[1][2]})': f"{last_year['total_qty']:,.0f}",
            f'Current ({sheet_info[2][2]})': f"{current['total_qty']:,.0f}",
            'YoY Change %': f"{yoy_qty_change:+.1f}%",
            'MoM Change %': f"{mom_qty_change:+.1f}%"
        },
        {
            'Metric': 'Unique Products',
            f'Last Month ({sheet_info[0][2]})': f"{last_month['unique_products']:,}",
            f'Last Year ({sheet_info[1][2]})': f"{last_year['unique_products']:,}",
            f'Current ({sheet_info[2][2]})': f"{current['unique_products']:,}",
            'YoY Change %': f"{((current['unique_products'] - last_year['unique_products']) / last_year['unique_products'] * 100):+.1f}%" if last_year['unique_products'] > 0 else "N/A",
            'MoM Change %': f"{((current['unique_products'] - last_month['unique_products']) / last_month['unique_products'] * 100):+.1f}%" if last_month['unique_products'] > 0 else "N/A"
        },
        {
            'Metric': 'Avg Order Value',
            f'Last Month ({sheet_info[0][2]})': f"AED {last_month['avg_order_value']:.2f}",
            f'Last Year ({sheet_info[1][2]})': f"AED {last_year['avg_order_value']:.2f}",
            f'Current ({sheet_info[2][2]})': f"AED {current['avg_order_value']:.2f}",
            'YoY Change %': f"{((current['avg_order_value'] - last_year['avg_order_value']) / last_year['avg_order_value'] * 100):+.1f}%" if last_year['avg_order_value'] > 0 else "N/A",
            'MoM Change %': f"{((current['avg_order_value'] - last_month['avg_order_value']) / last_month['avg_order_value'] * 100):+.1f}%" if last_month['avg_order_value'] > 0 else "N/A"
        }
    ]
    
    return comparison_data

# Function to get top performers across all periods
def get_top_performers(dfs, invoice_days, weeks, brands, idgs, types, selected_weekday, top_n=10):
    if selected_weekday is not None:
        add_week_calculation(dfs, selected_weekday)
    
    # Get top 10 products from the latest month (index 2)
    latest_df = dfs[2].copy()
    
    # Apply filters to latest month data
    if invoice_days:
        latest_df = latest_df[latest_df['InvoiceDay'].isin(invoice_days)]
    if weeks and 'Week' in latest_df.columns:
        latest_df = latest_df[latest_df['Week'].isin(weeks)]
    if brands:
        latest_df = latest_df[latest_df['Brand'].isin(brands)]
    if idgs:
        latest_df = latest_df[latest_df['idg'].isin(idgs)]
    if types:
        latest_df = latest_df[latest_df['TYPE'].isin(types)]
    
    # Get top products from latest month
    latest_product_totals = latest_df.groupby('ProductDesc').agg({
        'Amount Invoiced W.O. VAT': 'sum',
        'QtyOrdered': 'sum'
    }).sort_values(by='Amount Invoiced W.O. VAT', ascending=False)
    
    # Get top N products from latest month
    top_products_latest = latest_product_totals.head(top_n)
    top_product_names = top_products_latest.index.tolist()
    
    # Now get data for these products from all periods
    all_products_data = {}
    
    for product_name in top_product_names:
        all_products_data[product_name] = {
            'ProductDesc': product_name,
            f'{sheet_info[2][2]}_Revenue': top_products_latest.loc[product_name, 'Amount Invoiced W.O. VAT'],
            f'{sheet_info[2][2]}_Qty': top_products_latest.loc[product_name, 'QtyOrdered']
        }
        
        # Get data from other periods for the same products
        for i, df in enumerate(dfs[:2]):  # Only check first two periods (not the latest)
            filtered_df = df.copy()
            
            # Apply same filters
            if invoice_days:
                filtered_df = filtered_df[filtered_df['InvoiceDay'].isin(invoice_days)]
            if weeks and 'Week' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Week'].isin(weeks)]
            if brands:
                filtered_df = filtered_df[filtered_df['Brand'].isin(brands)]
            if idgs:
                filtered_df = filtered_df[filtered_df['idg'].isin(idgs)]
            if types:
                filtered_df = filtered_df[filtered_df['TYPE'].isin(types)]
            
            period_name = sheet_info[i][2]
            
            # Check if product exists in this period
            product_data = filtered_df[filtered_df['ProductDesc'] == product_name]
            if not product_data.empty:
                revenue = product_data['Amount Invoiced W.O. VAT'].sum()
                qty = product_data['QtyOrdered'].sum()
            else:
                revenue = 0
                qty = 0
            
            all_products_data[product_name][f'{period_name}_Revenue'] = revenue
            all_products_data[product_name][f'{period_name}_Qty'] = qty    # Format the results
    formatted_top_products = []
    for i, (product_name, product_data) in enumerate(all_products_data.items()):
        # Calculate total revenue and quantity across all periods
        total_revenue = (product_data[f'{sheet_info[0][2]}_Revenue'] + 
                        product_data[f'{sheet_info[1][2]}_Revenue'] + 
                        product_data[f'{sheet_info[2][2]}_Revenue'])
        total_qty = (product_data[f'{sheet_info[0][2]}_Qty'] + 
                    product_data[f'{sheet_info[1][2]}_Qty'] + 
                    product_data[f'{sheet_info[2][2]}_Qty'])
        
        # Calculate comparisons
        current_revenue = product_data[f'{sheet_info[2][2]}_Revenue']
        last_year_revenue = product_data[f'{sheet_info[1][2]}_Revenue']
        last_month_revenue = product_data[f'{sheet_info[0][2]}_Revenue']
        
        # Year-over-year comparison
        if last_year_revenue > 0:
            yoy_change = ((current_revenue - last_year_revenue) / last_year_revenue) * 100
            yoy_display = f"{yoy_change:+.1f}%"
        else:
            yoy_display = "New Product"
        
        # Month-over-month comparison
        if last_month_revenue > 0:
            mom_change = ((current_revenue - last_month_revenue) / last_month_revenue) * 100
            mom_display = f"{mom_change:+.1f}%"
        else:
            mom_display = "New Product"
        
        formatted_top_products.append({
            'Rank': i + 1,
            'Product': product_name[:50] + '...' if len(product_name) > 50 else product_name,
            'Total Revenue': f"AED {total_revenue:,.2f}",
            'Total Qty': f"{total_qty:,.0f}",
            f"{sheet_info[0][2]} Revenue": f"AED {product_data[f'{sheet_info[0][2]}_Revenue']:,.2f}",
            f"{sheet_info[1][2]} Revenue": f"AED {product_data[f'{sheet_info[1][2]}_Revenue']:,.2f}",
            f"{sheet_info[2][2]} Revenue": f"AED {product_data[f'{sheet_info[2][2]}_Revenue']:,.2f}",
            'YoY Change %': yoy_display,
            'MoM Change %': mom_display
        })
    
    return formatted_top_products

# CONFIGURATION HELPER FUNCTION
def update_dashboard_configuration(new_month_year, dsr_folder_path=None):
    """
    Update the dashboard configuration with a new month-year and DSR path
    Call this function to change the data source month and/or DSR location
    
    Parameters:
    new_month_year: str - Format: "June-2025"
    dsr_folder_path: str - Full path to DSR folder (optional)
    """
    global sheet_info
    
    try:
        config = setup_automated_paths(new_month_year, dsr_folder_path)
        sheet_info = config['sheet_info']
        
        print(f"🔄 Dashboard updated for {new_month_year}!")
        if dsr_folder_path:
            print(f"📁 Using DSR folder: {dsr_folder_path}")
        print(f"📁 Now using {len(sheet_info)} files:")
        for i, (path, sheet, display) in enumerate(sheet_info):
            print(f"   {i+1}. {display}: {path} -> {sheet}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False

# Define the app layout
app.layout = html.Div([
    html.H1("Product Analysis Dashboard", style={'textAlign': 'center', 'marginBottom': 30}),    # Universal Filters Section
    html.Div([
        html.H3("Universal Filters", style={'textAlign': 'center', 'marginBottom': 20}),
        
        # First Day of Month Selector
        html.Div([
            html.Label("First Day of Month:", style={'fontWeight': 'bold', 'marginBottom': 5}),
            dcc.Dropdown(
                id='first-day-selector',
                options=weekday_options,
                value=0,  # Default to Monday
                placeholder="Select what day the 1st falls on",
                style={'marginBottom': 15}
            ),
            html.P("Select what day of the week the 1st of the month falls on to calculate weeks correctly.", 
                   style={'fontSize': '12px', 'color': 'gray', 'marginBottom': 20})
        ], style={'textAlign': 'center', 'marginBottom': 20}),
        
        # Filter Selection Note
        html.Div([
            html.P("Note: You can either filter by specific invoice days OR by weeks, but not both at the same time.", 
                   style={'textAlign': 'center', 'fontStyle': 'italic', 'color': '#666', 'marginBottom': 15})
        ]),
        
        html.Div([
            html.Div([
                html.Label("Invoice Day:", style={'fontWeight': 'bold', 'marginBottom': 5}),
                dcc.Dropdown(
                    id='invoice-day-filter',
                    options=day_options,
                    multi=True,
                    placeholder="Select Invoice Days (e.g., 1st, 3rd-13th)",
                    style={'marginBottom': 10}
                )
            ], style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),
            
            html.Div([
                html.Label("Week:", style={'fontWeight': 'bold', 'marginBottom': 5}),
                dcc.Dropdown(
                    id='week-filter',
                    options=week_options,
                    multi=True,
                    placeholder="Select Weeks",
                    style={'marginBottom': 10}
                )
            ], style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),
            
            html.Div([
                html.Label("Brand:", style={'fontWeight': 'bold', 'marginBottom': 5}),
                dcc.Dropdown(
                    id='brand-filter',
                    options=brand_options,
                    multi=True,
                    placeholder="Select Brands",
                    style={'marginBottom': 10}
                )
            ], style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),
            
            html.Div([
                html.Label("IDG:", style={'fontWeight': 'bold', 'marginBottom': 5}),
                dcc.Dropdown(
                    id='idg-filter',
                    options=idg_options,
                    multi=True,
                    placeholder="Select IDG",
                    style={'marginBottom': 10}
                )
            ], style={'width': '19%', 'display': 'inline-block', 'marginRight': '1%'}),
            
            html.Div([
                html.Label("Type:", style={'fontWeight': 'bold', 'marginBottom': 5}),
                dcc.Dropdown(
                    id='type-filter',
                    options=type_options,
                    multi=True,
                    placeholder="Select Types",
                    style={'marginBottom': 10}
                )
            ], style={'width': '19%', 'display': 'inline-block'})
            
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': 20})
          ], style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': 30}),
    
    # Top Performers Section
    html.Div([
        html.H3(f"🏆 Top 10 Performers from {sheet_info[2][2]} (with data from all periods)", style={'textAlign': 'center', 'marginBottom': 20}),
        dash_table.DataTable(
            id='top-performers-table',
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontFamily': 'Arial, sans-serif',
                'fontSize': '12px'
            },
            style_header={
                'backgroundColor': 'rgb(255, 193, 7)',
                'color': 'black',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },            style_data_conditional=[
                {
                    'if': {'row_index': 0},
                    'backgroundColor': '#fff3cd',
                    'fontWeight': 'bold'
                },
                {
                    'if': {'row_index': 1},
                    'backgroundColor': '#f8f9fa'
                },
                {
                    'if': {'row_index': 2},
                    'backgroundColor': '#f8f9fa'
                },
                # Positive YoY changes in green
                {
                    'if': {'filter_query': '{YoY Change %} contains "+"'},
                    'color': '#28a745',
                    'fontWeight': 'bold'
                },
                # Negative YoY changes in red
                {
                    'if': {'filter_query': '{YoY Change %} contains "-"'},
                    'color': '#dc3545',
                    'fontWeight': 'bold'
                },
                # Positive MoM changes in green
                {
                    'if': {'filter_query': '{MoM Change %} contains "+"'},
                    'color': '#28a745',
                    'fontWeight': 'bold'
                },
                # Negative MoM changes in red
                {
                    'if': {'filter_query': '{MoM Change %} contains "-"'},
                    'color': '#dc3545',
                    'fontWeight': 'bold'
                }
            ],
            style_data={
                'backgroundColor': 'rgb(248, 248, 248)',
                'border': '1px solid rgb(230, 230, 230)'
            },
            page_size=10
        )
    ], style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': 30, 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    
    # Tables Section - Side by Side
    html.Div([
        html.Div([
            html.H4(f"{sheet_info[0][2]} - Product Analysis", style={'textAlign': 'center', 'marginBottom': 15}),
            dash_table.DataTable(
                id='table-0',
                columns=[
                    {'name': 'Product Description', 'id': 'ProductDesc', 'type': 'text'},
                    {'name': 'Amount Invoiced (W.O. VAT)', 'id': 'Amount Invoiced W.O. VAT', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
                    {'name': 'Quantity Ordered', 'id': 'QtyOrdered', 'type': 'numeric', 'format': {'specifier': ',.0f'}}
                ],
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '12px'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data={
                    'backgroundColor': 'rgb(248, 248, 248)',
                    'border': '1px solid rgb(230, 230, 230)'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(240, 240, 240)'
                    }
                ],
                page_size=10,
                sort_action="native",
                filter_action="native"
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),
        
        html.Div([
            html.H4(f"{sheet_info[1][2]} - Product Analysis", style={'textAlign': 'center', 'marginBottom': 15}),
            dash_table.DataTable(
                id='table-1',
                columns=[
                    {'name': 'Product Description', 'id': 'ProductDesc', 'type': 'text'},
                    {'name': 'Amount Invoiced (W.O. VAT)', 'id': 'Amount Invoiced W.O. VAT', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
                    {'name': 'Quantity Ordered', 'id': 'QtyOrdered', 'type': 'numeric', 'format': {'specifier': ',.0f'}}
                ],
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '12px'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data={
                    'backgroundColor': 'rgb(248, 248, 248)',
                    'border': '1px solid rgb(230, 230, 230)'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(240, 240, 240)'
                    }
                ],
                page_size=10,
                sort_action="native",
                filter_action="native"
            )
        ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),
        
        html.Div([
            html.H4(f"{sheet_info[2][2]} - Product Analysis", style={'textAlign': 'center', 'marginBottom': 15}),
            dash_table.DataTable(
                id='table-2',
                columns=[
                    {'name': 'Product Description', 'id': 'ProductDesc', 'type': 'text'},
                    {'name': 'Amount Invoiced (W.O. VAT)', 'id': 'Amount Invoiced W.O. VAT', 'type': 'numeric', 'format': {'specifier': ',.2f'}},
                    {'name': 'Quantity Ordered', 'id': 'QtyOrdered', 'type': 'numeric', 'format': {'specifier': ',.0f'}}
                ],
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '12px'
                },
                style_header={
                    'backgroundColor': 'rgb(230, 230, 230)',
                    'fontWeight': 'bold',
                    'textAlign': 'center'
                },
                style_data={
                    'backgroundColor': 'rgb(248, 248, 248)',
                    'border': '1px solid rgb(230, 230, 230)'
                },
                style_data_conditional=[
                    {
                        'if': {'row_index': 'odd'},
                        'backgroundColor': 'rgb(240, 240, 240)'
                    }
                ],
                page_size=10,
                sort_action="native",
                filter_action="native"
            )
        ], style={'width': '32%', 'display': 'inline-block'})
        
    ], style={'display': 'flex', 'justifyContent': 'space-between'}),
    
    html.Div([
        html.Hr(),
        html.P("Dashboard showing product analysis across different time periods with universal filters", 
               style={'textAlign': 'center', 'color': 'gray', 'marginTop': 20})
    ])
    
], style={'margin': '20px'})

# Callback for mutual exclusivity between invoice day and week filters
@app.callback(
    [Output('invoice-day-filter', 'disabled'),
     Output('week-filter', 'disabled')],
    [Input('invoice-day-filter', 'value'),
     Input('week-filter', 'value')]
)
def toggle_filter_exclusivity(invoice_days, weeks):
    # Disable week filter if invoice days are selected
    week_disabled = bool(invoice_days)
    # Disable invoice day filter if weeks are selected
    day_disabled = bool(weeks)
    
    return day_disabled, week_disabled

# Callback for updating week options when first day of month changes
@app.callback(
    Output('week-filter', 'options'),
    [Input('first-day-selector', 'value')]
)
def update_week_options(selected_weekday):
    if selected_weekday is not None:
        # Recalculate weeks based on new first day selection
        add_week_calculation(dfs, selected_weekday)
        # Get updated week options
        return get_week_options(dfs)
    return week_options

# Removed summary cards callback - section no longer needed

# Removed comparison table callback - section no longer needed

# Callback for updating top performers table
@app.callback(
    [Output('top-performers-table', 'data'),
     Output('top-performers-table', 'columns')],
    [Input('invoice-day-filter', 'value'),
     Input('week-filter', 'value'),
     Input('brand-filter', 'value'),
     Input('idg-filter', 'value'),
     Input('type-filter', 'value'),
     Input('first-day-selector', 'value')]
)
def update_top_performers_table(invoice_days, weeks, brands, idgs, types, selected_weekday):
    top_performers_data = get_top_performers(dfs, invoice_days, weeks, brands, idgs, types, selected_weekday)
    
    columns = [
        {'name': 'Rank', 'id': 'Rank', 'type': 'numeric'},
        {'name': 'Product', 'id': 'Product', 'type': 'text'},
        {'name': 'Total Revenue', 'id': 'Total Revenue', 'type': 'text'},
        {'name': 'Total Qty', 'id': 'Total Qty', 'type': 'text'},
        {'name': f'{sheet_info[0][2]} Revenue', 'id': f'{sheet_info[0][2]} Revenue', 'type': 'text'},
        {'name': f'{sheet_info[1][2]} Revenue', 'id': f'{sheet_info[1][2]} Revenue', 'type': 'text'},
        {'name': f'{sheet_info[2][2]} Revenue', 'id': f'{sheet_info[2][2]} Revenue', 'type': 'text'},
        {'name': 'YoY Change %', 'id': 'YoY Change %', 'type': 'text'},
        {'name': 'MoM Change %', 'id': 'MoM Change %', 'type': 'text'}
    ]
    
    return top_performers_data, columns

# Callbacks for updating tables based on filters
@app.callback(
    [Output('table-0', 'data'),
     Output('table-1', 'data'),
     Output('table-2', 'data')],
    [Input('invoice-day-filter', 'value'),
     Input('week-filter', 'value'),
     Input('brand-filter', 'value'),
     Input('idg-filter', 'value'),
     Input('type-filter', 'value'),
     Input('first-day-selector', 'value')]
)
def update_tables(invoice_days, weeks, brands, idgs, types, selected_weekday):
    # Ensure week calculation is up to date
    if selected_weekday is not None:
        add_week_calculation(dfs, selected_weekday)
    
    # Enforce mutual exclusivity: if both are selected, prioritize the one that was selected first
    if invoice_days and weeks:
        # Clear weeks if both are selected (prioritize invoice days)
        weeks = None
    
    # Filter and aggregate data for each table (always product view)
    table_data_0 = filter_and_aggregate_data(dfs[0], invoice_days, weeks, brands, idgs, types)
    table_data_1 = filter_and_aggregate_data(dfs[1], invoice_days, weeks, brands, idgs, types)
    table_data_2 = filter_and_aggregate_data(dfs[2], invoice_days, weeks, brands, idgs, types)
    
    return table_data_0, table_data_1, table_data_2

# Run the app
if __name__ == '__main__':
    app.run(debug=True, port=8050)
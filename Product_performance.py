import json
import pandas as pd
import dash
from dash import dcc, html, dash_table, Input, Output, State, callback
import plotly.express as px
from datetime import datetime, date
import os
import glob
import calendar

# Automated Path Configuration Functions
def get_first_day_of_month(month_year):
    """
    Determine the first day of the month given a month-year string (e.g., 'June-2025')
    Returns the weekday number (0 = Monday, 6 = Sunday)
    """
    month_name, year = month_year.split('-')
    month_name = month_name.capitalize()
    year = int(year)
    month_num = list(calendar.month_name).index(month_name)
    
    # Get the weekday of the first day of the month (0 = Monday, 6 = Sunday)
    first_weekday = calendar.weekday(year, month_num, 1)
    
    return first_weekday

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
    latest_month_year = input("Enter the latest month-year (e.g., 'June-2025'): ")  # Default for dashboard - change this as needed
    
    # Automatically determine the first day of the month
    first_day_weekday = get_first_day_of_month(latest_month_year)
    print(f"📅 First day of {latest_month_year} is: {['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][first_day_weekday]}")
    
    # Load configuration from config.json
    try:
        with open('config.json', 'r') as f:
            config_data = json.load(f)
        dsr_path = config_data['paths']['dsr_folder_path']
    except Exception as e:
        print(f"❌ Error loading config.json: {e}")
        print("Using default DSR folder path...")
        dsr_path = "C:\\Users\\91843\\Documents\\VsCode Codes\\ReportAutomation\\test\\DSR"
        
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
    filtered_df['TYPE'] = filtered_df['TYPE'].replace('jumbo.ae', 'Jumbo.ae')
    
    # Group by ProductDesc and sum both Amount Invoiced W.O. VAT and QtyOrdered
    product_totals = filtered_df.groupby('ProductDesc').agg({
        'Amount Invoiced W.O. VAT': 'sum',
        'QtyOrdered': 'sum'
    }).sort_values(by='Amount Invoiced W.O. VAT', ascending=False)
    
    type_results.append((idx, product_totals))  # Store the index instead of sheet name    # Store the processed dataframe
    dfs.append(filtered_df)
# Initialize Dash app with custom CSS
app = dash.Dash(__name__)

# Add custom CSS for dropdown styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Custom styling for dynamic filter options */
            .Select-option:first-child {
                color: #28a745 !important;
                font-weight: bold !important;
            }
            .Select-option[title*="✓"] {
                color: #28a745 !important;
                font-weight: bold !important;
            }
            .Select-option[title*="✗"] {
                color: #dc3545 !important;
                opacity: 0.7 !important;
            }
            /* Loading spinner styling */
            ._dash-loading {
                margin: 10px auto;
            }
            .dash-spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #007bff;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 10px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Add custom CSS for dropdown styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            /* Custom styling for dynamic filter options */
            .Select-option:first-child {
                color: #28a745 !important;
                font-weight: bold !important;
            }
            .Select-option[title*="✓"] {
                color: #28a745 !important;
                font-weight: bold !important;
            }
            .Select-option[title*="✗"] {
                color: #dc3545 !important;
                opacity: 0.7 !important;
            }
            /* Loading spinner styling */
            ._dash-loading {
                margin: 10px auto;
            }
            .dash-spinner {
                border: 4px solid #f3f3f3;
                border-top: 4px solid #007bff;
                border-radius: 50%;
                width: 30px;
                height: 30px;
                animation: spin 1s linear infinite;
                margin: 10px auto;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Get unique values for filters from all dataframes
all_days = []
all_brands = []
all_idgs = []
all_types = []
all_categories = []
all_item_names = []

for df in dfs:
    # Get unique invoice days (1-31)
    days = df['InvoiceDay'].dropna().unique()
    all_days.extend(days)
    all_brands.extend(df['Brand'].dropna().unique())
    all_idgs.extend(df['idg'].dropna().unique())
    all_types.extend(df['TYPE'].dropna().unique())
    
    # Add new filters
    if 'Category Name (L3)' in df.columns:
        all_categories.extend(df['Category Name (L3)'].dropna().unique())
    if 'ItemName' in df.columns:
        all_item_names.extend(df['ItemName'].dropna().unique())

# Remove duplicates and sort
unique_days = sorted(list(set(all_days)))
unique_brands = sorted(list(set(all_brands)))
unique_idgs = sorted(list(set(all_idgs)))
unique_types = sorted(list(set(all_types)))
unique_categories = sorted(list(set(all_categories)))
unique_item_names = sorted(list(set(all_item_names)))

# Create options for dropdowns
day_options = [{'label': f'Day {int(day)}', 'value': day} for day in unique_days if not pd.isna(day)]
brand_options = [{'label': brand, 'value': brand} for brand in unique_brands]
idg_options = [{'label': idg, 'value': idg} for idg in unique_idgs]
type_options = [{'label': type_val, 'value': type_val} for type_val in unique_types]
category_options = [{'label': category, 'value': category} for category in unique_categories]
item_name_options = [{'label': item_name, 'value': item_name} for item_name in unique_item_names]

# Week calculation function
def get_week_date_ranges(first_day_of_month_weekday, month_year):
    """
    Calculate week date ranges for the month
    Returns a dictionary with week numbers and their date ranges
    """
    month_name, year = month_year.split('-')
    month_num = list(calendar.month_name).index(month_name.capitalize())
    year = int(year)
    
    # Get number of days in the month
    days_in_month = calendar.monthrange(year, month_num)[1]
    
    week_ranges = {}
    current_week = 1
    
    # Calculate days in week 1
    if first_day_of_month_weekday == 6:  # If 1st is Sunday
        days_in_week1 = 1
    else:  # If 1st is Monday-Saturday
        days_in_week1 = 7 - first_day_of_month_weekday
    
    # Week 1 range
    week_ranges[1] = (1, min(days_in_week1, days_in_month))
    
    # Calculate remaining weeks
    current_day = days_in_week1 + 1
    current_week = 2
    
    while current_day <= days_in_month:
        week_start = current_day
        week_end = min(current_day + 6, days_in_month)
        week_ranges[current_week] = (week_start, week_end)
        current_day = week_end + 1
        current_week += 1
    
    return week_ranges

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

# Initialize with automatically determined first day
add_week_calculation(dfs, first_day_weekday)

# Get unique weeks for filter (will be updated dynamically)
def get_week_options(dfs, first_day_weekday, month_year):
    all_weeks = []
    for df in dfs:
        if 'Week' in df.columns:
            weeks = df['Week'].dropna().unique()
            all_weeks.extend(weeks)
    
    unique_weeks = sorted(list(set(all_weeks))) if all_weeks else []
    
    # Get week date ranges
    week_ranges = get_week_date_ranges(first_day_weekday, month_year)
    
    # Create options with date ranges
    week_options = []
    for week in unique_weeks:
        if not pd.isna(week) and int(week) in week_ranges:
            start_day, end_day = week_ranges[int(week)]
            if start_day == end_day:
                label = f'Week {int(week)} ({start_day})'
            else:
                label = f'Week {int(week)} ({start_day}-{end_day})'
            week_options.append({'label': label, 'value': week})
    
    return week_options

week_options = get_week_options(dfs, first_day_weekday, latest_month_year)

# Function to filter and aggregate data
def filter_and_aggregate_data(df, invoice_days, weeks, brands, idgs, types, categories=None, item_names=None):
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
    if categories and 'Category Name (L3)' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['Category Name (L3)'].isin(categories)]
    if item_names and 'ItemName' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['ItemName'].isin(item_names)]
    
    # Always group by ProductDesc (product view)
    product_totals = filtered_df.groupby('ProductDesc').agg({
        'Amount Invoiced W.O. VAT': 'sum',
        'QtyOrdered': 'sum'
    }).sort_values(by='Amount Invoiced W.O. VAT', ascending=False)
    
    # Reset index and format
    df_display = product_totals.reset_index()
    df_display['Amount Invoiced W.O. VAT'] = df_display['Amount Invoiced W.O. VAT'].round(2)
    df_display['QtyOrdered'] = df_display['QtyOrdered'].round(0)
    
    # For display in the table, truncate long product descriptions
    df_display['ProductDesc_Display'] = df_display['ProductDesc'].apply(
        lambda x: (x[:50] + '...') if len(x) > 50 else x
    )
    
    return df_display.to_dict('records')

# Function to calculate summary metrics
def calculate_summary_metrics(dfs, invoice_days, weeks, brands, idgs, types, categories=None, item_names=None):
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
        if categories and 'Category Name (L3)' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Category Name (L3)'].isin(categories)]
        if item_names and 'ItemName' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['ItemName'].isin(item_names)]
        
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
            f'Last Month ({sheet_info[0][2]})': f"AED {last_month['total_revenue']:,.0f}",
            f'Last Year ({sheet_info[1][2]})': f"AED {last_year['total_revenue']:,.0f}",
            f'Current ({sheet_info[2][2]})': f"AED {current['total_revenue']:,.0f}",
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
def get_top_performers(dfs, invoice_days, weeks, brands, idgs, types, categories=None, item_names=None, top_n=10):
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
    if categories and 'Category Name (L3)' in latest_df.columns:
        latest_df = latest_df[latest_df['Category Name (L3)'].isin(categories)]
    if item_names and 'ItemName' in latest_df.columns:
        latest_df = latest_df[latest_df['ItemName'].isin(item_names)]
    
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
            if categories and 'Category Name (L3)' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Category Name (L3)'].isin(categories)]
            if item_names and 'ItemName' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['ItemName'].isin(item_names)]
            
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
            # 'Total Revenue': f"AED {total_revenue:,.0f}",
            # 'Total Qty': f"{total_qty:,.0f}",
            f"{sheet_info[0][2]} Revenue": f"AED {product_data[f'{sheet_info[0][2]}_Revenue']:,.0f}",
            f"{sheet_info[1][2]} Revenue": f"AED {product_data[f'{sheet_info[1][2]}_Revenue']:,.0f}",
            f"{sheet_info[2][2]} Revenue": f"AED {product_data[f'{sheet_info[2][2]}_Revenue']:,.0f}",
            'YoY Change %': yoy_display,
            'MoM Change %': mom_display
        })
    
    return formatted_top_products

# Function to get top performing brands across all periods
def get_top_brands(dfs, invoice_days, weeks, brands, idgs, types, categories=None, item_names=None, top_n=10):
    # Get top 10 brands from the latest month (index 2)
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
    if categories and 'Category Name (L3)' in latest_df.columns:
        latest_df = latest_df[latest_df['Category Name (L3)'].isin(categories)]
    if item_names and 'ItemName' in latest_df.columns:
        latest_df = latest_df[latest_df['ItemName'].isin(item_names)]
    
    # Get top brands from latest month
    latest_brand_totals = latest_df.groupby('Brand').agg({
        'Amount Invoiced W.O. VAT': 'sum',
        'QtyOrdered': 'sum'
    }).sort_values(by='Amount Invoiced W.O. VAT', ascending=False)
    
    # Get top N brands from latest month
    top_brands_latest = latest_brand_totals.head(top_n)
    top_brand_names = top_brands_latest.index.tolist()
    
    # Now get data for these brands from all periods
    all_brands_data = {}
    
    for brand_name in top_brand_names:
        all_brands_data[brand_name] = {
            'Brand': brand_name,
            f'{sheet_info[2][2]}_Revenue': top_brands_latest.loc[brand_name, 'Amount Invoiced W.O. VAT'],
            f'{sheet_info[2][2]}_Qty': top_brands_latest.loc[brand_name, 'QtyOrdered']
        }
        
        # Get data from other periods for the same brands
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
            if categories and 'Category Name (L3)' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['Category Name (L3)'].isin(categories)]
            if item_names and 'ItemName' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['ItemName'].isin(item_names)]
            
            period_name = sheet_info[i][2]
            
            # Check if brand exists in this period
            brand_data = filtered_df[filtered_df['Brand'] == brand_name]
            if not brand_data.empty:
                revenue = brand_data['Amount Invoiced W.O. VAT'].sum()
                qty = brand_data['QtyOrdered'].sum()
            else:
                revenue = 0
                qty = 0
            
            all_brands_data[brand_name][f'{period_name}_Revenue'] = revenue
            all_brands_data[brand_name][f'{period_name}_Qty'] = qty
    
    # Format the results
    formatted_top_brands = []
    for i, (brand_name, brand_data) in enumerate(all_brands_data.items()):
        # Calculate total revenue and quantity across all periods
        total_revenue = (brand_data[f'{sheet_info[0][2]}_Revenue'] + 
                        brand_data[f'{sheet_info[1][2]}_Revenue'] + 
                        brand_data[f'{sheet_info[2][2]}_Revenue'])
        total_qty = (brand_data[f'{sheet_info[0][2]}_Qty'] + 
                    brand_data[f'{sheet_info[1][2]}_Qty'] + 
                    brand_data[f'{sheet_info[2][2]}_Qty'])
        
        # Calculate comparisons
        current_revenue = brand_data[f'{sheet_info[2][2]}_Revenue']
        last_year_revenue = brand_data[f'{sheet_info[1][2]}_Revenue']
        last_month_revenue = brand_data[f'{sheet_info[0][2]}_Revenue']
        
        # Year-over-year comparison
        if last_year_revenue > 0:
            yoy_change = ((current_revenue - last_year_revenue) / last_year_revenue) * 100
            yoy_display = f"{yoy_change:+.1f}%"
        else:
            yoy_display = "New Brand"
        
        # Month-over-month comparison
        if last_month_revenue > 0:
            mom_change = ((current_revenue - last_month_revenue) / last_month_revenue) * 100
            mom_display = f"{mom_change:+.1f}%"
        else:
            mom_display = "New Brand"
        
        formatted_top_brands.append({
            'Rank': i + 1,
            'Brand': brand_name,
            f"{sheet_info[0][2]} Revenue": f"AED {brand_data[f'{sheet_info[0][2]}_Revenue']:,.0f}",
            f"{sheet_info[1][2]} Revenue": f"AED {brand_data[f'{sheet_info[1][2]}_Revenue']:,.0f}",
            f"{sheet_info[2][2]} Revenue": f"AED {brand_data[f'{sheet_info[2][2]}_Revenue']:,.0f}",
            'YoY Change %': yoy_display,
            'MoM Change %': mom_display
        })
    
    return formatted_top_brands

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
    html.H1("Product Analysis Dashboard", style={'textAlign': 'center', 'marginBottom': 30, 'fontFamily': 'Arial, sans-serif'}),
    
    # Universal Filters Section - Compact Design
    html.Div([
        html.H4("🔍 Filters", style={'textAlign': 'center', 'marginBottom': 8, 'fontSize': '16px'}),
        
        # Display automatically determined first day of month - compact
        html.Div([
            html.P(f"📅 {latest_month_year}: {['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][first_day_weekday]} start", 
                   style={'textAlign': 'center', 'fontSize': '10px', 'color': '#007bff', 'marginBottom': 5})
        ]),
        
        # Compact Filter Note
        html.Div([
            html.P("📝 Days OR Weeks (not both) | 💡 Select All → Clear All buttons", 
                   style={'textAlign': 'center', 'fontSize': '11px', 'color': '#666', 'marginBottom': 4}),
            html.P("🔄 Smart Filters: ✓ Compatible with other selections | ✗ No data when combined", 
                   style={'textAlign': 'center', 'fontSize': '10px', 'color': '#28a745', 'marginBottom': 8})
        ]),
        
        # Compact Filter Grid - 3 rows of filters
        html.Div([
            # Row 1: Time filters
            html.Div([
                html.Div([
                    html.Label("Days:", style={'fontSize': '11px', 'fontWeight': 'bold', 'marginBottom': 2}),
                    html.Div([
                        dcc.Checklist(
                            id='invoice-day-select-all',
                            options=[{'label': 'All', 'value': 'select_all'}],
                            value=[],
                            style={'display': 'inline-block', 'marginRight': '5px', 'fontSize': '9px'}
                        ),
                        html.Button('✕', id='invoice-day-clear-all', 
                                   style={'fontSize': '8px', 'padding': '1px 4px', 'border': '1px solid #ccc', 
                                         'borderRadius': '2px', 'backgroundColor': '#f8f9fa', 'cursor': 'pointer', 'lineHeight': '1'})
                    ], style={'marginBottom': 2}),
                    dcc.Dropdown(
                        id='invoice-day-filter',
                        options=day_options,
                        multi=True,
                        placeholder="Days",
                        style={'fontSize': '11px', 'minHeight': '28px'}
                    )
                ], style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%', 'minWidth': '120px'}),
                
                html.Div([
                    html.Label("Weeks:", style={'fontSize': '11px', 'fontWeight': 'bold', 'marginBottom': 2}),
                    html.Div([
                        dcc.Checklist(
                            id='week-select-all',
                            options=[{'label': 'All', 'value': 'select_all'}],
                            value=[],
                            style={'display': 'inline-block', 'marginRight': '5px', 'fontSize': '9px'}
                        ),
                        html.Button('✕', id='week-clear-all', 
                                   style={'fontSize': '8px', 'padding': '1px 4px', 'border': '1px solid #ccc', 
                                         'borderRadius': '2px', 'backgroundColor': '#f8f9fa', 'cursor': 'pointer', 'lineHeight': '1'})
                    ], style={'marginBottom': 2}),
                    dcc.Dropdown(
                        id='week-filter',
                        options=week_options,
                        multi=True,
                        placeholder="Weeks",
                        style={'fontSize': '11px', 'minHeight': '28px'}
                    )
                ], style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%', 'minWidth': '120px'}),
                
                html.Div([
                    html.Label("Brand:", style={'fontSize': '11px', 'fontWeight': 'bold', 'marginBottom': 2}),
                    html.Div([
                        dcc.Checklist(
                            id='brand-select-all',
                            options=[{'label': 'All', 'value': 'select_all'}],
                            value=[],
                            style={'display': 'inline-block', 'marginRight': '5px', 'fontSize': '9px'}
                        ),
                        html.Button('✕', id='brand-clear-all', 
                                   style={'fontSize': '8px', 'padding': '1px 4px', 'border': '1px solid #ccc', 
                                         'borderRadius': '2px', 'backgroundColor': '#f8f9fa', 'cursor': 'pointer', 'lineHeight': '1'})
                    ], style={'marginBottom': 2}),
                    dcc.Dropdown(
                        id='brand-filter',
                        options=brand_options,
                        multi=True,
                        placeholder="Brands",
                        style={'fontSize': '11px', 'minHeight': '28px'}
                    )
                ], style={'width': '24%', 'display': 'inline-block', 'marginRight': '1%', 'minWidth': '120px'}),
                
                html.Div([
                    html.Label("IDG:", style={'fontSize': '11px', 'fontWeight': 'bold', 'marginBottom': 2}),
                    html.Div([
                        dcc.Checklist(
                            id='idg-select-all',
                            options=[{'label': 'All', 'value': 'select_all'}],
                            value=[],
                            style={'display': 'inline-block', 'marginRight': '5px', 'fontSize': '9px'}
                        ),
                        html.Button('✕', id='idg-clear-all', 
                                   style={'fontSize': '8px', 'padding': '1px 4px', 'border': '1px solid #ccc', 
                                         'borderRadius': '2px', 'backgroundColor': '#f8f9fa', 'cursor': 'pointer', 'lineHeight': '1'})
                    ], style={'marginBottom': 2}),
                    dcc.Dropdown(
                        id='idg-filter',
                        options=idg_options,
                        multi=True,
                        placeholder="IDG",
                        style={'fontSize': '11px', 'minHeight': '28px'}
                    )
                ], style={'width': '24%', 'display': 'inline-block', 'minWidth': '120px'})
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': 8}),
            
            # Row 2: Product filters
            html.Div([
                html.Div([
                    html.Label("Type:", style={'fontSize': '11px', 'fontWeight': 'bold', 'marginBottom': 2}),
                    html.Div([
                        dcc.Checklist(
                            id='type-select-all',
                            options=[{'label': 'All', 'value': 'select_all'}],
                            value=[],
                            style={'display': 'inline-block', 'marginRight': '5px', 'fontSize': '9px'}
                        ),
                        html.Button('✕', id='type-clear-all', 
                                   style={'fontSize': '8px', 'padding': '1px 4px', 'border': '1px solid #ccc', 
                                         'borderRadius': '2px', 'backgroundColor': '#f8f9fa', 'cursor': 'pointer', 'lineHeight': '1'})
                    ], style={'marginBottom': 2}),
                    dcc.Dropdown(
                        id='type-filter',
                        options=type_options,
                        multi=True,
                        placeholder="Types",
                        style={'fontSize': '11px', 'minHeight': '28px'}
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'minWidth': '150px'}),
                
                html.Div([
                    html.Label("Category (L3):", style={'fontSize': '11px', 'fontWeight': 'bold', 'marginBottom': 2}),
                    html.Div([
                        dcc.Checklist(
                            id='category-select-all',
                            options=[{'label': 'All', 'value': 'select_all'}],
                            value=[],
                            style={'display': 'inline-block', 'marginRight': '5px', 'fontSize': '9px'}
                        ),
                        html.Button('✕', id='category-clear-all', 
                                   style={'fontSize': '8px', 'padding': '1px 4px', 'border': '1px solid #ccc', 
                                         'borderRadius': '2px', 'backgroundColor': '#f8f9fa', 'cursor': 'pointer', 'lineHeight': '1'})
                    ], style={'marginBottom': 2}),
                    dcc.Dropdown(
                        id='category-filter',
                        options=category_options,
                        multi=True,
                        placeholder="Categories",
                        style={'fontSize': '11px', 'minHeight': '28px'}
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%', 'minWidth': '150px'}),
                
                html.Div([
                    html.Label("Item SKU:", style={'fontSize': '11px', 'fontWeight': 'bold', 'marginBottom': 2}),
                    html.Div([
                        dcc.Checklist(
                            id='item-name-select-all',
                            options=[{'label': 'All', 'value': 'select_all'}],
                            value=[],
                            style={'display': 'inline-block', 'marginRight': '5px', 'fontSize': '9px'}
                        ),
                        html.Button('✕', id='item-name-clear-all', 
                                   style={'fontSize': '8px', 'padding': '1px 4px', 'border': '1px solid #ccc', 
                                         'borderRadius': '2px', 'backgroundColor': '#f8f9fa', 'cursor': 'pointer', 'lineHeight': '1'})
                    ], style={'marginBottom': 2}),
                    dcc.Dropdown(
                        id='item-name-filter',
                        options=item_name_options,
                        multi=True,
                        placeholder="Item Names",
                        style={'fontSize': '11px', 'minHeight': '28px'}
                    )
                ], style={'width': '32%', 'display': 'inline-block', 'minWidth': '150px'})
            ], style={'display': 'flex', 'flexWrap': 'wrap', 'marginBottom': 5})
        ])
        
    ], style={'backgroundColor': '#f8f9fa', 'padding': '12px', 'borderRadius': '8px', 'marginBottom': 20}),
      # Top Performers Section
    html.Div([
        html.H3(f"🏆 Top 10 Performers from {sheet_info[2][2]} (with data from all periods)", style={'textAlign': 'center', 'marginBottom': 20}),
        dcc.Loading(
            id="loading-top-performers",
            type="default",
            children=[
                dash_table.DataTable(
                    id='top-performers-table',
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontFamily': 'Arial, sans-serif',
                'fontSize': '12px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0,
            },
            style_cell_conditional=[
                {'if': {'column_id': 'Rank'}, 'width': '5%', 'textAlign': 'center'},
                {'if': {'column_id': 'Product'}, 'width': '40%'},
                {'if': {'column_id': f'{sheet_info[0][2]} Revenue'}, 'width': '12%'},
                {'if': {'column_id': f'{sheet_info[1][2]} Revenue'}, 'width': '12%'},
                {'if': {'column_id': f'{sheet_info[2][2]} Revenue'}, 'width': '12%'},
                {'if': {'column_id': 'YoY Change %'}, 'width': '10%', 'textAlign': 'center'},
                {'if': {'column_id': 'MoM Change %'}, 'width': '10%', 'textAlign': 'center'},
            ],
            tooltip_data=[],  # Will be populated in the callback
            tooltip_duration=None,
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
            ]
        )
    ], style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': 30, 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),
    
    # Top Brands Section
    html.Div([
        html.H3(f"🏅 Top 10 Brands from {sheet_info[2][2]} (with data from all periods)", style={'textAlign': 'center', 'marginBottom': 20}),
        dcc.Loading(
            id="loading-top-brands",
            type="default",
            children=[
                dash_table.DataTable(
                    id='top-brands-table',
            style_cell={
                'textAlign': 'left',
                'padding': '10px',
                'fontFamily': 'Arial, sans-serif',
                'fontSize': '12px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis',
                'maxWidth': 0,
            },
            style_cell_conditional=[
                {'if': {'column_id': 'Rank'}, 'width': '5%', 'textAlign': 'center'},
                {'if': {'column_id': 'Brand'}, 'width': '40%'},
                {'if': {'column_id': f'{sheet_info[0][2]} Revenue'}, 'width': '12%'},
                {'if': {'column_id': f'{sheet_info[1][2]} Revenue'}, 'width': '12%'},
                {'if': {'column_id': f'{sheet_info[2][2]} Revenue'}, 'width': '12%'},
                {'if': {'column_id': 'YoY Change %'}, 'width': '10%', 'textAlign': 'center'},
                {'if': {'column_id': 'MoM Change %'}, 'width': '10%', 'textAlign': 'center'},
            ],
            tooltip_data=[],  # Will be populated in the callback
            tooltip_duration=None,
            style_header={
                'backgroundColor': 'rgb(255, 193, 7)',
                'color': 'black',
                'fontWeight': 'bold',
                'textAlign': 'center'
            },
            style_data_conditional=[
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
            ]
        )
    ], style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'marginBottom': 30, 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}),

      # Tables Section - Responsive Layout
    html.Div([
        html.Div([            html.H4(f"{sheet_info[0][2]} - Product Analysis", style={'textAlign': 'center', 'marginBottom': 15}),
            dcc.Loading(
                id="loading-table-0",
                type="default",
                children=[
                    dash_table.DataTable(
                        id='table-0',
                columns=[
                    {'name': 'Product Description', 'id': 'ProductDesc', 'type': 'text'},
                    {'name': 'Amount (W.O. VAT)', 'id': 'Amount Invoiced W.O. VAT', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                    {'name': 'Qty', 'id': 'QtyOrdered', 'type': 'numeric', 'format': {'specifier': ',.0f'}}
                ],
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '12px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0,
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'ProductDesc'}, 'width': '60%'},
                    {'if': {'column_id': 'Amount Invoiced W.O. VAT'}, 'width': '20%'},
                    {'if': {'column_id': 'QtyOrdered'}, 'width': '20%'},
                ],
                tooltip_data=[],  # Will be populated in the callback
                tooltip_duration=None,
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
                ]
            )
        ], style={'width': '31%', 'display': 'inline-block', 'marginRight': '2%', 'minWidth': '300px'}),
        
        html.Div([            html.H4(f"{sheet_info[1][2]} - Product Analysis", style={'textAlign': 'center', 'marginBottom': 15}),
            dash_table.DataTable(
                id='table-1',
                columns=[
                    {'name': 'Product Description', 'id': 'ProductDesc', 'type': 'text'},
                    {'name': 'Amount (W.O. VAT)', 'id': 'Amount Invoiced W.O. VAT', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                    {'name': 'Qty', 'id': 'QtyOrdered', 'type': 'numeric', 'format': {'specifier': ',.0f'}}
                ],
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '12px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0,
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'ProductDesc'}, 'width': '60%'},
                    {'if': {'column_id': 'Amount Invoiced W.O. VAT'}, 'width': '20%'},
                    {'if': {'column_id': 'QtyOrdered'}, 'width': '20%'},
                ],
                tooltip_data=[],  # Will be populated in the callback
                tooltip_duration=None,
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
        ], style={'width': '31%', 'display': 'inline-block', 'marginRight': '2%', 'minWidth': '300px'}),
        
        html.Div([            html.H4(f"{sheet_info[2][2]} - Product Analysis", style={'textAlign': 'center', 'marginBottom': 15}),
            dash_table.DataTable(
                id='table-2',
                columns=[
                    {'name': 'Product Description', 'id': 'ProductDesc', 'type': 'text'},
                    {'name': 'Amount (W.O. VAT)', 'id': 'Amount Invoiced W.O. VAT', 'type': 'numeric', 'format': {'specifier': ',.0f'}},
                    {'name': 'Qty', 'id': 'QtyOrdered', 'type': 'numeric', 'format': {'specifier': ',.0f'}}
                ],
                style_cell={
                    'textAlign': 'left',
                    'padding': '8px',
                    'fontFamily': 'Arial, sans-serif',
                    'fontSize': '12px',
                    'overflow': 'hidden',
                    'textOverflow': 'ellipsis',
                    'maxWidth': 0,
                },
                style_cell_conditional=[
                    {'if': {'column_id': 'ProductDesc'}, 'width': '60%'},
                    {'if': {'column_id': 'Amount Invoiced W.O. VAT'}, 'width': '20%'},
                    {'if': {'column_id': 'QtyOrdered'}, 'width': '20%'},
                ],
                tooltip_data=[],  # Will be populated in the callback
                tooltip_duration=None,
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
        ], style={'width': '31%', 'display': 'inline-block', 'minWidth': '300px'})
    ], style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-between', 'marginBottom': '20px'}),
    
    html.Div([
        html.Hr(),
        html.P("Dashboard showing product analysis across different time periods with universal filters", 
               style={'textAlign': 'center', 'color': 'gray', 'marginTop': 20})
    ])
    
], style={'margin': '20px', 'fontFamily': 'Arial, sans-serif', 'maxWidth': '2000px', 'marginLeft': 'auto', 'marginRight': 'auto'})

# Callback for mutual exclusivity between invoice day and week filters
@app.callback(
    [Output('invoice-day-filter', 'disabled'),
     Output('week-filter', 'disabled'),
     Output('invoice-day-select-all', 'style'),
     Output('week-select-all', 'style'),
     Output('invoice-day-clear-all', 'disabled'),
     Output('week-clear-all', 'disabled')],
    [Input('invoice-day-filter', 'value'),
     Input('week-filter', 'value')]
)
def toggle_filter_exclusivity(invoice_days, weeks):
    # Disable week filter if invoice days are selected
    week_disabled = bool(invoice_days)
    # Disable invoice day filter if weeks are selected
    day_disabled = bool(weeks)
    
    # Style for disabled select all checkboxes - compact version
    disabled_style = {'display': 'inline-block', 'marginRight': '5px', 'fontSize': '9px', 'opacity': 0.5, 'pointerEvents': 'none'}
    enabled_style = {'display': 'inline-block', 'marginRight': '5px', 'fontSize': '9px'}
    
    day_select_all_style = disabled_style if day_disabled else enabled_style
    week_select_all_style = disabled_style if week_disabled else enabled_style
    
    return day_disabled, week_disabled, day_select_all_style, week_select_all_style, day_disabled, week_disabled

# Callbacks for "Select All" functionality
@app.callback(
    Output('invoice-day-filter', 'value'),
    [Input('invoice-day-select-all', 'value')],
    [State('invoice-day-filter', 'value')]
)
def select_all_invoice_days(select_all, current_values):
    if select_all and 'select_all' in select_all:
        # Select all days
        return [option['value'] for option in day_options]
    elif not select_all and current_values:
        # If "Select All" is unchecked and there are current values, keep them
        return current_values
    else:
        # Clear all selections
        return []

@app.callback(
    Output('week-filter', 'value'),
    [Input('week-select-all', 'value')],
    [State('week-filter', 'value')]
)
def select_all_weeks(select_all, current_values):
    if select_all and 'select_all' in select_all:
        # Select all weeks
        return [option['value'] for option in week_options]
    elif not select_all and current_values:
        # If "Select All" is unchecked and there are current values, keep them
        return current_values
    else:
        # Clear all selections
        return []

@app.callback(
    Output('brand-filter', 'value'),
    [Input('brand-select-all', 'value')],
    [State('brand-filter', 'value')]
)
def select_all_brands(select_all, current_values):
    if select_all and 'select_all' in select_all:
        # Select all brands
        return [option['value'] for option in brand_options]
    elif not select_all and current_values:
        # If "Select All" is unchecked and there are current values, keep them
        return current_values
    else:
        # Clear all selections
        return []

@app.callback(
    Output('idg-filter', 'value'),
    [Input('idg-select-all', 'value')],
    [State('idg-filter', 'value')]
)
def select_all_idgs(select_all, current_values):
    if select_all and 'select_all' in select_all:
        # Select all IDGs
        return [option['value'] for option in idg_options]
    elif not select_all and current_values:
        # If "Select All" is unchecked and there are current values, keep them
        return current_values
    else:
        # Clear all selections
        return []

@app.callback(
    Output('type-filter', 'value'),
    [Input('type-select-all', 'value')],
    [State('type-filter', 'value')]
)
def select_all_types(select_all, current_values):
    if select_all and 'select_all' in select_all:
        # Select all types
        return [option['value'] for option in type_options]
    elif not select_all and current_values:
        # If "Select All" is unchecked and there are current values, keep them
        return current_values
    else:
        # Clear all selections
        return []

@app.callback(
    Output('category-filter', 'value'),
    [Input('category-select-all', 'value')],
    [State('category-filter', 'value')]
)
def select_all_categories(select_all, current_values):
    if select_all and 'select_all' in select_all:
        # Select all categories
        return [option['value'] for option in category_options]
    elif not select_all and current_values:
        # If "Select All" is unchecked and there are current values, keep them
        return current_values
    else:
        # Clear all selections
        return []

@app.callback(
    Output('item-name-filter', 'value'),
    [Input('item-name-select-all', 'value')],
    [State('item-name-filter', 'value')]
)
def select_all_item_names(select_all, current_values):
    if select_all and 'select_all' in select_all:
        # Select all item names
        return [option['value'] for option in item_name_options]
    elif not select_all and current_values:
        # If "Select All" is unchecked and there are current values, keep them
        return current_values
    else:
        # Clear all selections
        return []

# Callbacks for "Clear All" functionality
@app.callback(
    Output('invoice-day-filter', 'value', allow_duplicate=True),
    [Input('invoice-day-clear-all', 'n_clicks')],
    prevent_initial_call=True
)
def clear_all_invoice_days(n_clicks):
    if n_clicks:
        return []
    return []  # Return empty list instead of no_update

@app.callback(
    Output('week-filter', 'value', allow_duplicate=True),
    [Input('week-clear-all', 'n_clicks')],
    prevent_initial_call=True
)
def clear_all_weeks(n_clicks):
    if n_clicks:
        return []
    return []

@app.callback(
    Output('brand-filter', 'value', allow_duplicate=True),
    [Input('brand-clear-all', 'n_clicks')],
    prevent_initial_call=True
)
def clear_all_brands(n_clicks):
    if n_clicks:
        return []
    return []

@app.callback(
    Output('idg-filter', 'value', allow_duplicate=True),
    [Input('idg-clear-all', 'n_clicks')],
    prevent_initial_call=True
)
def clear_all_idgs(n_clicks):
    if n_clicks:
        return []
    return []

@app.callback(
    Output('type-filter', 'value', allow_duplicate=True),
    [Input('type-clear-all', 'n_clicks')],
    prevent_initial_call=True
)
def clear_all_types(n_clicks):
    if n_clicks:
        return []
    return []

@app.callback(
    Output('category-filter', 'value', allow_duplicate=True),
    [Input('category-clear-all', 'n_clicks')],
    prevent_initial_call=True
)
def clear_all_categories(n_clicks):
    if n_clicks:
        return []
    return []

@app.callback(
    Output('item-name-filter', 'value', allow_duplicate=True),
    [Input('item-name-clear-all', 'n_clicks')],
    prevent_initial_call=True
)
def clear_all_item_names(n_clicks):
    if n_clicks:
        return []
    return []

# Auto-uncheck "Select All" when user manually deselects items
@app.callback(
    Output('invoice-day-select-all', 'value'),
    [Input('invoice-day-filter', 'value')]
)
def uncheck_invoice_day_select_all(selected_values):
    if not selected_values or len(selected_values) < len(day_options):
        return []  # Uncheck "Select All"
    return ['select_all']  # Keep "Select All" checked

@app.callback(
    Output('week-select-all', 'value'),
    [Input('week-filter', 'value')]
)
def uncheck_week_select_all(selected_values):
    if not selected_values or len(selected_values) < len(week_options):
        return []  # Uncheck "Select All"
    return ['select_all']  # Keep "Select All" checked

@app.callback(
    Output('brand-select-all', 'value'),
    [Input('brand-filter', 'value')]
)
def uncheck_brand_select_all(selected_values):
    if not selected_values or len(selected_values) < len(brand_options):
        return []  # Uncheck "Select All"
    return ['select_all']  # Keep "Select All" checked

@app.callback(
    Output('idg-select-all', 'value'),
    [Input('idg-filter', 'value')]
)
def uncheck_idg_select_all(selected_values):
    if not selected_values or len(selected_values) < len(idg_options):
        return []  # Uncheck "Select All"
    return ['select_all']  # Keep "Select All" checked

@app.callback(
    Output('type-select-all', 'value'),
    [Input('type-filter', 'value')]
)
def uncheck_type_select_all(selected_values):
    if not selected_values or len(selected_values) < len(type_options):
        return []  # Uncheck "Select All"
    return ['select_all']  # Keep "Select All" checked

@app.callback(
    Output('category-select-all', 'value'),
    [Input('category-filter', 'value')]
)
def uncheck_category_select_all(selected_values):
    if not selected_values or len(selected_values) < len(category_options):
        return []  # Uncheck "Select All"
    return ['select_all']  # Keep "Select All" checked

@app.callback(
    Output('item-name-select-all', 'value'),
    [Input('item-name-filter', 'value')]
)
def uncheck_item_name_select_all(selected_values):
    if not selected_values or len(selected_values) < len(item_name_options):
        return []  # Uncheck "Select All"
    return ['select_all']  # Keep "Select All" checked

# Removed callback for updating week options - now automatically determined

# Removed summary cards callback - section no longer needed

# Removed comparison table callback - section no longer needed

# Callback for updating top performers table
@app.callback(
    [Output('top-performers-table', 'data'),
     Output('top-performers-table', 'columns'),
     Output('top-performers-table', 'tooltip_data')],
    [Input('invoice-day-filter', 'value'),
     Input('week-filter', 'value'),
     Input('brand-filter', 'value'),
     Input('idg-filter', 'value'),
     Input('type-filter', 'value'),
     Input('category-filter', 'value'),
     Input('item-name-filter', 'value')]
)
def update_top_performers_table(invoice_days, weeks, brands, idgs, types, categories, item_names):
    top_performers_data = get_top_performers(dfs, invoice_days, weeks, brands, idgs, types, categories, item_names)
    
    columns = [
        {'name': 'Rank', 'id': 'Rank', 'type': 'numeric'},
        {'name': 'Product', 'id': 'Product', 'type': 'text'},
        # {'name': 'Total Revenue', 'id': 'Total Revenue', 'type': 'text'},
        # {'name': 'Total Qty', 'id': 'Total Qty', 'type': 'text'},
        {'name': f'{sheet_info[0][2]} Revenue', 'id': f'{sheet_info[0][2]} Revenue', 'type': 'text'},
        {'name': f'{sheet_info[1][2]} Revenue', 'id': f'{sheet_info[1][2]} Revenue', 'type': 'text'},
        {'name': f'{sheet_info[2][2]} Revenue', 'id': f'{sheet_info[2][2]} Revenue', 'type': 'text'},
        {'name': 'YoY Change %', 'id': 'YoY Change %', 'type': 'text'},
        {'name': 'MoM Change %', 'id': 'MoM Change %', 'type': 'text'}
    ]
    
    # Create tooltips for product names (to show full name on hover)
    tooltip_data = []
    for row in top_performers_data:
        tooltip_row = {'Product': {'value': row['Product'], 'type': 'markdown'}}
        tooltip_data.append(tooltip_row)
    
    return top_performers_data, columns, tooltip_data

# Callback for updating top brands table
@app.callback(
    [Output('top-brands-table', 'data'),
     Output('top-brands-table', 'columns'),
     Output('top-brands-table', 'tooltip_data')],
    [Input('invoice-day-filter', 'value'),
     Input('week-filter', 'value'),
     Input('brand-filter', 'value'),
     Input('idg-filter', 'value'),
     Input('type-filter', 'value'),
     Input('category-filter', 'value'),
     Input('item-name-filter', 'value')]
)
def update_top_brands_table(invoice_days, weeks, brands, idgs, types, categories, item_names):
    top_brands_data = get_top_brands(dfs, invoice_days, weeks, brands, idgs, types, categories, item_names)
    
    columns = [
        {'name': 'Rank', 'id': 'Rank', 'type': 'numeric'},
        {'name': 'Brand', 'id': 'Brand', 'type': 'text'},
        {'name': f'{sheet_info[0][2]} Revenue', 'id': f'{sheet_info[0][2]} Revenue', 'type': 'text'},
        {'name': f'{sheet_info[1][2]} Revenue', 'id': f'{sheet_info[1][2]} Revenue', 'type': 'text'},
        {'name': f'{sheet_info[2][2]} Revenue', 'id': f'{sheet_info[2][2]} Revenue', 'type': 'text'},
        {'name': 'YoY Change %', 'id': 'YoY Change %', 'type': 'text'},
        {'name': 'MoM Change %', 'id': 'MoM Change %', 'type': 'text'}
    ]
    
    # Create tooltips for brand names (to show full name on hover)
    tooltip_data = []
    for row in top_brands_data:
        tooltip_row = {'Brand': {'value': row['Brand'], 'type': 'markdown'}}
        tooltip_data.append(tooltip_row)
    
    return top_brands_data, columns, tooltip_data

# Callbacks for updating tables based on filters
@app.callback(
    [Output('table-0', 'data'),
     Output('table-1', 'data'),
     Output('table-2', 'data'),
     Output('table-0', 'tooltip_data'),
     Output('table-1', 'tooltip_data'),
     Output('table-2', 'tooltip_data')],
    [Input('invoice-day-filter', 'value'),
     Input('week-filter', 'value'),
     Input('brand-filter', 'value'),
     Input('idg-filter', 'value'),
     Input('type-filter', 'value'),
     Input('category-filter', 'value'),
     Input('item-name-filter', 'value')]
)
def update_tables(invoice_days, weeks, brands, idgs, types, categories, item_names):
    # Enforce mutual exclusivity: if both are selected, prioritize the one that was selected first
    if invoice_days and weeks:
        # Clear weeks if both are selected (prioritize invoice days)
        weeks = None
    
    # Filter and aggregate data for each table (always product view)
    table_data_0 = filter_and_aggregate_data(dfs[0], invoice_days, weeks, brands, idgs, types, categories, item_names)
    table_data_1 = filter_and_aggregate_data(dfs[1], invoice_days, weeks, brands, idgs, types, categories, item_names)
    table_data_2 = filter_and_aggregate_data(dfs[2], invoice_days, weeks, brands, idgs, types, categories, item_names)
    
    # Create tooltips for product descriptions (to show full description on hover)
    tooltip_data_0 = [{
        'ProductDesc': {'value': row['ProductDesc'], 'type': 'markdown'}
    } for row in table_data_0]
    
    tooltip_data_1 = [{
        'ProductDesc': {'value': row['ProductDesc'], 'type': 'markdown'}
    } for row in table_data_1]
    
    tooltip_data_2 = [{
        'ProductDesc': {'value': row['ProductDesc'], 'type': 'markdown'}
    } for row in table_data_2]
    
    return table_data_0, table_data_1, table_data_2, tooltip_data_0, tooltip_data_1, tooltip_data_2

# Function to get dynamic filter options based on current selections
def get_dynamic_filter_options(dfs, invoice_days=None, weeks=None, brands=None, idgs=None, types=None, categories=None, item_names=None):
    """
    Get available filter options based on current selections.
    Returns options with available ones highlighted and shown first.
    For each filter type, we exclude that filter type from the filtering logic to allow multiple selections.
    """
    # Combine all dataframes for filtering
    combined_df = pd.concat(dfs, ignore_index=True)
    
    # Helper function to get available values for a specific filter type
    def get_available_values_for_filter(filter_type):
        filtered_df = combined_df.copy()
        
        # Apply all filters EXCEPT the current filter type being updated
        if filter_type != 'invoice_days' and invoice_days:
            filtered_df = filtered_df[filtered_df['InvoiceDay'].isin(invoice_days)]
        if filter_type != 'weeks' and weeks and 'Week' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Week'].isin(weeks)]
        if filter_type != 'brands' and brands:
            filtered_df = filtered_df[filtered_df['Brand'].isin(brands)]
        if filter_type != 'idgs' and idgs:
            filtered_df = filtered_df[filtered_df['idg'].isin(idgs)]
        if filter_type != 'types' and types:
            filtered_df = filtered_df[filtered_df['TYPE'].isin(types)]
        if filter_type != 'categories' and categories and 'Category Name (L3)' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Category Name (L3)'].isin(categories)]
        if filter_type != 'item_names' and item_names and 'ItemName' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['ItemName'].isin(item_names)]
        
        return filtered_df
    
    # Get available values for each filter type
    days_df = get_available_values_for_filter('invoice_days')
    weeks_df = get_available_values_for_filter('weeks')
    brands_df = get_available_values_for_filter('brands')
    idgs_df = get_available_values_for_filter('idgs')
    types_df = get_available_values_for_filter('types')
    categories_df = get_available_values_for_filter('categories')
    item_names_df = get_available_values_for_filter('item_names')
    
    # Get available unique values for each filter
    available_days = sorted(list(set(days_df['InvoiceDay'].dropna().unique())))
    available_brands = sorted(list(set(brands_df['Brand'].dropna().unique())))
    available_idgs = sorted(list(set(idgs_df['idg'].dropna().unique())))
    available_types = sorted(list(set(types_df['TYPE'].dropna().unique())))
    available_categories = sorted(list(set(categories_df['Category Name (L3)'].dropna().unique()))) if 'Category Name (L3)' in categories_df.columns else []
    available_item_names = sorted(list(set(item_names_df['ItemName'].dropna().unique()))) if 'ItemName' in item_names_df.columns else []
    
    # Get available weeks
    available_weeks = []
    if 'Week' in weeks_df.columns:
        available_weeks = sorted(list(set(weeks_df['Week'].dropna().unique())))
    
    # Create options with styling for available vs unavailable
    def create_styled_options(all_values, available_values, format_func=None):
        options = []
        
        # First, add available options (highlighted with checkmark)
        for value in available_values:
            if not pd.isna(value):
                label = format_func(value) if format_func else str(value)
                options.append({
                    'label': f"✓ {label}",  # Green checkmark for available
                    'value': value
                })
        
        # Then add unavailable options (with X mark)
        unavailable_values = set(all_values) - set(available_values)
        for value in sorted(unavailable_values):
            if not pd.isna(value):
                label = format_func(value) if format_func else str(value)
                options.append({
                    'label': f"✗ {label}",  # Red X for unavailable
                    'value': value
                })
        
        return options
    
    # Create day options with formatting
    def format_day(day):
        return f'Day {int(day)}'
    
    # Create week options with formatting
    def format_week(week):
        if not pd.isna(week) and int(week) in get_week_date_ranges(first_day_weekday, latest_month_year):
            start_day, end_day = get_week_date_ranges(first_day_weekday, latest_month_year)[int(week)]
            if start_day == end_day:
                return f'Week {int(week)} ({start_day})'
            else:
                return f'Week {int(week)} ({start_day}-{end_day})'
        return f'Week {int(week)}'
    
    # Get all possible values from original data
    all_days = sorted(list(set(combined_df['InvoiceDay'].dropna().unique())))
    all_brands = sorted(list(set(combined_df['Brand'].dropna().unique())))
    all_idgs = sorted(list(set(combined_df['idg'].dropna().unique())))
    all_types = sorted(list(set(combined_df['TYPE'].dropna().unique())))
    all_categories = sorted(list(set(combined_df['Category Name (L3)'].dropna().unique()))) if 'Category Name (L3)' in combined_df.columns else []
    all_item_names = sorted(list(set(combined_df['ItemName'].dropna().unique()))) if 'ItemName' in combined_df.columns else []
    all_weeks = sorted(list(set(combined_df['Week'].dropna().unique()))) if 'Week' in combined_df.columns else []
    
    return {
        'day_options': create_styled_options(all_days, available_days, format_day),
        'week_options': create_styled_options(all_weeks, available_weeks, format_week),
        'brand_options': create_styled_options(all_brands, available_brands),
        'idg_options': create_styled_options(all_idgs, available_idgs),
        'type_options': create_styled_options(all_types, available_types),
        'category_options': create_styled_options(all_categories, available_categories),
        'item_name_options': create_styled_options(all_item_names, available_item_names)
    }

# Callback to update all filter options dynamically based on current selections
@app.callback(
    [Output('invoice-day-filter', 'options'),
     Output('week-filter', 'options'),
     Output('brand-filter', 'options'),
     Output('idg-filter', 'options'),
     Output('type-filter', 'options'),
     Output('category-filter', 'options'),
     Output('item-name-filter', 'options')],
    [Input('invoice-day-filter', 'value'),
     Input('week-filter', 'value'),
     Input('brand-filter', 'value'),
     Input('idg-filter', 'value'),
     Input('type-filter', 'value'),
     Input('category-filter', 'value'),
     Input('item-name-filter', 'value')]
)
def update_filter_options(invoice_days, weeks, brands, idgs, types, categories, item_names):
    """
    Update all filter options dynamically based on current selections.
    Available options are shown first with green checkmarks, unavailable options are grayed out.
    """
    try:
        # Get dynamic options based on current selections
        dynamic_options = get_dynamic_filter_options(
            dfs, invoice_days, weeks, brands, idgs, types, categories, item_names
        )
        
        return (
            dynamic_options['day_options'],
            dynamic_options['week_options'],
            dynamic_options['brand_options'],
            dynamic_options['idg_options'],
            dynamic_options['type_options'],
            dynamic_options['category_options'],
            dynamic_options['item_name_options']
        )
    except Exception as e:
        # Fallback to original static options if there's an error
        print(f"Error in dynamic filtering: {e}")
        return (
            day_options,
            week_options,
            brand_options,
            idg_options,
            type_options,
            category_options,
            item_name_options
        )
# Run the app
if __name__ == '__main__':
    app.run(debug=False, port=8050)
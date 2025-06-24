import os
import pandas as pd
import dash
from dash import dcc, html, dash_table, callback
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Load the data from the cache
cache_folder = os.path.join(os.path.dirname(__file__), 'cache')
cache_file = os.path.join(cache_folder, 'combined_data.pkl')

# Load cached data
if os.path.exists(cache_file):
    df = pd.read_pickle(cache_file)
    print("Data loaded successfully!")
    print(f"Data shape: {df.shape}")
    print(f"Columns: {df.columns.tolist()}")
else:
    print("No cache file found. Please run mainDashboard.py first.")
    df = pd.DataFrame()

# Initialize Dash app
app = dash.Dash(__name__)

# Define metrics for comparison
metrics = ['Items viewed', 'Items added to cart', 'Items purchased', 'Item revenue', 'Sessions']

# Custom CSS styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
            }
            .dashboard-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .filter-section {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .comparison-section {
                background: white;
                padding: 20px;
                border-radius: 10px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            .positive-change {
                color: #28a745;
                font-weight: bold;
            }
            .negative-change {
                color: #dc3545;
                font-weight: bold;
            }            .neutral-change {
                color: #6c757d;
                font-weight: bold;
            }
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table {
                border-collapse: separate !important;
                border-spacing: 0 !important;
            }
            .dash-table-container .dash-header {
                border: 1px solid #ddd !important;
            }            .dash-table-container .dash-header.dash-header--merged {
                background-color: #e9ecef !important;
                font-weight: bold !important;
                border-bottom: 2px solid #667eea !important;
            }            .Select-multi-value-wrapper {
                max-height: 60px !important;
                overflow-y: auto !important;
            }
            .Select-value {
                background-color: #667eea !important;
                color: white !important;
                border-color: #667eea !important;
            }
            .Select-value-icon {
                border-right-color: #5a6fd8 !important;
            }
            .Select-value-icon:hover {
                background-color: #5a6fd8 !important;
                color: white !important;
            }
            /* Modern dropdown styling */
            .Select-control {
                border: 1px solid #ddd !important;
                border-radius: 4px !important;
            }
            .Select-control:hover {
                border-color: #667eea !important;
            }
            .Select--is-focused .Select-control {
                border-color: #667eea !important;
                box-shadow: 0 0 0 1px #667eea !important;
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

def get_available_months():
    """Get list of available months from the data"""
    if not df.empty and 'Month' in df.columns and 'Year' in df.columns:
        # Create month-year combinations
        df['Month_Year'] = df['Month'].astype(str) + ' ' + df['Year'].astype(str)
        return sorted(df['Month_Year'].unique())
    return []

def get_available_brands():
    """Get list of available brands"""
    if not df.empty and 'Brand' in df.columns:
        try:
            # Convert to string and handle mixed types
            brands = df['Brand'].dropna().astype(str).unique().tolist()
            # Filter out empty strings and sort
            brands = [brand for brand in brands if brand.strip() != '' and brand != 'nan']
            return ['All'] + sorted(brands)
        except Exception as e:
            print(f"Error getting brands: {e}")
            return ['All']
    return ['All']

def get_available_categories():
    """Get list of available categories"""
    if not df.empty and 'Category' in df.columns:
        try:
            # Convert to string and handle mixed types
            categories = df['Category'].dropna().astype(str).unique().tolist()
            # Filter out empty strings and sort
            categories = [cat for cat in categories if cat.strip() != '' and cat != 'nan']
            return ['All'] + sorted(categories)
        except Exception as e:
            print(f"Error getting categories: {e}")
            return ['All']
    return ['All']

def get_available_days():
    """Get list of available days"""
    if not df.empty and 'Day' in df.columns:
        try:
            # Convert to numeric, then to int, then to string
            days = df['Day'].dropna().astype(float).astype(int).unique().tolist()
            days = sorted([day for day in days if 1 <= day <= 31])  # Valid day range
            return ['All'] + [str(day) for day in days]
        except Exception as e:
            print(f"Error getting days: {e}")
            return ['All']
    return ['All']

def filter_data(month1, month2, brand_filter, category_filter, day_filter):
    """Filter data based on selected criteria"""
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    try:
        # Create month-year column for filtering
        df_filtered = df.copy()
        df_filtered['Month_Year'] = df_filtered['Month'].astype(str) + ' ' + df_filtered['Year'].astype(str)
        
        # Filter by months
        df_month1 = df_filtered[df_filtered['Month_Year'] == month1].copy()
        df_month2 = df_filtered[df_filtered['Month_Year'] == month2].copy()
        
        # Handle multi-select filters
        # Brand filter
        if brand_filter and 'All' not in brand_filter:
            # Convert Brand column to string for comparison
            df_month1 = df_month1[df_month1['Brand'].astype(str).isin(brand_filter)]
            df_month2 = df_month2[df_month2['Brand'].astype(str).isin(brand_filter)]
            
        # Category filter
        if category_filter and 'All' not in category_filter:
            # Convert Category column to string for comparison
            df_month1 = df_month1[df_month1['Category'].astype(str).isin(category_filter)]
            df_month2 = df_month2[df_month2['Category'].astype(str).isin(category_filter)]
            
        # Day filter
        if day_filter and 'All' not in day_filter:
            # Convert Day column to numeric for comparison
            try:
                day_values = [int(day) for day in day_filter if day != 'All']
                if day_values:  # Only filter if there are valid day values
                    df_month1 = df_month1[df_month1['Day'].astype(float).astype(int).isin(day_values)]
                    df_month2 = df_month2[df_month2['Day'].astype(float).astype(int).isin(day_values)]
            except ValueError as ve:
                print(f"Invalid day filter values: {day_filter}, error: {ve}")
        
        return df_month1, df_month2
        
    except Exception as e:
        print(f"Error filtering data: {e}")
        return pd.DataFrame(), pd.DataFrame()

def calculate_percentage_change(val1, val2):
    """Calculate percentage change between two values"""
    if pd.isna(val1) or pd.isna(val2) or val1 == 0:
        return 0
    return ((val2 - val1) / val1) * 100

def format_percentage(value):
    """Format percentage with color coding"""
    if value > 0:
        return f"+{value:.1f}%"
    elif value < 0:
        return f"{value:.1f}%"
    else:
        return "0.0%"

def get_color_style(value):
    """Get color style based on percentage change"""
    if value > 0:
        return {'color': '#28a745', 'fontWeight': 'bold'}  # Green for positive
    elif value < 0:
        return {'color': '#dc3545', 'fontWeight': 'bold'}  # Red for negative
    else:
        return {'color': '#6c757d', 'fontWeight': 'bold'}  # Gray for neutral

# App layout
app.layout = html.Div([
    html.Div([
        html.H1("📊 Monthly Comparison Dashboard", 
                style={'margin': '0', 'fontSize': '2.5rem'}),
        html.P("Compare performance metrics between two months with detailed analytics",
               style={'margin': '10px 0 0 0', 'fontSize': '1.1rem', 'opacity': '0.9'})
    ], className='dashboard-header'),
    
    html.Div([
        html.H3("🔧 Filters & Comparison Settings", style={'marginBottom': '20px', 'color': '#333'}),
        
        html.Div([
            html.Div([
                html.Label("Select First Month:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Dropdown(
                    id='month1-dropdown',
                    options=[{'label': month, 'value': month} for month in get_available_months()],
                    value=get_available_months()[0] if get_available_months() else None,
                    style={'marginBottom': '15px'}
                )
            ], style={'width': '48%', 'display': 'inline-block', 'marginRight': '4%'}),
            
            html.Div([
                html.Label("Select Second Month:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Dropdown(
                    id='month2-dropdown',
                    options=[{'label': month, 'value': month} for month in get_available_months()],
                    value=get_available_months()[1] if len(get_available_months()) > 1 else None,
                    style={'marginBottom': '15px'}
                )
            ], style={'width': '48%', 'display': 'inline-block'})
        ]),
        
        html.Div([            html.Div([
                html.Label("Brand Filter:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Dropdown(
                    id='brand-filter',
                    options=[{'label': brand, 'value': brand} for brand in get_available_brands()],
                    value=['All'],
                    multi=True,
                    placeholder="Select brands...",
                    style={'marginBottom': '15px'}
                )
            ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),
            
            html.Div([
                html.Label("Category Filter:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Dropdown(
                    id='category-filter',
                    options=[{'label': cat, 'value': cat} for cat in get_available_categories()],
                    value=['All'],
                    multi=True,
                    placeholder="Select categories...",
                    style={'marginBottom': '15px'}
                )
            ], style={'width': '32%', 'display': 'inline-block', 'marginRight': '2%'}),
            
            html.Div([
                html.Label("Day Filter:", style={'fontWeight': 'bold', 'marginBottom': '5px', 'display': 'block'}),
                dcc.Dropdown(
                    id='day-filter',
                    options=[{'label': day, 'value': day} for day in get_available_days()],
                    value=['All'],
                    multi=True,
                    placeholder="Select days...",
                    style={'marginBottom': '15px'}
                )
            ], style={'width': '32%', 'display': 'inline-block'})
        ]),
  
    ], className='filter-section'),
      html.Div([
        html.H3("📊 Category Comparison", 
                style={'marginBottom': '20px', 'color': '#333'}),
        html.Div([
            html.P("📋 Select two different months and adjust filters to see comparison data.", 
                   style={'textAlign': 'center', 'color': '#666', 'fontSize': '16px', 'padding': '20px'})
        ], id='category-comparison-table')
    ], className='comparison-section'),
    
    html.Div([
        html.H3("🛍️ Item Name Comparison", 
                style={'marginBottom': '20px', 'color': '#333'}),
        html.Div([
            html.P("📋 Select two different months and adjust filters to see comparison data.", 
                   style={'textAlign': 'center', 'color': '#666', 'fontSize': '16px', 'padding': '20px'})
        ], id='item-comparison-table')
    ], className='comparison-section')
])

@app.callback(
    [Output('category-comparison-table', 'children'),
     Output('item-comparison-table', 'children')],
    [Input('month1-dropdown', 'value'),
     Input('month2-dropdown', 'value'),
     Input('brand-filter', 'value'),
     Input('category-filter', 'value'),
     Input('day-filter', 'value')],
    prevent_initial_call=True
)
def update_comparison_tables(month1, month2, brand_filter, category_filter, day_filter):
    if not month1 or not month2 or df.empty:
        return html.Div("Please select both months to compare."), html.Div("Please select both months to compare.")
    
    # Handle None values for filters (convert to empty list)
    brand_filter = brand_filter or ['All']
    category_filter = category_filter or ['All']
    day_filter = day_filter or ['All']
    
    # Handle "All" selection logic without triggering infinite loops
    # If "All" is selected along with other options, treat as "All" only
    if 'All' in brand_filter:
        brand_filter = ['All']
    if 'All' in category_filter:
        category_filter = ['All']
    if 'All' in day_filter:
        day_filter = ['All']
    
    # Filter data
    df_month1, df_month2 = filter_data(month1, month2, brand_filter, category_filter, day_filter)
    
    if df_month1.empty or df_month2.empty:
        return html.Div("No data available for the selected criteria."), html.Div("No data available for the selected criteria.")
    
    # Category Comparison
    category_comparison = create_category_comparison(df_month1, df_month2, month1, month2)
    
    # Item Comparison
    item_comparison = create_item_comparison(df_month1, df_month2, month1, month2)
    
    return category_comparison, item_comparison

def create_category_comparison(df_month1, df_month2, month1, month2):
    """Create category comparison table"""
    try:
        # Ensure Category column is string type and clean data
        df_month1 = df_month1.copy()
        df_month2 = df_month2.copy()
        
        df_month1['Category'] = df_month1['Category'].astype(str)
        df_month2['Category'] = df_month2['Category'].astype(str)
        
        # Filter out invalid categories
        df_month1 = df_month1[df_month1['Category'] != 'nan']
        df_month2 = df_month2[df_month2['Category'] != 'nan']
        
        # Aggregate by category
        agg_month1 = df_month1.groupby('Category')[metrics].sum().reset_index()
        agg_month2 = df_month2.groupby('Category')[metrics].sum().reset_index()
        
        # Merge the data
        comparison = pd.merge(agg_month1, agg_month2, on='Category', suffixes=(f'_{month1}', f'_{month2}'), how='outer').fillna(0)
        
        # Calculate percentage changes
        for metric in metrics:
            col1 = f'{metric}_{month1}'
            col2 = f'{metric}_{month2}'
            comparison[f'{metric}_change'] = comparison.apply(
                lambda row: calculate_percentage_change(row[col1], row[col2]), axis=1
            )
          # Create table data
        table_data = []
        for _, row in comparison.iterrows():
            row_data = {'Category': row['Category']}
            
            for metric in metrics:
                col1 = f'{metric}_{month1}'
                col2 = f'{metric}_{month2}'
                change_col = f'{metric}_change'
                
                row_data[f'{month1}_{metric}'] = f"{row[col1]:,.0f}"
                row_data[f'{month2}_{metric}'] = f"{row[col2]:,.0f}"
                row_data[f'Change_{metric}'] = format_percentage(row[change_col])
            
            table_data.append(row_data)
        
        # Create multi-level columns
        columns = [
            {'name': ['', 'Category'], 'id': 'Category', 'type': 'text'}
        ]
        
        for metric in metrics:
            columns.extend([
                {'name': [month1, metric], 'id': f'{month1}_{metric}', 'type': 'text'},
                {'name': [month2, metric], 'id': f'{month2}_{metric}', 'type': 'text'},
                {'name': ['% Change', metric], 'id': f'Change_{metric}', 'type': 'text'}
            ])
        
        # Style data conditionally for percentage columns
        style_data_conditional = []
        for metric in metrics:
            change_col = f'Change_{metric}'
            for i, row in enumerate(table_data):
                change_value = row[change_col]
                if change_value.startswith('+'):
                    color = '#28a745'
                elif change_value.startswith('-'):
                    color = '#dc3545'
                else:
                    color = '#6c757d'
                
                style_data_conditional.append({
                    'if': {'row_index': i, 'column_id': change_col},
                    'color': color,
                    'fontWeight': 'bold'
                })
        
        return dash_table.DataTable(
            data=table_data,
            columns=columns,
            merge_duplicate_headers=True,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '12px',
                'fontFamily': 'Arial, sans-serif',
                'fontSize': '14px',
                'border': '1px solid #ddd'
            },
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'color': '#333',
                'border': '1px solid #ddd',
                'textAlign': 'center'
            },
            style_data_conditional=style_data_conditional,
            page_size=20,
            sort_action='native',
            filter_action='native'
        )
    
    except Exception as e:
        print(f"Error creating category comparison: {e}")
        return html.Div(f"Error creating category comparison table: {str(e)}")

def create_item_comparison(df_month1, df_month2, month1, month2):
    """Create item comparison table"""
    try:
        # Ensure Item name column is string type and clean data
        df_month1 = df_month1.copy()
        df_month2 = df_month2.copy()
        
        df_month1['Item name'] = df_month1['Item name'].astype(str)
        df_month2['Item name'] = df_month2['Item name'].astype(str)
        
        # Filter out invalid item names
        df_month1 = df_month1[df_month1['Item name'] != 'nan']
        df_month2 = df_month2[df_month2['Item name'] != 'nan']
        
        # Aggregate by item name
        agg_month1 = df_month1.groupby('Item name')[metrics].sum().reset_index()
        agg_month2 = df_month2.groupby('Item name')[metrics].sum().reset_index()
        
        # Merge the data
        comparison = pd.merge(agg_month1, agg_month2, on='Item name', suffixes=(f'_{month1}', f'_{month2}'), how='outer').fillna(0)
        
        # Calculate percentage changes
        for metric in metrics:
            col1 = f'{metric}_{month1}'
            col2 = f'{metric}_{month2}'
            comparison[f'{metric}_change'] = comparison.apply(
                lambda row: calculate_percentage_change(row[col1], row[col2]), axis=1
            )
        
        # Sort by total revenue change (descending)
        if 'Item revenue_change' in comparison.columns:
            comparison = comparison.sort_values('Item revenue_change', ascending=False)
        
        # Take top 50 items to avoid overwhelming the table
        comparison = comparison.head(50)
          # Create table data
        table_data = []
        for _, row in comparison.iterrows():
            row_data = {'Item name': row['Item name']}
            
            for metric in metrics:
                col1 = f'{metric}_{month1}'
                col2 = f'{metric}_{month2}'
                change_col = f'{metric}_change'
                
                row_data[f'{month1}_{metric}'] = f"{row[col1]:,.0f}"
                row_data[f'{month2}_{metric}'] = f"{row[col2]:,.0f}"
                row_data[f'Change_{metric}'] = format_percentage(row[change_col])
            
            table_data.append(row_data)
        
        # Create multi-level columns
        columns = [
            {'name': ['', 'Item Name'], 'id': 'Item name', 'type': 'text'}
        ]
        
        for metric in metrics:
            columns.extend([
                {'name': [month1, metric], 'id': f'{month1}_{metric}', 'type': 'text'},
                {'name': [month2, metric], 'id': f'{month2}_{metric}', 'type': 'text'},
                {'name': ['% Change', metric], 'id': f'Change_{metric}', 'type': 'text'}
            ])
        
        # Style data conditionally for percentage columns
        style_data_conditional = []
        for metric in metrics:
            change_col = f'Change_{metric}'
            for i, row in enumerate(table_data):
                change_value = row[change_col]
                if change_value.startswith('+'):
                    color = '#28a745'
                elif change_value.startswith('-'):
                    color = '#dc3545'
                else:
                    color = '#6c757d'
                
                style_data_conditional.append({
                    'if': {'row_index': i, 'column_id': change_col},
                    'color': color,
                    'fontWeight': 'bold'
                })
        
        return dash_table.DataTable(
            data=table_data,
            columns=columns,
            merge_duplicate_headers=True,
            style_table={'overflowX': 'auto'},
            style_cell={
                'textAlign': 'left',
                'padding': '12px',
                'fontFamily': 'Arial, sans-serif',
                'fontSize': '14px',
                'border': '1px solid #ddd',
                'maxWidth': '200px',
                'overflow': 'hidden',
                'textOverflow': 'ellipsis'
            },
            style_header={
                'backgroundColor': '#f8f9fa',
                'fontWeight': 'bold',
                'color': '#333',
                'border': '1px solid #ddd',
                'textAlign': 'center'
            },
            style_data_conditional=style_data_conditional,
            page_size=20,
            sort_action='native',
            filter_action='native',
            tooltip_data=[
                {
                    'Item name': {'value': str(row['Item name']), 'type': 'markdown'}
                } for row in table_data
            ],
            tooltip_duration=None
        )
    
    except Exception as e:
        print(f"Error creating item comparison: {e}")
        return html.Div(f"Error creating item comparison table: {str(e)}")



if __name__ == '__main__':
    print("\n" + "="*50)
    print("🚀 Starting Comparison Dashboard...")
    print("="*50)
    
    if df.empty:
        print("❌ No data loaded. Please run mainDashboard.py first to generate cache.")
    else:
        print(f"✅ Data loaded successfully: {df.shape[0]} rows, {df.shape[1]} columns")
        print(f"📅 Available months: {len(get_available_months())}")
        print(f"🏢 Available brands: {len(get_available_brands())-1}")  # -1 for 'All'
        print(f"📦 Available categories: {len(get_available_categories())-1}")  # -1 for 'All'
        
    print("\n🌐 Dashboard will be available at: http://127.0.0.1:8050")
    print("📊 Features:")
    print("   • Month-to-month comparison")
    print("   • Percentage change calculations with color coding")
    print("   • Filtering by Brand, Category, and Day")
    print("   • Category-wise and Item-wise comparison tables")
    print("   • Sortable and filterable tables")
    print("\n" + "="*50)
    
    app.run(debug=True, host='127.0.0.1', port=8050)

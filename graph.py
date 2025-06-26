from graphviz import Digraph
import os

# Set path to GraphViz executables
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

# All scenarios and their respective flows
scenarios = {
    "Scenario 1: Online Order Fulfilled from Mall Store as Home Delivery": {
        "Current Flow": [
            "Customer Placed Online Order",
            "Customer select Home Delivery",
            "Order Allocated to mall store & stock reserved in system",
            "Order shipped and Invoice generated",
            
            "Invoice contains Customer Shipping and Billing address",
            "Post Delivery sales accounted in Mall store"
        ],
        "Proposed Flow": [
            "Customer Placed Online Order",
            "Customer select Home Delivery",
            "Order Allocated to mall store & stock virtually transferred to high street store",

            "Order shipped and Invoice generated",
            "Customer Shipping and Billing address is mentioned on the Invoice",
            "Post Delivery sales accounted in Highstreet store"
        ]
    },
    "Scenario 2: Online Order Collected from Mall Store by Customer (Click & Collect)": {
        "Current Flow": [
            "Customer Placed Online Order",
            "Customer select Click& Collect method",
            "Order Allocated to mall store & stock reserved in system",

            "Order shipped and Invoice generated",
            "Invoice contains Mall Store Shipping and Customer Billing address",
            "Post collection sales accounted in Mall store"
        ],
        "Proposed Flow": [
            "Customer Placed Online Order",
            "Customer select Click& Collect method",
            "Order Allocated to mall store & stock virtually transferred to high street store",
            "Order shipped and Invoice generated",

            "Invoice contains Highstreet Store Shipping and Customer Billing address",
            "Post Delivery sales accounted in Highstreet store"
        ]
    },
    "Scenario 3: Endless Aisle - Ordered in Store A, Collected from Mall Store B (Click & Collect)": {
        "Current Flow": [
            "Store Staff assist customer to place Order",
            "Choose store based on availability and place Click & Collect order",
            "Order Allocated to mall store & stock reserved in system",
            "Customer collect the order from Mall store and Invoice generated",

            "Invoice contains Mall Store Shipping address and Customer Billing address",
            "Post collection sales accounted in Mall store"
        ],
        "Proposed Flow": [
            "Store Staff assist customer to place Order",
            "Choose store based on availability and place Click & Collect order",
            "Order Allocated to mall store & stock virtually transferred to high street store",
            "Customer collect the order from Mall store and Invoice generated",
            "Invoice contains Highstreet Store Shipping and Customer Billing address",
            "Post collection accounted in Highstreet store"
        ]
    },
    "Scenario 4: Endless Aisle - Ordered & Collected from Same Mall Store (Click & Collect)": {
        "Current Flow": [
            "Store Staff assist customer to place Order",
            "Choose own store and place Click & Collect order",
            "Order Allocated to mall store & stock reserved in system",
            "Customer collect the order from same mall store and Invoice generated",

            "Invoice contains Mall Store Shipping address and Customer Billing address",
            "Post collection sales accounted in Mall store"
        ],
        "Proposed Flow": [
            "Store Staff assist customer to place Order",
            "Choose own store and place Click & Collect order",
            "Order Allocated to same mall store & stock virtually transferred to high street store",
            "Customer collect the order from same mall store and Invoice generated",
            "Invoice contains Highstreet Store Shipping address and Customer Billing address",
            "Post collection accounted in Highstreet store"
        ]
    },
    "Scenario 5: Endless Aisle - Ordered in Store A, Delivered from Mall B Store (Home Delivery)": {
        "Current Flow": [
            "Mall Store Staff assist customer to place Order",
            "Choose home delivery option",
            "Order Allocated to mall store & stock reserved in system",
            "Order shipped and Invoice generated",
            "Invoice contains Customer Shipping and Billing address",
            "Post Delivery sales accounted in Mall store"
        ],
        "Proposed Flow": [
            "Store Staff assist customer to place Order",
            "Choose home delivery option",
            "Order Allocated to mall store & stock virtually transferred to high street store",
            "Order shipped and Invoice generated",
            "Invoice contains Customer Shipping and Billing address",
            "Post delivery sales accounted in Highstreet store"
        ]
    },
    "Scenario 6: Endless Aisle - Ordered in Store A, Delivered from Same Mall Store (Home Delivery)": {
        "Current Flow": [
            "Store Staff assist customer to place Order",
            "Choose home delivery option",
            "Order Allocated to mall store & stock reserved in system",
            "Order shipped and Invoice generated",
            "Invoice contains Customer Shipping and Billing address",
            "Post Delivery sales accounted in Mall store"
        ],
        "Proposed Flow": [
            "Store Staff assist customer to place Order",
            "Choose home delivery option",
            "Order Allocated to mall store & stock virtually transferred to high street store",
            "Order shipped and Invoice generated",
            "Invoice contains Customer Shipping and Billing address",
            "Post delivery sales accounted in Highstreet store"
        ]
    }
}

def wrap_text(text, width):
    """Wrap text to fit in nodes better with more square proportions"""
    import textwrap
    lines = textwrap.wrap(text, width=width)
    return '\\n'.join(lines)

def calculate_spacing(flow_steps, width_constraint=16):
    """Calculate appropriate spacing based on content length"""
    total_content = sum(len(step) for step in flow_steps)
    # More content means smaller spacing to fit in the width constraint
    if total_content > 300:
        return "0.6"  # Small spacing for verbose scenarios
    elif total_content > 200:
        return "0.9"  # Medium spacing
    else:
        return "1.2"  # Larger spacing for concise scenarios

# Create left-to-right flowcharts for each scenario with better readability
def create_flowcharts(scenarios):
    for scenario, flows in scenarios.items():
        dot = Digraph(comment=scenario, format='png')
        
        # Calculate appropriate spacing based on content length
        current_ranksep = calculate_spacing(flows['Current Flow'])
        proposed_ranksep = calculate_spacing(flows['Proposed Flow'])
        
        # Use the smaller of the two to ensure both flows fit well
        ranksep = min(current_ranksep, proposed_ranksep)
        
        dot.attr(rankdir='LR', size='16,8', dpi='300', bgcolor='white', 
                 nodesep='0.4', ranksep=ranksep)
        dot.attr('node', shape='box', style='filled', fontsize='13', fontname='Arial')
        dot.attr('edge', fontsize='10', fontname='Arial')
        
        # Special handling for Scenario 2 - Add a header node for clarity
        is_scenario_2 = "Scenario 2" in scenario
        
        # Proposed Flow section
        with dot.subgraph(name='cluster_proposed') as c:
            c.attr(label='PROPOSED FLOW', labeljust='l', fontsize='16', fontcolor='#006633',
                  style='filled', fillcolor='#F0FFF0', fontname='Arial Bold', margin='10')
            
            prev = None
            for i, step in enumerate(flows['Proposed Flow']):
                node = f'P{i}'                # Break long text into multiple lines for compact boxes
                wrapped_text = wrap_text(step, 18)
                # Calculate node size based on text length
                text_length = len(step)
                width = max(1.3, min(2.0, 1.3 + (text_length / 100)))
                height = max(0.8, min(1.5, 0.8 + (len(wrapped_text.split('\\n')) * 0.15)))
                c.node(node, wrapped_text, fillcolor='#E6FFE6', style='filled,rounded',
                      fontsize='12', fontname='Arial', margin='0.15,0.15', width=str(width), height=str(height))
                if prev:
                    c.edge(prev, node, color='#006633', penwidth='1.5')
                prev = node
                
        # Current Flow section
        with dot.subgraph(name='cluster_current') as c:
            c.attr(label='CURRENT FLOW', labeljust='l', fontsize='16', fontcolor='#0066CC',
                  style='filled', fillcolor='#F0F8FF', fontname='Arial Bold', margin='10')
            
            prev = None
            for i, step in enumerate(flows['Current Flow']):
                node = f'C{i}'                # Break long text into multiple lines for compact boxes
                wrapped_text = wrap_text(step, 18)
                # Use a different node ID for Scenario 2 to avoid conflicts
                if is_scenario_2:
                    node = f'C{i}_current'
                # Calculate node size based on text length
                text_length = len(step)
                width = max(1.3, min(2.0, 1.3 + (text_length / 100)))
                height = max(0.8, min(1.5, 0.8 + (len(wrapped_text.split('\\n')) * 0.15)))
                c.node(node, wrapped_text, fillcolor='#E6F3FF', style='filled,rounded', 
                      fontsize='12', fontname='Arial', margin='0.15,0.15', width=str(width), height=str(height))
                if prev:
                    c.edge(prev, node, color='#0066CC', penwidth='1.5')
                prev = node
            
        # Clean up the filename - replace problematic characters
        filename = scenario.replace(":", "").replace(",", "").replace("–", "-").replace("&", "and").replace(" ", "_")
        # Save to the flowcharts directory
        output_path = os.path.join("flowcharts", filename)
        dot.render(filename=output_path, cleanup=True)

create_flowcharts(scenarios)

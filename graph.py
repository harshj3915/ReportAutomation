from graphviz import Digraph
import os

# Set path to GraphViz executables
os.environ["PATH"] += os.pathsep + r"C:\Program Files\Graphviz\bin"

# All scenarios and their respective flows
scenarios = {
    "Scenario 1: Online Order Fulfilled from Mall Store as Home Delivery": {
        "Current Flow": [
            "Customer places online order.",
            "Order is for Home Delivery.",
            "Order is put on hold in mall store through ERP.",
            "Once confirmed for delivery by the order system, stock is deducted from mall store.",
            "Mall store picks, packs, and dispatches the order via courier.",
            "Sales are recorded in designated store system.",
            "Invoice generated from order system with customer shipping and billing address.",
            "Post-delivery, sales are recorded in ERP."
        ],
        "Proposed Flow": [
            "Customer places online order.",
            "Order is for Home Delivery.",
            "Order is allocated to mall store.",
            "Stock is virtually transferred to a designated high street store.",
            "Order is shipped and invoice is generated.",
            "Shipping and billing address remain the customer's.",
            "Sales are shown as fulfilled from designated high street store in ERP."
        ]
    },

    "Scenario 2: Online Order Fulfilled by Supplier – No Change": {
        "Current Flow": [
            "Customer places order.",
            "Supplier directly ships to the customer.",
            "Sales are recorded in designated store system.",
            "Invoice generated from order system with customer's shipping and billing address."
        ],
        "Proposed Flow": [
            "Customer places order.",
            "Supplier directly ships to the customer.",
            "Sales are recorded in designated store system.",
            "Invoice generated from order system with customer's shipping and billing address."
        ]
    },

    "Scenario 3 Option A: Click & Collect from Mall Store": {
        "Current Flow": [
            "Customer places online order.",
            "Order is held in mall store via ERP.",
            "Stock is deducted on customer pickup confirmation.",
            "Customer collects from the mall store.",
            "Sales are recorded in designated store system.",
            "Invoice is generated showing mall store as shipping address and customer as billing address."
        ],
        "Proposed Flow": [
            "Customer places online order.",
            "Order is held in mall store via ERP.",
            "Stock is deducted on customer pickup confirmation.",
            "Customer collects from the mall store.",
            "Sales are recorded in designated store system.",
            "Invoice is generated showing mall store as shipping address and customer as billing address."
        ]
    },

    "Scenario 3 Option B: Click & Collect – With Virtual Transfer": {
        "Current Flow": [
            "Order is held in mall store via ERP.",
            "Deducted from mall store on customer collection.",
            "Customer picks up from mall store.",
            "Sales recorded in designated store system."
        ],
        "Proposed Flow": [
            "Order held by mall store.",
            "Stock virtually transferred to designated high street store.",
            "Deducted from designated store when customer picks up.",
            "Sales shown under high street store.",
            "Invoice shows shipping from high street store; billing to customer.",
            "Tracked via mystery shopper for verification."
        ]
    },

    "Scenario 4 Option A: Ordered in Store A, Collected from Mall Store B": {
        "Current Flow": [
            "Order held in mall store.",
            "Deducted on pickup.",
            "Collected by customer.",
            "Sales recorded under designated store."
        ],
        "Proposed Flow": [
            "Order held in mall store.",
            "Virtually transferred to designated high street store.",
            "Deducted on pickup from designated store.",
            "Invoice shows mall store as shipping location.",
            "Customer as billing address."
        ]
    },

    "Scenario 4 Option B: Same as 4A but Invoice from Designated Store": {
        "Current Flow": [
            "Order held in mall store.",
            "Deducted on pickup.",
            "Collected by customer.",
            "Sales recorded under designated store."
        ],
        "Proposed Flow": [
            "Order held in mall store.",
            "Virtually transferred to designated high street store.",
            "Deducted on pickup from designated store.",
            "Invoice shows designated high street store as shipping address.",
            "Mystery shopper used for verification."
        ]
    },

    "Scenario 5 Option A: Ordered & Collected from Same Mall Store": {
        "Current Flow": [
            "Order held in same mall store.",
            "Deducted on customer pickup.",
            "Collected from same store.",
            "Invoice shows mall store as shipping address and customer as billing address."
        ],
        "Proposed Flow": [
            "Order held in same mall store.",
            "Deducted on customer pickup.",
            "Collected from same store.",
            "Invoice shows mall store as shipping address and customer as billing address."
        ]
    },

    "Scenario 5 Option B: Ordered & Collected with Virtual Transfer": {
        "Current Flow": [
            "Order held in mall store.",
            "Deducted on customer pickup.",
            "Collected from mall store.",
            "Sales recorded under designated store."
        ],
        "Proposed Flow": [
            "Order virtually transferred to designated high street store.",
            "Deducted from designated store upon pickup.",
            "Collected from mall store.",
            "Invoice shows designated store as shipping origin.",
            "Verification possible via mystery shopper."
        ]
    },

    "Scenario 6 Option A: Ordered in Store A, Delivered from Mall Store A": {
        "Current Flow": [
            "Order held in mall store.",
            "Deducted on shipping confirmation.",
            "Picked, packed, and shipped from mall store by courier.",
            "Invoice shows customer shipping and billing address."
        ],
        "Proposed Flow": [
            "Order held in mall store.",
            "Deducted on shipping confirmation.",
            "Picked, packed, and shipped from mall store by courier.",
            "Invoice shows customer shipping and billing address."
        ]
    },

    "Scenario 6 Option B: Delivered via Virtual Transfer": {
        "Current Flow": [
            "Order held in mall store.",
            "Deducted on shipping confirmation.",
            "Picked, packed, and shipped from mall store by courier.",
            "Invoice shows customer shipping and billing address."
        ],
        "Proposed Flow": [
            "Stock virtually transferred to designated high street store.",
            "Deducted from designated store on shipment confirmation.",
            "Still physically packed and dispatched from mall store.",
            "Invoice shows customer addresses.",
            "Traced via mystery shopper if needed."
        ]
    },

    "Scenario 7 Option A: Ordered in Store A, Delivered from Mall Store B": {
        "Current Flow": [
            "Order held and fulfilled from mall store B.",
            "Shipped via courier.",
            "Invoice from order system with customer address details."
        ],
        "Proposed Flow": [
            "Order held and fulfilled from mall store B.",
            "Shipped via courier.",
            "Invoice from order system with customer address details."
        ]
    },

    "Scenario 7 Option B: Delivered via Virtual Transfer from Store B": {
        "Current Flow": [
            "Order held in mall store via ERP.",
            "Deducted from mall store on delivery confirmation.",
            "Sales recorded in designated store system.",
            "Order shipped by mall store B.",
            "Invoice shows customer shipping and billing address."
        ],
        "Proposed Flow": [
            "Order virtually transferred to designated high street store.",
            "Deducted from designated store after shipping.",
            "Mall store B dispatches the order.",
            "Customer shipping and billing address remain same.",
            "Traced via mystery shopper."
        ]
    }
}

def wrap_text(text, width):
    """Wrap text to fit in nodes better with more square proportions"""
    import textwrap
    lines = textwrap.wrap(text, width=width)
    return '\\n'.join(lines)

# Create left-to-right flowcharts for each scenario with better readability
def create_flowcharts(scenarios):
    for scenario, flows in scenarios.items():
        dot = Digraph(comment=scenario, format='png')
        dot.attr(rankdir='LR', size='16,8', dpi='300', bgcolor='white', 
                 nodesep='0.4', ranksep='0.8')
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
                node = f'P{i}'
                # Break long text into multiple lines for compact boxes
                wrapped_text = wrap_text(step, 18)
                c.node(node, wrapped_text, fillcolor='#E6FFE6', style='filled,rounded',
                      fontsize='12', fontname='Arial', margin='0.15,0.15', width='1.5', height='1.0')
                if prev:
                    c.edge(prev, node, color='#006633', penwidth='1.5')
                prev = node
                
        # Current Flow section
        with dot.subgraph(name='cluster_current') as c:
            c.attr(label='CURRENT FLOW', labeljust='l', fontsize='16', fontcolor='#0066CC',
                  style='filled', fillcolor='#F0F8FF', fontname='Arial Bold', margin='10')
            
            prev = None
            for i, step in enumerate(flows['Current Flow']):
                node = f'C{i}'
                # Break long text into multiple lines for compact boxes
                wrapped_text = wrap_text(step, 18)
                # Use a different node ID for Scenario 2 to avoid conflicts
                if is_scenario_2:
                    node = f'C{i}_current'
                c.node(node, wrapped_text, fillcolor='#E6F3FF', style='filled,rounded', 
                      fontsize='12', fontname='Arial', margin='0.15,0.15', width='1.5', height='1.0')
                if prev:
                    c.edge(prev, node, color='#0066CC', penwidth='1.5')
                prev = node
            
        # Clean up the filename - replace problematic characters
        filename = scenario.replace(":", "").replace(",", "").replace("–", "-").replace("&", "and").replace(" ", "_")
        # Save to the flowcharts directory
        output_path = os.path.join("flowcharts", filename)
        dot.render(filename=output_path, cleanup=True)

create_flowcharts(scenarios)

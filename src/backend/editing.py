import psycopg2
import os
from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from decimal import Decimal  # Import Decimal for price calculations

# Load environment variables
load_dotenv()

# Connect to PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create Blueprint for editing
editing_bp = Blueprint('editing', __name__)

# Function to get the best editing PC components based on the budget
def get_editing_build(budget):
    if budget >= 500 and budget <= 700:
        build_type = 'Entry Level'
        cpu_budget = (150, 180)
        gpu_budget = (150, 200)
        motherboard_budget = (70, 100)
        ram_budget = (60, 80)
        storage_budget = (50, 70)
        psu_budget = (40, 60)
        cooler_budget = (20, 40)
        case_budget = (40, 50)
        monitor_budget = (100, 150)
    elif budget > 700 and budget <= 1000:
        build_type = 'Mid Level'
        cpu_budget = (180, 250)
        gpu_budget = (250, 350)
        motherboard_budget = (100, 120)
        ram_budget = (80, 100)
        storage_budget = (80, 100)
        psu_budget = (60, 80)
        cooler_budget = (40, 60)
        case_budget = (50, 70)
        monitor_budget = (200, 300)
    elif budget > 1000:
        build_type = 'High Level'
        cpu_budget = (250, 400)
        gpu_budget = (350, 500)
        motherboard_budget = (150, 200)
        ram_budget = (100, 150)
        storage_budget = (100, 150)
        psu_budget = (80, 120)
        cooler_budget = (60, 100)
        case_budget = (80, 150)
        monitor_budget = (300, 500)
    else:
        return "Budget too low for an editing PC."

    # Query for each component
    def query_component(category, price_range, extra_conditions=""):
        # Properly quote the table name to avoid issues with reserved keywords like "case"
        query = f"""
            SELECT name, price
            FROM "{category}"  -- Use double quotes to ensure proper table name handling
            WHERE price >= %s AND price <= %s {extra_conditions}
            ORDER BY price DESC
            LIMIT 1
        """
        cursor.execute(query, price_range)
        result = cursor.fetchone()

        if result is None:
            return (f"No component found in {category}", Decimal(0))
        
        return result

    # Get components based on price ranges
    cpu = query_component('cpu', cpu_budget, "AND core_count >= 6 AND core_clock >= 3.0")
    video_card = query_component('video_card', gpu_budget, "AND memory >= 6")
    motherboard = query_component('motherboard', motherboard_budget, f"AND socket = '{cpu[0].split()[1]}'")  # Match CPU socket
    memory = query_component('memory', ram_budget, "AND module_size >= 16")  # At least 16GB RAM
    internal_hard_drive = query_component('internal_hard_drive', storage_budget, "AND capacity >= 1024 AND tipe = 'SSD'")  # At least 1TB SSD
    power_supply = query_component('power_supply', psu_budget, "AND wattage >= 500")
    cpu_coolers = query_component('cpu_coolers', cooler_budget)
    cases = query_component('cases', case_budget)  # Assume ATX case size
    monitor = query_component('monitor', monitor_budget, "AND screen_size >= 27")

    # Collect the total build
    components = [
        {"name": cpu[0], "price": cpu[1], "category": "cpu"},
        {"name": video_card[0], "price": video_card[1], "category": "video_card"},
        {"name": motherboard[0], "price": motherboard[1], "category": "motherboard"},
        {"name": memory[0], "price": memory[1], "category": "memory"},
        {"name": internal_hard_drive[0], "price": internal_hard_drive[1], "category": "internal_hard_drive"},
        {"name": power_supply[0], "price": power_supply[1], "category": "power_supply"},
        {"name": cpu_coolers[0], "price": cpu_coolers[1], "category": "cpu_coolers"},
        {"name": cases[0], "price": cases[1], "category": "cases"},
        {"name": monitor[0], "price": monitor[1], "category": "monitor"},
    ]
    
    # Filter out components with zero price
    valid_components = [comp for comp in components if comp["price"] > 0]
    total_price = sum(comp["price"] for comp in valid_components)

    # Define component priority from least important to most important
    component_priority = ["cases", "cpu_coolers", "monitor", "power_supply", "internal_hard_drive", "memory", "video_card", "cpu"]

    # Handle budget exceeding by reducing component prices starting from least important
    while total_price > budget:
        for priority in component_priority:
            for i in range(len(valid_components)):
                if valid_components[i]["category"] == priority:
                    # Reduce maximum price by 10%
                    max_price = valid_components[i]["price"] * Decimal(0.9)
                    new_component = query_component(valid_components[i]["category"].lower(), (Decimal(0), max_price))

                    # If a cheaper component is found, replace it
                    if new_component[1] < valid_components[i]["price"]:
                        valid_components[i]["name"] = new_component[0]
                        valid_components[i]["price"] = new_component[1]

            total_price = sum(comp["price"] for comp in valid_components)
            if total_price <= budget:
                break

    # Format output with categories
    output = {
        "Build Type": build_type,
        "Total Price": total_price,
        "Components": {comp["name"]: {"price": comp["price"], "category": comp["category"]} for comp in valid_components},
    }

    return output

# Route to get editing build
@editing_bp.route('/editing_build', methods=['GET'])
def editing_build():
    budget = int(request.args.get('budget', 0))
    build = get_editing_build(budget)

    # Format output jadi JSON
    response = {
        "Build Type": build['Build Type'],
        "Total Price": float(build['Total Price']),  # Convert Decimal to float
        "Components": {category: {"name": component['name'], "price": float(component['price'])} for category, component in build["Components"].items()}
    }

    return jsonify(response), 200

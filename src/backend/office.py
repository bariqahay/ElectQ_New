from flask import Blueprint, jsonify, request
import psycopg2
import os
from dotenv import load_dotenv
from decimal import Decimal

# Load environment variables
load_dotenv()

# Connect to PostgreSQL
DATABASE_URL = os.getenv('DATABASE_URL')
conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor()

# Create Blueprint for gaming
office_bp = Blueprint('office', __name__)

# Function to get gaming build components
def get_office_build(budget):
    if budget >= 500 and budget <= 700:
        build_type = 'Entry Level'
        cpu_budget = (80, 120)
        gpu_budget = (50, 80)  # Integrated GPU
        motherboard_budget = (60, 80)
        ram_budget = (40, 60)
        storage_budget = (50, 70)
        psu_budget = (30, 50)
        cooler_budget = (10, 30)
        case_budget = (30, 50)
        monitor_budget = (100, 120)
    elif budget > 700 and budget <= 1000:
        build_type = 'Mid Level'
        cpu_budget = (120, 150)
        gpu_budget = (80, 100)  # Entry-level GPU
        motherboard_budget = (80, 100)
        ram_budget = (60, 80)
        storage_budget = (60, 80)
        psu_budget = (50, 70)
        cooler_budget = (30, 50)
        case_budget = (40, 60)
        monitor_budget = (150, 200)
    elif budget > 1000:
        build_type = 'High Level'
        cpu_budget = (150, 200)
        gpu_budget = (100, 150)  # Entry-level dedicated GPU
        motherboard_budget = (100, 150)
        ram_budget = (80, 100)
        storage_budget = (80, 120)
        psu_budget = (50, 80)
        cooler_budget = (50, 80)
        case_budget = (50, 100)
        monitor_budget = (200, 300)
    else:
        return "Budget too low for an office PC."

    # Function to query each component
    def query_component(category, price_range, extra_conditions="", condition_params=()):
        query = f"""
            SELECT name, price
            FROM "{category}"
            WHERE price >= %s AND price <= %s {extra_conditions}
            ORDER BY price DESC
            LIMIT 1
        """
        # Execute the query with the price range and any additional condition parameters
        cursor.execute(query, (*price_range, *condition_params))
        result = cursor.fetchone()

        if result is None:
            return (f"No component found in {category}", Decimal(0))

        return result

    # Get components based on price ranges
    cpu = query_component('cpu', cpu_budget, "AND core_count >= 4 AND core_clock >= 3.0 AND tdp <= 65")
    video_card = query_component('video_card', gpu_budget, "AND memory >= 6 AND (chipset LIKE %s OR chipset LIKE %s)", ('Geforce%', 'Radeon%'))

    # Check if CPU is found before splitting
    if cpu[0]:
        motherboard = query_component('motherboard', motherboard_budget, f"AND socket = '{cpu[0].split()[1]}'")
    else:
        motherboard = ("No motherboard found", Decimal(0))
        
    memory = query_component('memory', ram_budget, "AND module_size >= 8")
    internal_hard_drive = query_component('internal_hard_drive', storage_budget, "AND capacity >= 256 AND tipe = 'SSD'")
    power_supply = query_component('power_supply', psu_budget, "AND wattage >= 400")
    cpu_coolers = query_component('cpu_coolers', cooler_budget)
    cases = query_component('cases', case_budget)
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

# Route to get gaming build
@office_bp.route('/office_build', methods=['GET'])
def gaming_build():
    budget = int(request.args.get('budget', 0))
    build = get_office_build(budget)

    # Format output jadi JSON
    response = {
        "Build Type": build['Build Type'],
        "Total Price": float(build['Total Price']),  # Convert Decimal to float
        "Components": {category: {"name": component['name'], "price": float(component['price'])} for category, component in build["Components"].items()}
    }

    return jsonify(response), 200

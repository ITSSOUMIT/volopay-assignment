import csv
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Load the CSV data
data = []

with open('data.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        data.append(row)



@app.route('/api/total_items', methods=['GET'])
def get_total_items():
    start_date = request.args.getlist('start_date')
    end_date = request.args.getlist('end_date')
    department = request.args.getlist('department')

    # Check if any of the parameters is missing
    if not all([start_date, end_date, department]):
        missing_params = []
        if not start_date:
            missing_params.append('start_date')
        if not end_date:
            missing_params.append('end_date')
        if not department:
            missing_params.append('department')
        error_message = f"Missing parameter(s): {', '.join(missing_params)}"
        return jsonify({'error': error_message}), 400

    # Format the input dates to "YYYY-MM-DD" format
    start_date = datetime.strptime(start_date[0], "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date[0], "%Y-%m-%d").date()

    # Perform date filtering and department filtering
    filtered_data = [item for item in data if start_date <= datetime.strptime(item['date'], "%Y-%m-%d %H:%M:%S %z").date() <= end_date and item['department'] == department[0]]

    # Calculate the total number of items sold
    total_items = sum(int(item['seats']) for item in filtered_data)

    return jsonify(total_items)



@app.route('/api/nth_most_total_item', methods=['GET'])
def get_nth_most_total_item():
    item_by = request.args.get('item_by')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    n = int(request.args.get('n'))

    # Check if any of the parameters is missing
    if not all([item_by, start_date, end_date, n]):
        missing_params = []
        if not item_by:
            missing_params.append('item_by')
        if not start_date:
            missing_params.append('start_date')
        if not end_date:
            missing_params.append('end_date')
        if not n:
            missing_params.append('n')
        error_message = f"Missing parameter(s): {', '.join(missing_params)}"
        return jsonify({'error': error_message}), 400

    # Format the input dates to "YYYY-MM-DD" format
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Perform date filtering
    filtered_data = [item for item in data if start_date <= datetime.strptime(item['date'], "%Y-%m-%d %H:%M:%S %z").date() <= end_date]

    # Calculate the total quantity sold and total price for each item
    items_quantity = {}
    items_price = {}

    for item in filtered_data:
        item_name = item['software']
        quantity = int(item['seats'])
        price = float(item['amount'])

        if item_name in items_quantity:
            items_quantity[item_name] += quantity
        else:
            items_quantity[item_name] = quantity

        if item_name in items_price:
            items_price[item_name] += price
        else:
            items_price[item_name] = price

    # Sort items based on quantity or price
    if item_by == 'quantity':
        sorted_items = sorted(items_quantity.items(), key=lambda x: x[1], reverse=True)
    elif item_by == 'price':
        sorted_items = sorted(items_price.items(), key=lambda x: x[1], reverse=True)
    else:
        return jsonify({'error': 'Invalid value for item_by parameter. Expected "quantity" or "price".'}), 400

    # Retrieve the nth most sold item
    if n > len(sorted_items):
        return jsonify({'error': 'Invalid value for n parameter. Exceeds the number of available items.'}), 400

    nth_item_name = sorted_items[n - 1][0]

    return jsonify(nth_item_name)



@app.route('/api/percentage_of_department_wise_sold_items', methods=['GET'])
def get_percentage_of_department_wise_sold_items():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    # Check if any of the parameters is missing
    if not all([start_date, end_date]):
        missing_params = []
        if not start_date:
            missing_params.append('start_date')
        if not end_date:
            missing_params.append('end_date')
        error_message = f"Missing parameter(s): {', '.join(missing_params)}"
        return jsonify({'error': error_message}), 400

    # Format the input dates to "YYYY-MM-DD" format
    start_date = datetime.strptime(start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

    # Perform date filtering
    filtered_data = [item for item in data if start_date <= datetime.strptime(item['date'], "%Y-%m-%d %H:%M:%S %z").date() <= end_date]

    # Calculate the total quantity sold for each department
    department_quantity = {}

    for item in filtered_data:
        department = item['department']
        quantity = int(item['seats'])

        if department in department_quantity:
            department_quantity[department] += quantity
        else:
            department_quantity[department] = quantity

    # Calculate the total quantity sold across all departments
    total_quantity = sum(department_quantity.values())

    # Calculate the percentage of sold items department-wise
    percentage_of_department_sold_items = {
        department: f"{(quantity / total_quantity) * 100}%"
        for department, quantity in department_quantity.items()
    }

    return jsonify(percentage_of_department_sold_items)



@app.route('/api/monthly_sales', methods=['GET'])
def get_monthly_sales():
    product = request.args.get('product')
    year = int(request.args.get('year'))

    # Check if any of the parameters is missing
    if not all([product, year]):
        missing_params = []
        if not product:
            missing_params.append('product')
        if not year:
            missing_params.append('year')
        error_message = f"Missing parameter(s): {', '.join(missing_params)}"
        return jsonify({'error': error_message}), 400

    # Filter the data for the specified product and year
    filtered_data = [item for item in data if item['software'] == product and int(item['date'].split('-')[0]) == year]

    # Initialize monthly sales list with 0 values for all 12 months
    monthly_sales = [0] * 12

    # Calculate monthly sales
    for item in filtered_data:
        month = int(item['date'].split('-')[1])
        quantity = float(item['amount'])
        monthly_sales[month - 1] += quantity

    return jsonify(monthly_sales)



if __name__ == '__main__':
    app.run()
from flask import Flask, jsonify, request
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# File path to store data (use a persistent path for deployment)
file_path = os.path.join(os.getcwd(), 'data.html')

# Helper function to read data from the HTML file
def read_data_from_html():
    data = []
    try:
        with open(file_path, 'r') as file:
            lines = file.readlines()
        for line in lines:
            if line.startswith('<tr>'):
                parts = line.split('</td>')
                if len(parts) >= 3:
                    id = int(parts[0].split('<td>')[1])
                    name = parts[1].split('<td>')[1].strip()
                    email = parts[2].split('<td>')[1].strip()
                    data.append({"id": id, "name": name, "email": email})
    except Exception as e:
        print(f"Error reading file: {e}")
    return data

# Helper function to save data to the HTML file
def save_data_to_html(data):
    try:
        with open(file_path, 'w') as file:
            file.write('<table><tr><th>ID</th><th>Name</th><th>Email</th></tr>\n')
            for item in data:
                file.write(f'<tr><td>{item["id"]}</td><td>{item["name"]}</td><td>{item["email"]}</td></tr>\n')
            file.write('</table>\n')
    except Exception as e:
        print(f"Error saving data: {e}")

# GET method to retrieve all data
@app.route('/api/data', methods=['GET'])
def get_data():
    data = read_data_from_html()
    return jsonify(data)

# POST method to add new data
@app.route('/api/data', methods=['POST'])
def add_data():
    new_data = request.get_json()
    data = read_data_from_html()
    new_id = max([item['id'] for item in data], default=0) + 1
    new_data['id'] = new_id
    data.append(new_data)
    save_data_to_html(data)
    return jsonify({"message": "Data added successfully!"}), 201

# PUT method to update existing data
@app.route('/api/data/<int:id>', methods=['PUT'])
def update_data(id):
    updated_data = request.get_json()
    data = read_data_from_html()
    for item in data:
        if item['id'] == id:
            item['name'] = updated_data['name']
            item['email'] = updated_data['email']
            save_data_to_html(data)
            return jsonify({"message": "Data updated successfully!"})
    return jsonify({"message": "Data not found"}), 404

# DELETE method to delete data
@app.route('/api/data/<int:id>', methods=['DELETE'])
def delete_data(id):
    data = read_data_from_html()
    for item in data:
        if item['id'] == id:
            data.remove(item)
            save_data_to_html(data)
            return jsonify({"message": "Data deleted successfully!"})
    return jsonify({"message": "Data not found"}), 404

if __name__ == '__main__':
    # Initialize an empty HTML file with a table if it doesn't exist
    if not os.path.exists(file_path):
        save_data_to_html([])

    app.run(debug=True, host='0.0.0.0', port=5000)

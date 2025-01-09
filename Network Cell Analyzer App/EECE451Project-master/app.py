from flask import Flask, render_template, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import socket
import threading
import json
import os

app = Flask(__name__)
db_file_path = os.path.join(app.root_path, 'test.db')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_file_path
db = SQLAlchemy(app)
app.app_context().push()

class NetworkData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=datetime.now())
    operator = db.Column(db.String(10), nullable=False)
    signal_power = db.Column(db.Text, nullable=False)
    snr = db.Column(db.Integer)
    network_type = db.Column(db.Text, nullable=False)
    frequency_band = db.Column(db.Text)
    cell_id = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return self.cell_id

@app.route('/')
def index():
    return render_template('index.html')
 
def handle_client(client_socket):
    while True:
        data = client_socket.recv(1024).decode()
        print('----- 1 data received ---')
        if not data:
            break

        try:
            data_dict = json.loads(data)

            operator = data_dict.get('operator')
            signal_power = data_dict.get('signal_power')
            snr = int(data_dict.get('snr'))
            network_type = data_dict.get('network_type')
            frequency_band = data_dict.get('frequency_band')
            cell_id = data_dict.get('cell_id')
            date1 = data_dict.get('date_1')
            date2 = data_dict.get('date_2')
            print('----- 2 decoded successfully -----')
            new_network_data = NetworkData(operator=operator, signal_power=signal_power, snr=snr, network_type=network_type, frequency_band=frequency_band, cell_id=cell_id)
            with app.app_context():
                db.session.add(new_network_data)
                print('----- 3 added successfully -----')
                db.session.commit()
                print('----- 4 commited successfully -----')
            if date1!=None and date2!=None:
                statistics = calculate_statistics(date1, date2)
                statistics_json = json.dumps(statistics)
                client_socket.send(statistics_json.encode())
                print("----- 5 Sent Statistics ----")
        except json.JSONDecodeError:
            print("Error: Invalid Data")
        
        client_socket.send("Received".encode())

    print("Closing Connection")
    client_socket.close()


def calculate_statistics(start_date, end_date):
    with app.app_context():
        data = NetworkData.query.filter(NetworkData.date_created.between(start_date, end_date)).all()

        # Calculate statistics
        statistics = {}

        # Average connectivity time per operator
        operator_counts = {}
        for item in data:
            operator_counts[item.operator] = operator_counts.get(item.operator, 0) + 1
        
        operator_averages = {}
        for operator, count in operator_counts.items():
            operator_averages[operator] = round((count / len(data)) * 100, 2)
        statistics['average_connectivity_time_per_operator'] = operator_averages

        '''
        # Average connectivity time per network type
        network_type_counts = {}
        for item in data:
            network_type_counts[item.network_type] = network_type_counts.get(item.network_type, 0) + 1
        network_type_averages = {}
        for network_type, count in network_type_counts.items():
            network_type_averages[network_type] = round((count / len(data))*100, 2)
        statistics['average_connectivity_time_per_network_type'] = network_type_averages

        # Average Signal Power per network type
        signal_power_sums = {}
        for item in data:
            signal_power_sums[item.network_type] = signal_power_sums.get(item.network_type, 0) + int(item.signal_power)
        signal_power_averages={}
        for network_type, power_sum in signal_power_sums.items():
            signal_power_averages[network_type] = round((power_sum / count)*100, 2)
        statistics['average_signal_power_per_network_type'] = signal_power_averages
        '''

        # Create dictionaries to store counts and power sums per network type
        network_type_counts = {}
        signal_power_sums = {}
        snr_sums = {}

        # Iterate over data to populate network_type_counts and signal_power_sums
        for item in data:
            network_type = item.network_type
            count = network_type_counts.get(network_type, 0)
            network_type_counts[network_type] = count + 1

            signal_power = int(item.signal_power)
            power_sum = signal_power_sums.get(network_type, 0)
            signal_power_sums[network_type] = power_sum + signal_power

            snr = int(item.snr)
            snr_sum = snr_sums.get(network_type, 0)
            snr_sums[network_type] = snr_sum + snr

        # Calculate average connectivity time per network type
        average_connectivity_time_per_network_type = {}
        total_data_count = len(data)
        for network_type, count in network_type_counts.items():
            percentage = round((count / total_data_count) * 100, 2)
            average_connectivity_time_per_network_type[network_type] = percentage
        statistics['average_connectivity_time_per_network_type'] = average_connectivity_time_per_network_type

        # Calculate average signal power per network type
        average_signal_power_per_network_type = {}
        for network_type, power_sum in signal_power_sums.items():
            count = network_type_counts[network_type]
            average_power = round((power_sum / count), 2)
            average_signal_power_per_network_type[network_type] = average_power
        statistics['average_signal_power_per_network_type'] = average_signal_power_per_network_type


        # Average SNR or SINR per network type
        snr_averages={}
        for network_type, snr_sum in snr_sums.items():
            count = network_type_counts[network_type]
            average_snr = round((snr_sum / count), 2)
            snr_averages[network_type] = average_snr
        statistics['average_snr_per_network_type'] = snr_averages

        # Average Signal power per device
        device_signal_power = {}
        for item in data:
            device_signal_power[item.cell_id] = device_signal_power.get(item.cell_id, []) + [int(item.signal_power)]
        device_average_signal_power = {cell_id: sum(powers) / len(powers) for cell_id, powers in device_signal_power.items()}
        statistics['average_signal_power_per_device'] = device_average_signal_power
        return statistics

def socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('0.0.0.0', 8080))
    server_socket.listen(5)

    while True:
        client_socket, addr = server_socket.accept()
        client_thread = threading.Thread(target=handle_client, args=(client_socket,))
        client_thread.start()
        print("connected client")

if __name__ == "__main__":
    server_thread = threading.Thread(target=socket_server)
    server_thread.start()

    app.run(port=8000, debug=True)
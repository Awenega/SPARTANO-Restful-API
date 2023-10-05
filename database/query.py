import psycopg2
import json
from datetime import datetime, timezone
from model.order import Order

def load_credentials():
    try:
        with open('credentials.json', 'r') as f:
            credentials = json.load(f)
            return credentials
    except FileNotFoundError:
        print(f"File 'credentials.json not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON in credentials.json")
        return None

def get_ordini_database():
    orders = []
    data_inizio = ((datetime(2023,7,30).replace(hour=0, minute=0, second=0, microsecond=0)).astimezone(timezone.utc)).isoformat()
    data_fine = (datetime(2023,7,31).astimezone(timezone.utc)).isoformat()
    print(f'Getting orders from {data_inizio} to {data_fine}')

    credentials = load_credentials()
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM orders where purchase_date >= '{data_inizio}' and purchase_date < '{data_fine}'")
    ret = cur.fetchall()
    
    for order_db in ret:
        order = Order(order_db[0], order_db[1], order_db[2], order_db[3], order_db[4], order_db[5], order_db[6], order_db[7], order_db[8], order_db[9], order_db[10], order_db[11], order_db[12])
        orders.append(order)

    return orders
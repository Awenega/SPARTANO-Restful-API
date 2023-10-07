import psycopg2
import json
from datetime import datetime, timezone
from model.order import Order
from model.refund import Refund

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

# **ORDERS** #

def get_orders_database(from_date, to_date, asin):

    from_date = datetime.strptime(from_date, "%Y-%m-%d").astimezone(timezone.utc)
    to_date = datetime.now().astimezone(timezone.utc) if to_date is None else datetime.strptime(to_date, "%Y-%m-%d").astimezone(timezone.utc) 
    orders = []
    credentials = load_credentials()
    query_asin = f"and asin = '{asin}'" if asin else ""

    print(f'Getting orders from {from_date} to {to_date}')
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM orders where purchase_date >= '{from_date}' and purchase_date < '{to_date}' {query_asin}")
    ret = cur.fetchall()
    
    for order_db in ret:
        orderItem = {'asin': order_db[3], 'quantity': order_db[4], 'price': order_db[7]}
        order = Order(order_db[0], order_db[1], order_db[2], orderItem, order_db[5], order_db[6])
        orders.append(order)
    print(len(orders))
    return orders

def insert_orders_database(orders):
    print(f'Inserting {len(orders)} orders in database')
    dataInsertionTuples = []
    credentials = load_credentials()
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()

    insertion = 0
    for order in orders:
        for item in order.items:
            insertion = insertion + 1
            tmp = (order.order_id, order.merchant_id, order.purchase_date, item.asin,
                    item.quantity, order.sales_channel, order.status, item.price,  
                    item.comm_logistica, item.comm_venditore, item.costo_prodotto, item.iva, item.net)
            dataInsertionTuples.append(tmp)
    dataText = ','.join(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", row).decode("utf-8") for row in dataInsertionTuples)
    sqlTxt = """INSERT INTO orders VALUES {0} ON CONFLICT (order_id, asin) DO UPDATE SET 
                                            (merchant_id, purchase_date, quantity, sales_channel, status, price,
                                             comm_logistica, comm_venditore, costo_prodotto, iva, net) = 
                                            (EXCLUDED.merchant_id, EXCLUDED.purchase_date, EXCLUDED.quantity, EXCLUDED.sales_channel, 
                                            EXCLUDED.status, EXCLUDED.price, EXCLUDED.comm_logistica, EXCLUDED.comm_venditore,
                                            EXCLUDED.costo_prodotto, EXCLUDED.iva, EXCLUDED.net);""".format(dataText)
    try:
        cur.execute(sqlTxt)
        conn.commit()
        msg = f"Database updated with {str(insertion)} insertions"
        print(msg)
        return {'msg': msg}, 200
    except(Exception, psycopg2.Error) as err:
        return {'msg': "Error while interacting with PostgreSQL...\n",'err': str(err)}, 400
    
def delete_orders_database(order_ids):
    print(f'Deleting {len(order_ids)} orders in database')
    credentials = load_credentials()
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()

    placeholders = ",".join(["%s"] * len(order_ids))
    delete_query = f"DELETE FROM orders WHERE order_id IN ({placeholders})"
    try:
        cur.execute(delete_query, tuple(order_ids))
        conn.commit()
        return {'msg': f"Database updated with {len(order_ids)} deletetions"}, 200
    except(Exception, psycopg2.Error) as err:
        return {'msg': "Error while interacting with PostgreSQL...\n",'err': str(err)}, 400

def delete_all_orders_database():
    print(f'Deleting all orders in database')
    credentials = load_credentials()
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()

    delete_query = f"DELETE FROM orders"
    try:
        cur.execute(delete_query)
        conn.commit()
        return {'msg': f"Database updated"}, 200
    except(Exception, psycopg2.Error) as err:
        return {'msg': "Error while interacting with PostgreSQL...\n",'err': str(err)}, 400
    
# **REFUNDS** #

def get_refunds_database(from_date, to_date, asin):

    from_date = datetime.strptime(from_date, "%Y-%m-%d").astimezone(timezone.utc)
    to_date = datetime.now().astimezone(timezone.utc) if to_date is None else datetime.strptime(to_date, "%Y-%m-%d").astimezone(timezone.utc) 
    refunds = []
    credentials = load_credentials()
    query_asin = f"and asin = '{asin}'" if asin else ""

    print(f'Getting refunds from {from_date} to {to_date}')
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM refunds where purchase_date >= '{from_date}' and purchase_date < '{to_date}' {query_asin}")
    ret = cur.fetchall()
    
    for refund_db in ret:
        refund = Refund(refund_db[0], refund_db[1], refund_db[2], refund_db[3], refund_db[4], refund_db[5], refund_db[6], refund_db[7])
        refunds.append(refund)
    print(len(refunds))
    return refunds

def insert_refunds_database(refunds):
    print(f'Inserting {len(refunds)} orders in database')
    dataInsertionTuples = []
    credentials = load_credentials()
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()

    for refund in refunds:
        tmp = (refund.order_id, refund.purchase_date, refund.asin, refund.quantity, 
               refund.sales_channel, refund.comm_venditore, refund.comm_refund, refund.loss)
        dataInsertionTuples.append(tmp)
    dataText = ','.join(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s)", row).decode("utf-8") for row in dataInsertionTuples)
    sqlTxt = """INSERT INTO refunds VALUES {0} ON CONFLICT (order_id, asin) DO UPDATE SET 
                                            (purchase_date, quantity, sales_channel, comm_venditore,comm_refund, loss) = 
                                            (EXCLUDED.purchase_date, EXCLUDED.quantity, EXCLUDED.sales_channel, 
                                            EXCLUDED.comm_venditore, EXCLUDED.comm_refund, EXCLUDED.loss);""".format(dataText)
    try:
        cur.execute(sqlTxt)
        conn.commit()
        return {'msg': f"Database updated with {len(refunds)} insertions"}, 200
    except(Exception, psycopg2.Error) as err:
        return {'msg': "Error while interacting with PostgreSQL...\n",'err': str(err)}, 400

def delete_refunds_database(order_ids):
    print(f'Deleting {len(order_ids)} refunds in database')
    credentials = load_credentials()
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()

    placeholders = ",".join(["%s"] * len(order_ids))
    delete_query = f"DELETE FROM refunds WHERE order_id IN ({placeholders})"
    try:
        cur.execute(delete_query, tuple(order_ids))
        conn.commit()
        return {'msg': f"Database updated with {len(order_ids)} deletetions"}, 200
    except(Exception, psycopg2.Error) as err:
        return {'msg': "Error while interacting with PostgreSQL...\n",'err': str(err)}, 400

def delete_all_refunds_database():
    print(f'Deleting all refunds in database')
    credentials = load_credentials()
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()

    delete_query = f"DELETE FROM refunds"
    try:
        cur.execute(delete_query)
        conn.commit()
        return {'msg': f"Database updated"}, 200
    except(Exception, psycopg2.Error) as err:
        return {'msg': "Error while interacting with PostgreSQL...\n",'err': str(err)}, 400

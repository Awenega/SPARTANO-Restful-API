import psycopg2
import json
from datetime import datetime, timezone
from model.order import Order
from model.refund import Refund
from model.setting import Setting

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
    query_asin = f"and orders.asin = '{asin}'" if asin else ""

    print(f'Getting orders from {from_date} to {to_date}')
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()
    query = f'''
        SELECT orders.order_id, orders.merchant_id, (orders.purchase_date AT time zone 'utc' AT time zone 'cest')::DATE, orders.asin, orders.quantity, orders.sales_channel, orders.status, 
        orders.price, settings.costo_prodotto, settings.comm_logistica, settings.comm_venditore, settings.iva,
        Coalesce (refunds.quantity, 0) as quantity_refund, Coalesce( refunds.comm_venditore, 0.00) as comm_venditore_refund, 
        Coalesce (refunds.comm_refund, 0.00) as comm_refund, 
        CASE
            WHEN refunds.quantity IS NULL THEN sum ((price/iva) - (orders.quantity*(costo_prodotto + comm_logistica)) - (price*settings.comm_venditore))
            WHEN refunds.quantity > 0 THEN sum(comm_refund - (refunds.quantity*settings.comm_logistica))
        END 
        as net
        FROM orders
        JOIN settings ON orders.asin = settings.asin AND  
            orders.sales_channel = settings.sales_channel AND 
            orders.purchase_date AT time zone 'utc' AT time zone 'cest'
            BETWEEN settings.from_date AND settings.to_date
        LEFT JOIN refunds ON orders.order_id = refunds.order_id AND orders.asin = refunds.asin
        WHERE orders.quantity <> 0 AND orders.sales_channel <> 'Cancelled' AND
        orders.purchase_date BETWEEN '{from_date}' AND '{to_date}' {query_asin}
        GROUP BY orders.order_id, orders.merchant_id, orders.purchase_date, orders.asin, orders.quantity, orders.sales_channel, orders.status, 
        orders.price, settings.costo_prodotto, settings.comm_logistica, settings.comm_venditore, settings.iva, refunds.quantity, comm_venditore_refund, comm_refund
    '''
    cur.execute(query)
    ret = cur.fetchall()
    
    for order_db in ret:
        orderItem = {
            'asin': order_db[3], 'quantity': order_db[4], 'price': order_db[7], 
            'costo_prodotto': order_db[8], 'comm_logistica': order_db[9], 
            'comm_venditore': order_db[10], 'iva': order_db[11], 'quantity_refund': order_db[12],
            'comm_venditore_refund': order_db[13], 'comm_refund': order_db[14], 'net': order_db[15]
            }
        order = Order(order_db[0], order_db[1], order_db[2], order_db[5], order_db[6], orderItem)
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
                    item.quantity, order.sales_channel, order.status, item.price
                    )
            dataInsertionTuples.append(tmp)
    dataText = ','.join(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s)", row).decode("utf-8") for row in dataInsertionTuples)
    sqlTxt = """INSERT INTO orders VALUES {0} ON CONFLICT (order_id, asin) DO UPDATE SET 
                                            (merchant_id, purchase_date, quantity, sales_channel, status, price) = 
                                            (EXCLUDED.merchant_id, EXCLUDED.purchase_date, EXCLUDED.quantity, EXCLUDED.sales_channel, 
                                            EXCLUDED.status, EXCLUDED.price);""".format(dataText)
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
        return {'msg': f"Database updated with {str(len(order_ids))} deletetions"}, 200
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
    query_asin = f"and refunds.asin = '{asin}'" if asin else ""

    print(f'Getting refunds from {from_date} to {to_date}')
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()
    query = f'''
            SELECT refunds.order_id, orders.purchase_date, refunds.asin, refunds.quantity, refunds.sales_channel, 
                    orders.price, settings.costo_prodotto, settings.comm_logistica, refunds.comm_venditore, refunds.comm_refund
            FROM refunds
            JOIN settings ON refunds.asin = settings.asin AND  
                refunds.sales_channel = settings.sales_channel AND 
                refunds.purchase_date AT time zone 'utc' AT time zone 'cest'
                BETWEEN settings.from_date AND settings.to_date
            JOIN orders ON refunds.order_id = orders.order_id AND
                refunds.asin = orders.asin
            WHERE orders.purchase_date BETWEEN '{from_date}' AND '{to_date} {query_asin}'
            '''
    cur.execute(query)
    ret = cur.fetchall()
    
    for refund_db in ret:
        refund = Refund(refund_db[0], refund_db[1], refund_db[2], refund_db[3], refund_db[4], refund_db[8], refund_db[9], refund_db[5], refund_db[6], refund_db[7])
        refunds.append(refund)
    print(len(refunds))
    return refunds

def insert_refunds_database(refunds):
    print(f'Inserting {len(refunds)} refunds in database')
    dataInsertionTuples = []
    credentials = load_credentials()
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()

    for refund in refunds:
        tmp = (refund.order_id, refund.purchase_date, refund.asin, refund.quantity, 
               refund.sales_channel, refund.comm_venditore, refund.comm_refund)
        dataInsertionTuples.append(tmp)
    dataText = ','.join(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s)", row).decode("utf-8") for row in dataInsertionTuples)
    sqlTxt = """INSERT INTO refunds VALUES {0} ON CONFLICT (order_id, asin) DO UPDATE SET 
                                            (purchase_date, quantity, sales_channel, comm_venditore, comm_refund) = 
                                            (EXCLUDED.purchase_date, EXCLUDED.quantity, EXCLUDED.sales_channel, 
                                            EXCLUDED.comm_venditore, EXCLUDED.comm_refund);""".format(dataText)
    try:
        cur.execute(sqlTxt)
        conn.commit()
        return {'msg': f"Database updated with {str(len(refunds))} insertions"}, 200
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
        return {'msg': f"Database updated with {str(len(order_ids))} deletetions"}, 200
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

# **SETTINGS** #

def get_settings_database(from_date, to_date, asin, sales_channel):

    settings = []
    credentials = load_credentials()
    sales_channel_query = f"and sales_channel = '{sales_channel}'" if sales_channel is not None else ''

    print(f'Getting settings from {from_date} to {to_date}')
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM settings where from_date >= '{from_date}' and to_date <= '{to_date}' and asin = '{asin}' {sales_channel_query}")
    ret = cur.fetchall()
    
    for setting_db in ret:
        setting = Setting(setting_db[0], setting_db[1], setting_db[2], setting_db[3], setting_db[4], setting_db[5], setting_db[6], setting_db[7])
        settings.append(setting)
    print(len(settings))
    return settings

def insert_settings_database(settings):
    print(f'Inserting {len(settings)} settings in database')
    dataInsertionTuples = []
    credentials = load_credentials()
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()

    for setting in settings:
        tmp = (setting.asin, setting.sales_channel, setting.from_date, setting.to_date,
                setting.costo_prodotto, setting.comm_logistica, setting.comm_venditore, setting.iva)
        dataInsertionTuples.append(tmp)
    dataText = ','.join(cur.mogrify("(%s, %s, %s, %s, %s, %s, %s, %s)", row).decode("utf-8") for row in dataInsertionTuples)
    sqlTxt = """INSERT INTO settings VALUES {0} ON CONFLICT (asin, sales_channel, from_date) DO UPDATE SET 
                                            (to_date, costo_prodotto, comm_logistica, comm_venditore, iva) = 
                                            (EXCLUDED.to_date, EXCLUDED.costo_prodotto, EXCLUDED.comm_logistica, 
                                            EXCLUDED.comm_venditore, EXCLUDED.iva);""".format(dataText)
    try:
        cur.execute(sqlTxt)
        conn.commit()
        return {'msg': f"Database updated with {str(len(settings))} insertions"}, 200
    except(Exception, psycopg2.Error) as err:
        return {'msg': "Error while interacting with PostgreSQL...\n",'err': str(err)}, 400

def delete_settings_database(asin, sales_channel, from_date):
    print(f'Deleting {asin, sales_channel, from_date} setting in database')
    credentials = load_credentials()
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()
    
    delete_query = f"DELETE FROM settings WHERE (asin, sales_channel, from_date) IN (SELECT asin, sales_channel, from_date From settings where asin = '{asin}' and sales_channel = '{sales_channel}' and from_date = '{from_date}')"
    try:
        cur.execute(delete_query)
        conn.commit()
        return {'msg': f"Deleted from database record {asin, sales_channel, from_date} in setting"}, 200
    except(Exception, psycopg2.Error) as err:
        return {'msg': "Error while interacting with PostgreSQL...\n",'err': str(err)}, 400

def delete_all_settings_database():
    print(f'Deleting all settings in database')
    credentials = load_credentials()
    conn = psycopg2.connect(f"dbname={credentials.get('dbname')} user={credentials.get('user')} host='{credentials.get('host')}' password='{credentials.get('password')}'")
    cur = conn.cursor()

    delete_query = f"DELETE FROM settings"
    try:
        cur.execute(delete_query)
        conn.commit()
        return {'msg': f"Database updated"}, 200
    except(Exception, psycopg2.Error) as err:
        return {'msg': "Error while interacting with PostgreSQL...\n",'err': str(err)}, 400

from marshmallow import Schema, fields, post_load, EXCLUDE, ValidationError

class Item(object):
    def __init__(self, orderItem):
        self.asin = orderItem['asin']
        self.quantity = orderItem['quantity']
        self.price = orderItem['price']
        if 'net' in orderItem:
            self.costo_prodotto = orderItem['costo_prodotto']
            self.comm_logistica = orderItem['comm_logistica']
            self.comm_venditore = orderItem['comm_venditore']
            self.iva = orderItem['iva']
            self.quantity_refund = orderItem['quantity_refund']
            self.comm_venditore_refund = orderItem['comm_venditore_refund']
            self.comm_refund = orderItem['comm_refund']
            self.net = orderItem['net']

class Order(object):
    def __init__(self, order_id, merchant_id, purchase_date, sales_channel, status, orderItem):
        self.order_id = order_id
        self.merchant_id = merchant_id
        self.purchase_date = purchase_date
        self.sales_channel = sales_channel
        self.status = status
        self.items = []
        if isinstance(orderItem, dict):
            item = Item(orderItem)
            self.items.append(item)
        else:
            for elem in orderItem:
                item = Item(elem)
                self.items.append(item)
        
    def __repr__(self):
        return '<Order(order_id={self.order_id!r})>'.format(self=self)

class OrderItemSchema(fields.Field):
    def _get_price(self, value):
            
        if 'ItemPrice' in value:
            itemPrice = value['ItemPrice']['Component']
        
            if isinstance(itemPrice, dict):
                return itemPrice['Amount']['#text']
            elif isinstance(itemPrice, list):
                for elem in itemPrice:
                    if elem['Type'] == 'Principal':
                        return elem['Amount']['#text']
            else:
                raise ValidationError('Field should be dict or list')
            
        return '0.0'
        
    def _get_discount(self, value):
        if "Promotion" in value:
            if 'ItemPromotionDiscount' in value['Promotion']:
                return value['Promotion']['ItemPromotionDiscount']
        return '0.0'

    def _deserialize(self, value, attr, data, **kwargs):
        if isinstance(value, dict):
            asin = value['ASIN']
            quantity = value['Quantity']
            price_original = self._get_price(value)
            discount = self._get_discount(value)
            price = str(round(float(price_original) - float(discount), 2))
            return {'asin': asin, 'quantity': quantity, 'price': price}
        elif isinstance(value, list):
            arr = []
            for elem in value:
                asin = elem['ASIN']
                quantity = elem['Quantity']
                price_original = self._get_price(elem)
                discount = self._get_discount(value)
                price = str(round(float(price_original) - float(discount), 2))
                arr.append({'asin': asin, 'quantity': quantity, 'price': price})
            return arr
        else:
            raise ValidationError('Field should be dict or list')

class SingleOrderSchema(Schema):
    AmazonOrderID = fields.String()
    MerchantOrderID = fields.String()
    PurchaseDate = fields.String()
    OrderItem = OrderItemSchema()
    OrderStatus = fields.String()
    SalesChannel = fields.String()

class OrderSchema(Schema):
    Order = fields.Nested(SingleOrderSchema, unknown=EXCLUDE)
    @post_load
    def create_order(self, data, **kwargs):
        order_info = data.get('Order')
        return Order(
            order_info['AmazonOrderID'], order_info['MerchantOrderID'], order_info['PurchaseDate'],
            order_info['SalesChannel'], order_info['OrderStatus'], order_info['OrderItem']
            )

class ItemDbSchema(Schema):
    asin = fields.String()
    quantity = fields.Integer()
    price = fields.Float()
    costo_prodotto = fields.Float()
    comm_logistica = fields.Float()
    comm_venditore = fields.Float()
    iva = fields.Float()
    quantity_refund = fields.Integer()
    comm_venditore_refund = fields.Float()
    comm_refund = fields.Float()
    net = fields.Float()

class OrderDbSchema(Schema):
    order_id = fields.String()
    merchant_id = fields.String()
    purchase_date = fields.Date()
    sales_channel = fields.String()
    status = fields.String()
    items = fields.Nested(ItemDbSchema, many=True)
    
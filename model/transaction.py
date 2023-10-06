from marshmallow import Schema, fields

class Transaction(object):
    def __init__(self, order_id, purchase_date, asin, quantity, sales_channel, type):
        self.order_id = order_id
        self.purchase_date = purchase_date
        self.asin = asin
        self.quantity = quantity
        self.sales_channel = sales_channel
        self.type = type


    def __repr__(self):
        return '<Transaction(order_id={self.order_id!r})>'.format(self=self)


class TransactionSchema(Schema):
    order_id = fields.Str()
    purchase_date = fields.Str()
    asin = fields.Str()
    quantity = fields.Number()
    sales_channel = fields.Str()
    
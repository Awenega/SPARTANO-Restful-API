import datetime as dt

from marshmallow import Schema, fields

class Transaction(object):
    def __init__(self, order_id, data_acquisto, asin, quantity, sales_channel, type):
        self.order_id = order_id
        self.data_acquisto = data_acquisto
        self.asin = asin
        self.quantity = quantity
        self.sales_channel = sales_channel
        self.type = type


    def __repr__(self):
        return '<Transaction(order_id={self.order_id!r})>'.format(self=self)


class TransactionSchema(Schema):
    order_id = fields.Str()
    data_acquisto = fields.Date()
    asin = fields.Str()
    quantity = fields.Number()
    sales_channel = fields.Str()
    
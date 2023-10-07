from marshmallow import post_load, fields, Schema

class Refund(object):
    def __init__(self, order_id, purchase_date, asin, quantity, sales_channel, comm_venditore, comm_refund, loss):
        super(Refund, self).__init__(order_id, purchase_date, asin, quantity, sales_channel, '')
        self.comm_venditore = comm_venditore
        self.comm_refund = comm_refund
        self.loss = loss

    def __repr__(self):
        return '<Refund(order_id={self.order_id!r})>'.format(self=self)

class RefundSchema(Schema):
    comm_venditore = fields.Float()
    comm_refund = fields.Float()
    loss = fields.Float()
    @post_load
    def make_refund(self, data, **kwargs):
        return Refund(**data)
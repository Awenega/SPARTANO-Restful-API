from marshmallow import post_load, fields, Schema

class Refund(object):
    def __init__(self, order_id, purchase_date, asin, quantity, sales_channel, comm_venditore, comm_refund):
        self.order_id = order_id
        self.purchase_date = purchase_date
        self.sales_channel = sales_channel
        self.asin = asin
        self.quantity =  quantity
        self.comm_venditore = comm_venditore
        self.comm_refund = comm_refund

    def __repr__(self):
        return '<Refund(order_id={self.order_id!r})>'.format(self=self)

class SingleRefundSchema(Schema):
    order_id = fields.String()
    purchase_date = fields.String()
    sales_channel = fields.String()
    asin = fields.String()
    quantity =  fields.Integer()
    comm_venditore = fields.Float()
    comm_refund = fields.Float()

class RefundSchema(Schema):
    Refund = fields.Nested(SingleRefundSchema)
    @post_load
    def make_refund(self, data, **kwargs):
        refund_info = data.get('Refund')
        return Refund(
            refund_info['order_id'], refund_info['purchase_date'], refund_info['asin'], refund_info['quantity'],
            refund_info['sales_channel'], refund_info['comm_venditore'], refund_info['comm_refund']
        )

class RefundDbSchema(Schema):
    order_id = fields.String()
    purchase_date = fields.DateTime()
    asin = fields.String()
    quantity =  fields.Integer()
    sales_channel = fields.String()
    comm_venditore = fields.Float()
    comm_refund = fields.Float()
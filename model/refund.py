from marshmallow import post_load, fields
from .transaction import Transaction, TransactionSchema
from .transaction_type import TransactionType


class Refund(Transaction):
    def __init__(self, order_id, purchase_date, asin, quantity, sales_channel, comm_venditore, comm_refund, loss):
        super(Refund, self).__init__(order_id, purchase_date, asin, quantity, sales_channel, TransactionType.REFUND)
        self.comm_venditore = comm_venditore
        self.comm_refund = comm_refund
        self.loss = loss

    def __repr__(self):
        return '<Refund(order_id={self.order_id!r})>'.format(self=self)


class RefundSchema(TransactionSchema):
    comm_segnalazione = fields.Float()
    comm_refund = fields.Float()
    loss = fields.Float()
    @post_load
    def make_refund(self, data, **kwargs):
        return Refund(**data)
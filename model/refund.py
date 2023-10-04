from marshmallow import post_load, fields

from .transaction import Transaction, TransactionSchema
from .transaction_type import TransactionType


class Refund(Transaction):
    def __init__(self, order_id, data_acquisto, asin, quantity, sales_channel, comm_segnalazione, comm_rimborso):
        super(Refund, self).__init__(order_id, data_acquisto, asin, quantity, sales_channel, TransactionType.REFUND)
        self.comm_segnalazione = comm_segnalazione
        self.comm_rimborso = comm_rimborso

    def __repr__(self):
        return '<Refund(order_id={self.order_id!r})>'.format(self=self)


class RefundSchema(TransactionSchema):
    comm_segnalazione = fields.Float()
    comm_rimborso = fields.Float()
    @post_load
    def make_refund(self, data, **kwargs):
        return Refund(**data)
from marshmallow import fields, post_load

from .transaction import Transaction, TransactionSchema
from .transaction_type import TransactionType


class Order(Transaction):
    def __init__(self, order_id, data_acquisto, asin, quantity, sales_channel, status, prezzo, comm_logistica, comm_venditore, costo_prodotto, iva, utile):
        super(Order, self).__init__(order_id, data_acquisto, asin, quantity, sales_channel, TransactionType.ORDER)
        self.status = status
        self.prezzo = prezzo
        self.comm_logistica = comm_logistica
        self.comm_venditore = comm_venditore
        self.costo_prodotto = costo_prodotto
        self.iva = iva
        self.utile = utile

    def __repr__(self):
        return '<Order(order_id={self.order_id!r})>'.format(self=self)


class OrderSchema(TransactionSchema):
    status = fields.String()
    prezzo = fields.Float()
    comm_logistica = fields.Float()
    comm_venditore = fields.Float()
    costo_prodotto = fields.Float()
    iva = fields.Float()
    utile = fields.Float()
    @post_load
    def make_order(self, data, **kwargs):
        return Order(**data)
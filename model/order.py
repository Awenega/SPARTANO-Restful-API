from marshmallow import fields, post_load

from .transaction import Transaction, TransactionSchema
from .transaction_type import TransactionType


class Order(Transaction):
    def __init__(self, order_id, merchant_id, purchase_date, asin, quantity, sales_channel, status, price, comm_logistica, comm_venditore, costo_prodotto, iva, net):
        super(Order, self).__init__(order_id, purchase_date, asin, quantity, sales_channel, TransactionType.ORDER)
        self.merchant_id = merchant_id
        self.status = status
        self.price = price
        self.comm_logistica = comm_logistica
        self.comm_venditore = comm_venditore
        self.costo_prodotto = costo_prodotto
        self.iva = iva
        self.net = net

    def __repr__(self):
        return '<Order(order_id={self.order_id!r})>'.format(self=self)


class OrderSchema(TransactionSchema):
    merchant_id = fields.String()
    status = fields.String()
    price = fields.Float()
    comm_logistica = fields.Float()
    comm_venditore = fields.Float()
    costo_prodotto = fields.Float()
    iva = fields.Float()
    net = fields.Float()
    @post_load
    def make_order(self, data, **kwargs):
        return Order(**data)
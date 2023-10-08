from marshmallow import post_load, fields, Schema

class Setting(object):
    def __init__(self, asin, sales_channel, from_date, to_date, costo_prodotto, comm_logistica, comm_venditore, iva):
        self.asin = asin
        self.sales_channel = sales_channel
        self.from_date =  from_date
        self.to_date =  to_date
        self.costo_prodotto =  costo_prodotto
        self.comm_logistica = comm_logistica
        self.comm_venditore = comm_venditore
        self.iva = iva

    def __repr__(self):
        return '<Settings(from_date={self.from_date!r})>'.format(self=self)

class SettingSchema(Schema):
    asin = fields.String()
    sales_channel = fields.String()
    from_date = fields.String()
    to_date = fields.String()
    costo_prodotto = fields.Float()
    comm_logistica = fields.Float()
    comm_venditore = fields.Float()
    iva =  fields.Float()
    @post_load
    def make_setting(self, data, **kwargs):
        return Setting(**data)

class SettingDbSchema(Schema):
    asin = fields.String()
    sales_channel = fields.String()
    from_date = fields.Date()
    to_date = fields.Date()
    costo_prodotto = fields.Float()
    comm_logistica = fields.Float()
    comm_venditore = fields.Float()
    iva =  fields.Float()
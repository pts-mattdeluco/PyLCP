from pylcp.crud import base as crud


class PaymentAuth(crud.LCPCrud):
    def create(self, path, payload):
        return super(PaymentAuth, self).create(path, payload)


class PaymentCapture(crud.LCPCrud):
    def create(self, path):
        return super(PaymentCapture, self).create(path, '{}')

import crud


class PaymentAuth(crud.LCP):
    def create(self, url, payload):
        return super(PaymentAuth, self).create(url, payload)


class PaymentCapture(crud.LCP):
    def create(self, url):
        return super(PaymentCapture, self).create(url, {})

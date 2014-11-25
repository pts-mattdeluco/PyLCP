import collections

import crud


class Offer(crud.LCP):
    pass


class OfferSet(crud.LCP):
    """ Create an offerset. Any kwargs will be added as top-level parameters in the request payload.
    """
    def create(self, url, offer_types, session, user_details, recipient_details=None, **kwargs):
        payload = self._create_payload(offer_types, session, user_details, recipient_details, **kwargs)

        return super(OfferSet, self).create(url, payload)

    def _create_payload(self, offer_types, session, user_details, recipient_details=None, **kwargs):
        payload = {'offerTypes': offer_types,
                   'session': session,
                   'user': user_details}

        if recipient_details is not None:
            payload['recipient'] = recipient_details

        payload.update(kwargs)

        return payload

Session = collections.namedtuple('Session', 'channel referralCode clientIpAddress clientUserAgent')

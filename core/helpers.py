import requests, json

_PAYUDATA = {
    "pos_id": 388753,
    "second_key": "dbdf21a26d8da15ba5338ed5bd05bbff",
    "oauth_id": 388753,
    "oauth_secret": "b34d4e8accd4a3f36caadd009e1bb34e"
}


class PayUHelper:
    snd = 'https://secure.snd.payu.com'
    prod= 'https://secure.payu.com'
    in_sandbox = True
    _access_token = None
    def get_auth(self, force=False):
        if not PayUHelper._access_token or force:
            host = PayUHelper.snd if PayUHelper.in_sandbox else PayUHelper.prod
            data = {
                'grant_type':'client_credentials',
                'client_id':_PAYUDATA['oauth_id'],
                'client_secret':_PAYUDATA['oauth_secret'],
            }
            resp = requests.post(host+'/pl/standard/user/oauth/authorize',data)
            PayUHelper._access_token = resp.json()['access_token']

    def _rest_json_post(self, fnc, data):
        self.get_auth()
        host = PayUHelper.snd if PayUHelper.in_sandbox else PayUHelper.prod
        headers = {
            'Content-Type':'application/json',
            'Authorization':'Bearer {}'.format(PayUHelper._access_token)
        }
        return requests.post(host+fnc,json=data,headers=headers, allow_redirects=False)

    def _rest_json_get(self, fnc):
        self.get_auth()
        host = PayUHelper.snd if PayUHelper.in_sandbox else PayUHelper.prod
        headers = {
            'Content-Type':'application/json',
            'Authorization':'Bearer {}'.format(PayUHelper._access_token)
        }
        return requests.get(host+fnc,headers=headers, allow_redirects=False)

    def newOrder(self, internal_id, buyer, items, description):
        fnc = '/api/v2_1/orders'
        data = {
            "notifyUrl": "https://xxx.bcelmer.tk/payu-notification",
            "customerIp": "51.77.245.145",# Fake IP
            "extOrderId": internal_id,
            "continueUrl": 'http://127.0.0.1:8000/order/{}'.format(internal_id),
            "merchantPosId": _PAYUDATA['pos_id'],
            "description": description,
            "currencyCode": "PLN",
            "totalAmount": round(sum([p.product.price*p.quantity for p in items])*100),
            "buyer": {
                "email": buyer.email,
                "firstName": buyer.first_name if len(buyer.first_name) else 'Nie podano',
                "lastName": buyer.last_name if len(buyer.last_name) else 'Nie podano',
                "language": "pl"
            },
            "settings":{
                "invoiceDisabled":"true"
            },
            "products": [
                {
                    "name": p.product.name,
                    "unitPrice": round(p.product.price*100*p.quantity),
                    "quantity": p.quantity
                } for p in items
            ]
        }
        return self._rest_json_post(fnc,data)

    def orderData(self,order_id):
        fnc = '/api/v2_1/orders/{}'.format(order_id)
        return self._rest_json_get(fnc)

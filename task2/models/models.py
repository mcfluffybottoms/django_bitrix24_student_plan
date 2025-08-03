import hashlib
import os

from django.core import signing
from django.core.signing import Signer
import urllib.parse


class Product:
    signer = Signer()

    @classmethod
    def get_product_by_id(cls, but, id):
        try:
            result = but.call_api_method("crm.product.get",
                                         {
                                             "id": id,
                                         }
                                         )
            if result.get('error'):
                return None;
            return result['result']
        except:
            return None

    @classmethod
    def get_available_ids(cls, but):
        rawIds = but.call_api_method("crm.product.list", {
            "select": [
                'id',
            ],
        })
        Ids = []
        if rawIds.get("result"):
            Ids = [BlockIds["ID"] for BlockIds in rawIds["result"]]
        print(Ids)
        return Ids

    @classmethod
    def generate_token(cls, but, id):
        product = cls.get_product_by_id(but, id);
        if not product:
            return None
        rawBlockIds = but.call_api_method("catalog.catalog.list", {
            "select": [
                "iblockId"
            ]
        })
        if rawBlockIds.get("result"):
            possibleiblockIds = [BlockIds["iblockId"] for BlockIds in rawBlockIds["result"]["catalogs"]]
        possibleImages = []
        rawImagesIds = but.call_api_method("catalog.productImage.list", {
            "productId": id,
            "select": [
                'detailUrl',
            ],
        })
        if rawImagesIds.get("result"):
            possibleImages = [ImagesId["detailUrl"] for ImagesId in rawImagesIds["result"]["productImages"]]
        img_url = possibleImages[0] if len(possibleImages) > 0 else None
        url = signing.dumps({
            "NAME": product['NAME'],
            "DATE_CREATE": product['DATE_CREATE'],
            "IMG": "https://" + urllib.parse.quote(img_url[8:]) if img_url else None,
        })
        return url

    @classmethod
    def get_site_from_link(cls, token):
        if not token:
            return None
        product = signing.loads(token)

        return product

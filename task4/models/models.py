import requests

from settings import APP_SETTINGS

ADDRESS_FIELDS = [
    "ENTITY_ID", "ADDRESS_1",
    "CITY"
]

COMPANY_FIELDS = [
    "ID", "TITLE",
    "LOGO", "COMPANY_TYPE"
]

class Map:
    @classmethod
    def get_full_address(cls, address):
        address_list = []
        for field in ADDRESS_FIELDS:
            if address.get(field) and field != "ENTITY_ID":
                address_list.append(address.get(field))
        return ", ".join(address_list)
        
    @classmethod
    def form_enquiry(cls, address, api_key):
        base_url = "https://geocode-maps.yandex.ru/1.x/"
        params = {
            'apikey': api_key,
            'geocode': address,
            'lang': "ru_RU",
            'format': 'json'
        }
        try:
            response = requests.get(base_url, params=params)
            response.raise_for_status()
            data = response.json()
            positions = []
            for member in data['response']['GeoObjectCollection']['featureMember']:
                positions.append(member['GeoObject']['Point']['pos'].split(" "))
            return positions
        except requests.exceptions.RequestException as e:
            print(f"Geocoding error: {e}")
            return None
        
    @classmethod
    def get_map_locations(cls, but, api_key):
        companyList = but.call_api_method("crm.company.list",
        {
            "select": COMPANY_FIELDS
        })
        rawAddressList = but.call_api_method("crm.address.list",
        {
            "select": ADDRESS_FIELDS
        })
        if not companyList.get('result') or not rawAddressList.get('result'):
            return None
        addressList = {}
        for address in rawAddressList.get("result"):
            temp_dict = {}
            temp_id = ''
            for field in ADDRESS_FIELDS:
                if field == 'ENTITY_ID':
                    temp_id = address[field]
                else:
                    temp_dict[field] = address[field]
            addressList[str(temp_id)] = temp_dict
        
        print(but.call_api_method("crm.company.fields"))
        company_output_data = companyList.get('result')
        for company in company_output_data:
            img_name = ''
            if company.get('LOGO') and company.get('LOGO').get('downloadUrl'):
                img_name = "".join(["https://", APP_SETTINGS.portal_domain, company['LOGO']['downloadUrl']])
            print(img_name)
            
            address = cls.get_full_address(addressList[company['ID']])
            coordinates = cls.form_enquiry(address, api_key)
            company['ADDRESS'] = address
            company['COORDINATES'] = coordinates
            company['LOGO'] = img_name
            print(company["COMPANY_TYPE"])
        return company_output_data

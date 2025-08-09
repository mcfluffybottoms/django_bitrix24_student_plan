import os
import traceback
from urllib.parse import urlparse
import pandas as pd
from os.path import splitext

import settings
from integration_utils.bitrix24.functions.batch_api_call import BatchResultDict


def check_if_email(s):
    email_parts = s.split("@")
    if len(email_parts) != 2 or not email_parts[0] or not email_parts[1]:
        return None
    right_part = email_parts[1].split(".")
    if len(right_part) != 2 or not right_part[0] or not right_part[1]:
        return None
    return s.strip()


def iter_BatchResultDict(dict: BatchResultDict):  # type: () -> Iterable[Tuple[str, Any]]
    for name, res in dict.items():
        yield name, res.get('result')


class BaseContactLoader:
    REQUIRED_FIELDS = [
        'NAME', 'LAST_NAME', "PHONE",
        'EMAIL', 'COMPANY_ID'
    ]

    def __init__(self, file=None):
        self.file = file
        self.df = None

    def set_lead_row(self):
        if self.df is None:
            return None
        if len(self.df.columns) != len(self.REQUIRED_FIELDS):
            raise ValueError(f"В таблице неверное количество столбцов - должно быть {len(self.REQUIRED_FIELDS)}.")
        self.df.columns = self.REQUIRED_FIELDS

    def import_to_bitrix(self, but, max_data=50):
        if self.df is None:
            return None
        print(self.df)
        self.set_lead_row()
        companies = self.handle_companies(but)
        add_contacts_command = "crm.contact.add"
        contacts_queue = []
        for index, row in self.df.iterrows():
            parsed_phone_numbers = [phone.strip() for phone in row['PHONE'].split(',')]
            parsed_emails = [check_if_email(phone) for phone in row['EMAIL'].split(',')]
            if None in parsed_emails:
                parsed_emails.remove(None)
            contacts_queue.append(
                {
                    "NAME": row['NAME'],
                    "LAST_NAME": row['LAST_NAME'],
                    "PHONE": [{"VALUE": phone} for phone in parsed_phone_numbers],
                    "EMAIL": [{"VALUE": email} for email in parsed_emails],
                    "COMPANY_ID": companies.get(row['COMPANY_ID']),
                }
            )
            if len(contacts_queue) == max_data:
                self.import_from_temp_to_bitrix(but=but, queue=contacts_queue, command=add_contacts_command)
                contacts_queue = []
        self.import_from_temp_to_bitrix(but=but, queue=contacts_queue, command=add_contacts_command)
        return None

    def handle_companies(self, but):
        rawCompanies = but.call_api_method("crm.company.list", {
            "select": ["TITLE", "ID"]
        })
        if rawCompanies.get('error'):
            return None
        companies = {}
        for company in rawCompanies.get('result'):
            companies[company["TITLE"]] = company["ID"]

        companies_name = companies.keys()
        add_company_command = "crm.company.add"
        unique_company_queue = [
            (add_company_command, {"fields": {"TITLE": name}})
            for name in self.df['COMPANY_ID'].unique() if name not in companies_name
        ]
        results: BatchResultDict = but.batch_api_call(unique_company_queue)
        i = 0
        for name, res in iter_BatchResultDict(results):
            if res:
                companies[unique_company_queue[i][1]["fields"]["TITLE"]] = res
            i += 1;
        return companies

    def get_companies_id_name(self, but):
        rawCompanies = but.call_api_method("crm.company.list", {
            "select": ["TITLE", "ID"]
        })
        if rawCompanies.get('error'):
            return None
        companies = {}
        for company in rawCompanies.get('result'):
            companies[company["ID"]] = company["TITLE"]
        return companies

    def import_from_temp_to_bitrix(self, but, queue, command):
        queue_to_add = [
            (command, {"fields": field})
            for field in queue
        ]
        return but.batch_api_call(queue_to_add)

    def export_from_bitrix(self, but):
        command = "crm.contact.list"
        raw_contact_data = but.call_api_method(command, {
            "select": self.REQUIRED_FIELDS
        })
        if not raw_contact_data.get("result"):
            return None
        companies = self.get_companies_id_name(but)
        contact_data = [{
            'NAME': contact["NAME"],
            'LAST_NAME': contact["LAST_NAME"],
            "PHONE": ",".join([phone["VALUE"] for phone in contact["PHONE"]]),
            'EMAIL': ",".join([email["VALUE"] for email in contact["EMAIL"]]),
            'COMPANY_NAME': companies.get(contact['COMPANY_ID']),
        } for contact in raw_contact_data.get("result")]
        self.df = pd.DataFrame.from_dict(contact_data)
        return self.df

    def load_data(self, temp_container):
        raise NotImplementedError()

    def unload_data(self, temp_container):
        raise NotImplementedError()

    def prettify_dataframe(self):
        self.df.drop_duplicates()
        self.df = self.df.astype(str)


class CsvContactLoader(BaseContactLoader):
    def load_data(self):
        self.df = pd.read_csv(self.file, delimiter=';')
        self.prettify_dataframe()
        return self.df

    def unload_data(self, temp_container):
        self.df.to_csv(temp_container, index=False)


class XlsxContactLoader(BaseContactLoader):
    def load_data(self):
        self.df = pd.read_excel(self.file)
        self.prettify_dataframe()
        return self.df

    def unload_data(self, temp_container):
        self.df.to_excel(temp_container, index=False)

AVAILABLE_EXTENSIONS = {
    ".csv": CsvContactLoader,
    ".xlsx": XlsxContactLoader,
}

def load_data(but, url):
    parsed = urlparse(url)
    _, ext = splitext(parsed.path)
    if ext.lower() in AVAILABLE_EXTENSIONS:
        content_loader = AVAILABLE_EXTENSIONS[ext.lower()](url)
        try:
            content_loader.load_data()
            content_loader.import_to_bitrix(but)
            return {"done": True};
        except Exception as e:
            print(traceback.format_exc())
            return {"done": False, "error": str(e)};
    else:
        return {"done": False, "error": "Type not supported."};


def get_data(but, ext, temp_container):
    if ext.lower() in AVAILABLE_EXTENSIONS:
        content_loader = AVAILABLE_EXTENSIONS[ext.lower()]()
        try:
            content_loader.export_from_bitrix(but)
            content_loader.unload_data(temp_container)
            return {"done": True};
        except Exception as e:
            return {"done": False, "error": str(e)};
    else:
        return {"done": False, "error": "Type not supported."};

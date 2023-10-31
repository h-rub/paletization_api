import os
from suds.client import Client

USERNAME = "EX_SYNCRON02"
PASSWORD = "Nidec2024$"

def get_sap_client():
    wsdl_url = "http://sapeccqas.embraco.com/sap/bc/srt/wsdl/flv_10002A1011D1/bndg_url/sap/bc/srt/scs/sap/zppws_palletizing?sap-client=100"
    client = Client(url=wsdl_url, username=USERNAME, password=PASSWORD)
    return client
from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Pallet, MountedComponent
from .serializers import PalletSerializer, MountedComponentSerializer, MountedComponentCreateSerializer
from .sap_client import get_sap_client
from xml.etree import ElementTree as ET

class PalletListCreateView(APIView):
    def get(self, request):
        pallets = Pallet.objects.all()
        serializer = PalletSerializer(pallets, many=True)
        return Response(serializer.data)

    def post(self, request):
        identifier = request.data.get("identifier")

        # Buscar un pallet existente por su identifier
        pallet, created = Pallet.objects.get_or_create(identifier=identifier)

        if not created:
            # Si el pallet ya existe, devuelve los datos del pallet y el estado 200 OK
            serializer = PalletSerializer(pallet)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # Si se creó un nuevo pallet, responde con el nuevo pallet y el estado 201 Created
            serializer = PalletSerializer(pallet)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def put(self, request, pallet_id):
        try:
            pallet = Pallet.objects.get(identifier=pallet_id)
            if pallet.is_closed:
                pallet.open_pallet()
            else:
                pallet.close_pallet()
            return Response({"message": "Pallet status closed successfully."})
        except Pallet.DoesNotExist:
            return Response({"error": "Pallet not found."}, status=status.HTTP_404_NOT_FOUND)

class MountedComponentListByPalletView(APIView):
    def get(self, request, pallet_id):
        try:
            pallet = Pallet.objects.get(identifier=pallet_id)
            components = MountedComponent.objects.filter(pallet=pallet)
            serializer = MountedComponentSerializer(components, many=True)
            return Response(serializer.data)
        except Pallet.DoesNotExist:
            return Response({"error": "Pallet not found."}, status=status.HTTP_404_NOT_FOUND)

class MountedComponentAssociateToPalletView(APIView):
    def post(self, request, pallet_id):
        try:
            pallet = Pallet.objects.get(identifier=pallet_id)
            data = request.data
            data['pallet_id'] = pallet.identifier  # Asigna el identificador del pallet a 'pallet_id'
            # TODO: Validar que el componente no esté asociado a otro pallet
            serializer = MountedComponentCreateSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Pallet.DoesNotExist:
            return Response({"error": "Pallet not found."}, status=status.HTTP_404_NOT_FOUND)

class MountedComponentDismountFromPalletView(APIView):
    def delete(self, request, pallet_id, component_id):
        try:
            pallet = Pallet.objects.get(identifier=pallet_id)
            try:
                component = MountedComponent.objects.get(id=component_id, pallet=pallet)
                component.delete()
                return Response({"msg": "MountedComponent dismounted"}, status=status.HTTP_204_NO_CONTENT)
            except MountedComponent.DoesNotExist:
                return Response({"error": "MountedComponent not found in the pallet."}, status=status.HTTP_404_NOT_FOUND)
        except Pallet.DoesNotExist:
            return Response({"error": "Pallet not found."}, status=status.HTTP_404_NOT_FOUND)

class NotifiyToSAPView(APIView):

    def convert_json_to_xml(self, json_data):
        envelope = ET.Element("soapenv:Envelope",  attrib={"xmlns:soapenv": "http://schemas.xmlsoap.org/soap/envelope/", "xmlns:urn": "urn:sap-com:document:sap:soap:functions:mc-style"})
        body = ET.Element("soapenv:Body")
        header = ET.Element("soapenv:Header")
        zppfm_production_notification = ET.Element("urn:ZppfmProductionNotification")
        
        # Construct XML elements based on JSON data
        elements = {
            "IArbpl": json_data.get("IArbpl", ""),
            "IAufnr": json_data.get("IAufnr", ""),
            "ICharg": json_data.get("ICharg", ""),
            "IComplemento": json_data.get("IComplemento", ""),
            "IDataProd": json_data.get("IDataProd", ""),
            "IFase": json_data.get("IFase", ""),
            "IHoraProd": json_data.get("IHoraProd", ""),
            "IMatnrDestino": json_data.get("IMatnrDestino", ""),
            "IMatnrOrigem": json_data.get("IMatnrOrigem", ""),
            "INumin": json_data.get("INumin", ""),
            "IQuantProd": str(json_data.get("IQuantProd", 0)),
        }
        
        for key, value in elements.items():
            element = ET.Element(key)
            element.text = value
            zppfm_production_notification.append(element)
        
        it_json_inst = ET.Element("ItJsonInst")
        it_json_inst.text = str(json_data.get("ItJsonInst", ""))
        
        zppfm_production_notification.append(it_json_inst)
        
        body.append(zppfm_production_notification)

        envelope.append(header)
        
        envelope.append(body)
    
        xml_string = ET.tostring(envelope, encoding='utf-8').decode()
        return xml_string
    
    def post(self, request):
        sap_client = get_sap_client()
        json_data = request.data
        # Convert the JSON data to an XML request
        xml_data = self.convert_json_to_xml(json_data)
        print(type(xml_data))
        palletId = json_data.get("ICharg", "")
        try:
            pallet = Pallet.objects.get(identifier = palletId)
        except Pallet.DoesNotExist:
            return Response({"error": "Pallet not found."}, status=status.HTTP_404_NOT_FOUND)
        # Build the SOAP request using the data from the JSON
        components_list = json_data.get("ItJsonInst", "")
        mat_destino = json_data.get("IMatnrDestino", "")
        if pallet.send_to_sap == True:
            complemento = "X"
        else:
            complemento = ""
        try:
            sap_response = sap_client.service.ZppfmProductionNotification(
            json_data.get("IArbpl", ""), json_data.get("IAufnr", ""), 
            json_data.get("ICharg", ""),
            complemento, json_data.get("IDataProd", ""), json_data.get("IFase", ""), 
            json_data.get("IHoraProd", ""), mat_destino, json_data.get("IMatnrOrig"),  
            json_data.get("INumin", ""), str(json_data.get("IQuantProd", 0)),
            str(components_list))
            fase = sap_response.EFase
            message = sap_response.EMessage
            pallet.send_to_sap = True
            if message == "":
                pallet.sap_success = True
                pallet.sap_status = f"Lote {palletId} sincronizado con éxito en SAP."
                for component_data in components_list:
                    condenser_serial = mat_destino + component_data["sernr"]
                    compressor_serial = component_data["matfi"][:9] + component_data["serfi"]
                    print(condenser_serial)
                    print(compressor_serial)
                    # Si hay MountedComponent asociados al Pallet, también los actualizamos
                    mounted_component = MountedComponent.objects.get(pallet=pallet, condenser_unit_serial = condenser_serial, compressor_unit_serial = compressor_serial)
                    mounted_component.send_to_sap = True
                    mounted_component.sap_status = "Procesado"
                    mounted_component.save()
            else:
                pallet.sap_success = False
                pallet.sap_status = f"Error en sincronización de lote {palletId}. Detalles: {message}"
                for component_data in components_list:
                    condenser_serial =  mat_destino + component_data["sernr"]
                    compressor_serial = component_data["matfi"][:9] + component_data["serfi"]
                    # Si hay MountedComponent asociados al Pallet, también los actualizamos
                    mounted_component = MountedComponent.objects.get(pallet=pallet, condenser_unit_serial = condenser_serial, compressor_unit_serial = compressor_serial)
                    mounted_component.send_to_sap = False
                    mounted_component.sap_status = "Error al procesar"
                    mounted_component.save()
            
            pallet.fase = fase
            pallet.save()
            print(fase)
            print(message)
            
            return Response(sap_response)
        except Exception as e:
            print(e)
            return Response({"error": f"Error: {e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
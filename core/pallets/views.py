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
        envelope = ET.Element("soapenv:Envelope", xmlns="http://schemas.xmlsoap.org/soap/envelope/")
        body = ET.Element("soapenv:Body")
        zppfm_production_notification = ET.Element("urn:ZppfmProductionNotification", xmlns="urn:sap-com:document:sap:soap:functions:mc-style")
        
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
        envelope.append(body)
        
        xml_string = ET.tostring(envelope).decode()
        return xml_string
    
    def get(self, request):
        sap_client = get_sap_client()
        json_data = request.data
        # Convert the JSON data to an XML request
        xml_data = self.convert_json_to_xml(json_data)
        print(xml_data)
        # Build the SOAP request using the data from the JSON
        sap_response = sap_client.service[0].ZppfmProductionNotification(xml_data)
        print(sap_response)
        return Response({})
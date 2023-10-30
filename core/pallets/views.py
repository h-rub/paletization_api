from django.shortcuts import render

# Create your views here.
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Pallet, Component
from .serializers import PalletSerializer, ComponentSerializer, ComponentCreateSerializer

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

class ComponentListByPalletView(APIView):
    def get(self, request, pallet_id):
        try:
            pallet = Pallet.objects.get(identifier=pallet_id)
            components = Component.objects.filter(pallet=pallet)
            serializer = ComponentSerializer(components, many=True)
            return Response(serializer.data)
        except Pallet.DoesNotExist:
            return Response({"error": "Pallet not found."}, status=status.HTTP_404_NOT_FOUND)

class ComponentAssociateToPalletView(APIView):
    def post(self, request, pallet_id):
        try:
            pallet = Pallet.objects.get(identifier=pallet_id)
            data = request.data
            data['pallet_id'] = pallet.identifier  # Asigna el identificador del pallet a 'pallet_id'
            serializer = ComponentCreateSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Pallet.DoesNotExist:
            return Response({"error": "Pallet not found."}, status=status.HTTP_404_NOT_FOUND)

class ComponentDismountFromPalletView(APIView):
    def delete(self, request, pallet_id, component_id):
        try:
            pallet = Pallet.objects.get(identifier=pallet_id)
            try:
                component = Component.objects.get(id=component_id, pallet=pallet)
                component.delete()
                return Response({"msg": "Component dismounted"}, status=status.HTTP_204_NO_CONTENT)
            except Component.DoesNotExist:
                return Response({"error": "Component not found in the pallet."}, status=status.HTTP_404_NOT_FOUND)
        except Pallet.DoesNotExist:
            return Response({"error": "Pallet not found."}, status=status.HTTP_404_NOT_FOUND)

class NotifiyToSAPView(APIView):
    def get(self, request):
        return Response({})
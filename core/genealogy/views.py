from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Component
from .serializers import ComponentSerializer

class ComponentAPIView(APIView):

    def get(self, request):
        condenser_unit_serial = request.query_params.get('condenser_unit_serial')
        compressor_unit_serial = request.query_params.get('compressor_unit_serial')
        order = request.query_params.get('order')
        mode = request.query_params.get('mode')

        if order:
            if mode == 'list':
                try:
                    components = Component.objects.filter(order=order)
                    serializer = ComponentSerializer(components, many=True)
                    return Response(serializer.data)
                except Component.DoesNotExist:
                    return Response([])
            elif mode == 'count':
                try:
                    components = Component.objects.filter(order=order)
                    response = {
                        "total": len(components),
                        "order": order
                    }
                    return Response(response)
                except Component.DoesNotExist:
                    return Response([])

        if condenser_unit_serial:
            try:
                component = Component.objects.get(condenser_unit_serial=condenser_unit_serial)
                serializer = ComponentSerializer(component)
                return Response(serializer.data)
            except Component.DoesNotExist:
                return Response({"detail": "Component not found."}, status=status.HTTP_404_NOT_FOUND)

        if compressor_unit_serial:
            try:
                component = Component.objects.get(compressor_unit_serial=compressor_unit_serial)
                serializer = ComponentSerializer(component)
                return Response(serializer.data)
            except Component.DoesNotExist:
                return Response({"detail": "Component not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"detail": "Please provide condenser_unit_serial or compressor_unit_serial."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        serializer = ComponentSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, condenser_unit_serial):
        try:
            component = Component.objects.get(condenser_unit_serial=condenser_unit_serial)
        except Component.DoesNotExist:
            return Response({"detail": "Component not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = ComponentSerializer(component, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request):
        compressor_unit_serial = request.query_params.get('condenser_unit_serial')

        if compressor_unit_serial:
            try:
                component = Component.objects.get(compressor_unit_serial=compressor_unit_serial)
                component.delete()
                return Response({"success": True}, status=status.HTTP_204_NO_CONTENT)
            except Component.DoesNotExist:
                return Response({"detail": "Component not found.", "success": False}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({"detail": "Please provide condenser."}, status=status.HTTP_400_BAD_REQUEST)


from rest_framework import serializers
from .models import Pallet, Component

class PalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pallet
        fields = '__all__'  # Puedes especificar los campos que deseas incluir aquí si no quieres todos.

class ComponentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Component
        fields = '__all__' 

class ComponentCreateSerializer(serializers.ModelSerializer):    
    pallet_id = serializers.CharField(write_only=True)

    class Meta:
        model = Component
        exclude = ['pallet']

    def create(self, validated_data):
        pallet_id = validated_data.pop('pallet_id')
        try:
            # Buscamos el pallet utilizando el identificador recibido.
            pallet = Pallet.objects.get(identifier=pallet_id)
        except Pallet.DoesNotExist:
            raise serializers.ValidationError("Pallet not found")

        # Asociamos el componente al pallet y lo guardamos.
        component = Component.objects.create(pallet=pallet, **validated_data)
        return component
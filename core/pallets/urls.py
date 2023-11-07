from django.urls import path
from .views import PalletListCreateView, MountedComponentListByPalletView, MountedComponentAssociateToPalletView, MountedComponentDismountFromPalletView, NotifiyToSAPView

urlpatterns = [
    path('pallets/', PalletListCreateView.as_view(), name='pallet-list-create'),
    path('pallets/<str:pallet_id>/', PalletListCreateView.as_view(), name='pallet-detail'),
    path('pallets/<str:pallet_id>/components/', MountedComponentListByPalletView.as_view(), name='component-list-by-pallet'),
    path('pallets/<str:pallet_id>/components/add/', MountedComponentAssociateToPalletView.as_view(), name='component-associate-to-pallet'),
    path('pallets/<str:pallet_id>/components/<int:component_id>/dismount/', MountedComponentDismountFromPalletView.as_view(), name='component-dismount-from-pallet'),
    path('pallets/sap/notifiy/', NotifiyToSAPView.as_view(), name='notify-to-sap')
]

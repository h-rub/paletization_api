from django.urls import path
from .views import PalletListCreateView, ComponentListByPalletView, ComponentAssociateToPalletView, ComponentDismountFromPalletView, NotifiyToSAPView

urlpatterns = [
    path('pallets/', PalletListCreateView.as_view(), name='pallet-list-create'),
    path('pallets/<str:pallet_id>/', PalletListCreateView.as_view(), name='pallet-detail'),
    path('pallets/<str:pallet_id>/components/', ComponentListByPalletView.as_view(), name='component-list-by-pallet'),
    path('pallets/<str:pallet_id>/components/add/', ComponentAssociateToPalletView.as_view(), name='component-associate-to-pallet'),
    path('pallets/<str:pallet_id>/components/<int:component_id>/dismount/', ComponentDismountFromPalletView.as_view(), name='component-dismount-from-pallet'),
    path('pallets/sap/notifiy', NotifiyToSAPView.as_view(), name='notify-to-sap')
]

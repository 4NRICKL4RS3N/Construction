"""
URL configuration for Construction project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from AppConstruction.views import ConnectionUserView, FirstRedirect, ClientView, ConnectionAdminView, AdminView, Logout, \
    DevisDetailView, DashboardView, ImportData, ImportPaiement, TravauxView, TravauxUpdateView, FinitionView, \
    FinitionUpdateView, ExportDevisPDF, ResetDatabase

urlpatterns = [
    path('', FirstRedirect.as_view(), name='first_redirect'),

    path('admin/', ConnectionAdminView.as_view(), name='login_admin'),
    path('admin/devis', AdminView.as_view(), name='devis-admin'),
    path('admin/devis/<int:pk>', DevisDetailView.as_view(), name='devis-detail'),
    path('admin/dashboard', DashboardView.as_view(), name='dashboard'),
    path('admin/dashboard/import-data', ImportData.as_view(), name='import-data'),
    path('admin/dashboard/import-paiement', ImportPaiement.as_view(), name='import-paiement'),

    path('admin/travaux', TravauxView.as_view(), name='travaux-admin'),
    path('admin/travaux/update/<int:pk>', TravauxUpdateView.as_view(), name='travaux-update'),

    path('admin/finition', FinitionView.as_view(), name='finition-admin'),
    path('admin/finition/update/<int:pk>', FinitionUpdateView.as_view(), name='finition-update'),

    path('login/', ConnectionUserView.as_view(), name='login_user'),
    path('construction/', ClientView.as_view(), name='construction'),
    path('construction/export/devis', ExportDevisPDF.as_view(), name='export-devis-pdf'),

    path('logout/', Logout.as_view(), name='logout'),
    path('reset-database/', ResetDatabase.as_view(), name='reset-database')
]

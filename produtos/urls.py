from django.urls import path
from . views import home, imprimir_produtos, lista_produtos

urlpatterns = [
    path('', home, name='lista'),
    path('imprimir/', imprimir_produtos, name='imprimir_produtos'),
    path("tabela", lista_produtos, name="tabela")

]

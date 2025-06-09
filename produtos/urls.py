from django.urls import path
from . views import lista_produtos, imprimir_produtos, lista_produtos

urlpatterns = [
    path('', lista_produtos, name='lista'),
    path('imprimir/', imprimir_produtos, name='imprimir_produtos'),
    path("tabela", lista_produtos, name="tabela")

]

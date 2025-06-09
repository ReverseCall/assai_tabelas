from django.shortcuts import render
from django.core.paginator import Paginator
from .models import Produto
from datetime import date

# Create your views here.

def home(request):
    produtos = Produto.objects.all()
    paginator = Paginator(produtos, 10)  # 10 itens por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'lista.html', {'page_obj': page_obj})


def imprimir_produtos(request):
    produtos = Produto.objects.all()
    data_atual = date.today()
    return render(request, 'imprimir.html', {'produtos': produtos, 'data': data_atual})


def lista_produtos(request):
    produtos = Produto.objects.all()
    modo_tabela = False  # ou pegue isso do request se quiser persistência via GET
    return render(request, 'lista_produtos.html', {
        'produtos': produtos,
        'modo_tabela': modo_tabela,
    })
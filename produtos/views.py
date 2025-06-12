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
    produtos = list(Produto.objects.all())
    max_linhas = 40

    # === Divide os produtos em colunas verticais ===
    colunas = []
    for i in range(0, len(produtos), max_linhas):
        colunas.append(produtos[i:i+max_linhas])

    linhas_necessarias = max(len(c) for c in colunas) if colunas else 0
    linhas = range(linhas_necessarias)

    num_pares = len(colunas)

    # === Define a largura da tabela ===
    if num_pares % 4 == 0:
        largura_tabela = "100%"
    else:
        largura_percentual = min(100, num_pares * 25)
        largura_tabela = f"{largura_percentual}%"

    context = {
        'produtos': produtos,
        'colunas': colunas,
        'linhas': linhas,
        'modo_tabela': True,
        'largura_tabela': largura_tabela,
    }

    return render(request, 'lista_produtos.html', context=context)
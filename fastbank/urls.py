from . import views
from rest_framework import routers
from .views import EmprestimoCreateAPIView
from django.urls import include, path
from .views import me_view



router = routers.SimpleRouter()
router.register('Usuario', views.ListarDetalharUsuario)
router.register('clientes',views.ClientesViewSet, basename='clientes')
router.register('endereco',views.EnderecoViewSet)
router.register('contato',views.ContatoViewSet)
path('emprestimos/', EmprestimoCreateAPIView.as_view(), name='emprestimos-create'),
router.register('conta',views.ContaViewSet)
path('auth/token/login', views.login_view, name='login'),
router.register('cartao',views.CartaoViewSet)
router.register('investimento',views.InvestimentoViewSet)
router.register('movimentacao',views.MovimentacaoViewSet)
path('auth/users/me', me_view, name='me'),
path('banco/transferencias/', views.Transferencia),




urlpatterns = [] +router.urls
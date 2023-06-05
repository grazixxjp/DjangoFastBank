from .serializer import *
import decimal
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import AccessToken
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.generics import CreateAPIView
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate, login

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'auth_token': 'seu_token_de_autenticacao'})
        else:
            return JsonResponse({'error': 'E-mail ou senha incorretos'}, status=401)

    return JsonResponse({'error': 'Método não permitido'}, status=405)

class ListarDetalharUsuario(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer

class TransferenciaSerializer(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, ) 
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

def me_view(request):
    user = request.user  

    response = {
        'email': user.email,
        'password': user.password
    }

    return JsonResponse(response)

class ListarDetalharTransferencia(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )
    queryset = Transferencia.objects.all()
    serializer_class = TransferenciaSerializer

    def create(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION', '').split(' ')[1]
        dados = AccessToken(token)
        usuario = dados['user_id']
        conta_remetente = Conta.objects.get(fk_usuario=usuario)
        destinatario = request.data['cpf']
        if destinatario :
            if conta_remetente.saldo >= decimal.Decimal(request.data['valor']):
                print(conta_remetente.saldo)
                conta_remetente.saldo -= decimal.Decimal(request.data['valor'])
                conta_remetente.save()
                cpf_destinatario = Cliente.objects.get(cpf=destinatario)
                conta_destinatario = Conta.objects.get(fk_usuario=cpf_destinatario.id)
                if conta_destinatario is not None:
                    conta_destinatario.saldo += decimal.Decimal(request.data['valor'])
                    conta_destinatario.save()
                    request.POST._mutable = True
                    request.data['codigo_conta'] = conta_remetente
                    request.data['conta_destinatario'] = conta_destinatario.id

        else:
            raise serializers.ValidationError({'Conta destinatário não existe'})
        
        
        return super().create(request, *args, **kwargs)

class ClientesViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, ) 
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    
    def get_queryset(self):
        queryset = Cliente.objects.all()
        # query            
        cpf = self.request.query_params.get('cpf')
        if cpf is not None:
            usuario =  get_object_or_404(Cliente, user__id_fiscal=cpf)
            if usuario is not None:
                print("caiu aqui")
                queryset = queryset.filter(id=usuario.id)
            return queryset
        else:
            queryset = Cliente.objects.all()
            return queryset
        

class EnderecoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )  
    queryset = Endereco.objects.all()
    serializer_class = EnderecoSerializer

    def create(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION', '').split(" ")[1]
        print(token)
        dados_TOKEN = AccessToken(token)
        usuario = dados_TOKEN['user_id']
        print(usuario)
        clienteObject = Cliente.objects.get(user=usuario)
        print(clienteObject)
        dados = request.data
        print(dados)    
        criar = Endereco.objects.create(
            logradouro = dados['logradouro'],
            bairro = dados['bairro'],
            cep = dados['cep'],
            cidade = dados['cidade'],
            n_casa = dados['casa'],
            uf = dados['uf'],
            cliente = clienteObject,
        )
        return super().list(request, *args, **kwargs)
    

class ContatoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )  
    queryset = Contato.objects.all()
    serializer_class = ContatoSerializer

    def create(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION', '').split(" ")[1]
        print(token)
        dados_TOKEN = AccessToken(token)
        usuario = dados_TOKEN['user_id']
        print(usuario)
        clienteObject = Cliente.objects.get(user=usuario)
        print(clienteObject)
        dados = request.data
        print(dados)    
        criar = Contato.objects.create(
            telefone = dados['telefone'],
            ramal = dados['ramal'],
            # observacao = dados['observacao'],
            email = dados['email'],
            cliente = clienteObject,
            )
        return super().list(request, *args, **kwargs)
    

class ContaViewSet(viewsets.ModelViewSet):
    # permission_classes = (IsAuthenticated, )  
    queryset = Conta.objects.all()
    serializer_class = ContaSerializer
    def get_queryset(self):
        queryset = Conta.objects.all()
        id_Cliente = self.request.query_params.get('cliente')
        if id_Cliente is not None:
            queryset = queryset.filter(cliente=id_Cliente)
            return queryset
        else:
            queryset = Conta.objects.all()
            return queryset
        
    def create(self, request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION', '').split(" ")[1]
        dados_TOKEN = AccessToken(token)
        usuario = dados_TOKEN['user_id']
        clienteObject = Cliente.objects.get(user=usuario)
        dados = request.data
        criar = Conta.objects.create(
            ativo = dados['ativo'],
            agencia = dados['agencia'],
            cliente = clienteObject,
            tipo =  dados['tipo'],
            saldo = dados['saldo'],
            numero = dados['numero'],
        )
        return super().list(request, *args, **kwargs)

class EmprestimoCreateAPIView(CreateAPIView):
    serializer_class = EmprestimoSerializer


class MovimentacaoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )  
    queryset = Movimentacao.objects.all()
    serializer_class = MovimentacaoSerializer
    def get_queryset(self):
        queryset = Movimentacao.objects.all()
        id_Conta = self.request.query_params.get('conta')
        if id_Conta is not None:
            queryset = queryset.filter(Q(conta_remetente=id_Conta) | Q(conta_destinatario=id_Conta))
            # queryset +=queryset.filter(conta_destinatario=id_Conta)
            return queryset
        else:
            queryset = Movimentacao.objects.all()
            return queryset     

class InvestimentoViewSet(viewsets.ModelViewSet):
    queryset = Investimento.objects.all()
    serializer_class = InvestimentoSerializer

class CartaoViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthenticated, )  
    queryset = Cartao.objects.all()
    serializer_class = CartaoSerializer

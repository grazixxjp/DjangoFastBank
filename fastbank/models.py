from django.db import models
from django.contrib import admin
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin,AbstractUser
from django.core.validators import MinValueValidator,MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

# class CustomUser(AbstractUser):
#     id_fiscal = models.CharField(max_length=20, unique= True)
#     username = None

#     USERNAME_FIELD = "id_fiscal"
#     REQUIRED_FIELDS = []

#     objects = CustomUserManager()

#     def __str__(self):
#         return self.id_fiscal
from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UsuarioManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, senha, **extra_fields):
        """
        Create and save a user with the given email and senha.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_senha(senha)
        user.save()
        return user

    def create_superuser(self, email, senha, **extra_fields):
        """
        Create and save a SuperUser with the given email and senha.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, senha, **extra_fields)

class Usuario(AbstractUser):
    username = None
    nome_cliente = models.CharField(max_length=100)
    email = models.EmailField(_("email address"), unique=True)
    nome_cliente = models.CharField(max_length=100)
    cpf_cnpj = models.CharField(max_length=11, unique=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(default=timezone.now)
    foto = models.ImageField(upload_to="foto_perfil", blank=True, null=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [  "nome_cliente",
        "cpf_cnpj",
        "nome_cliente",
        ]

    objects = UsuarioManager()

    def __str__(self):
        return self.email

    
class Cliente(models.Model):
    nome = models.CharField(max_length=255)
    rg = models.CharField(max_length=13)
    foto = models.ImageField(upload_to="pessoas", null=True)
    dt_nascimento = models.DateField()
    dt_abertura = models.DateField(auto_now=True)
    
    def __str__(self) -> str:
        return self.nome

class Endereco(models.Model):
    logradouro = models.CharField(max_length=100)
    bairro = models.CharField(max_length=75)
    cidade = models.CharField(max_length=75)
    uf = models.CharField(max_length=2)
    cep = models.CharField(max_length=10)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)



class Contato(models.Model):
    telefone = models.CharField(max_length=14)
    ramal = models.IntegerField(null=True)
    observacao = models.TextField(max_length=255)
    email = models.EmailField(unique=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)

class Conta(models.Model):
    CONTA_SALARIO ="S"
    CONTA_DEPOSITO ="D"
    CONTA_PAGAMENTO ="P"
    CONTA_CHOICES = (
        (CONTA_SALARIO,"SALARIO"),
        (CONTA_DEPOSITO, "DEPOSITO"),
        (CONTA_PAGAMENTO,"PAGAMENTO")
    )

    ativo = models.BooleanField(default=True)
    agencia = models.IntegerField()
    tipo = models.CharField(max_length=1, choices=CONTA_CHOICES, default=CONTA_DEPOSITO)
    numero = models.IntegerField()
    saldo = models.DecimalField(max_digits=11,decimal_places=2)
    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    
    def __str__(self) -> str:
        return self.cliente.nome
    
class Transferencia(models.Model):
    
    conta_destinatario = models.ForeignKey(Conta, on_delete=models.PROTECT, related_name="conta_destinatario")
    conta_remetente = models.ForeignKey(Conta, on_delete=models.PROTECT, related_name="conta_remetente",)
    data= models.DateField(auto_now=True)
    hora = models.TimeField(auto_now=True)
    valor = models.DecimalField(max_digits=6, decimal_places=2)
    cpf = models.CharField(max_length=11)

class Emprestimo(models.Model):
    fk_conta_emprestimo = models.ForeignKey(Conta, on_delete=models.CASCADE)
    dataSolicitacao = models.DateField(auto_now=True)
    valorSolicitado = models.DecimalField(validators=[MinValueValidator(1,message='O preço deve ser maior que 1 real'),MaxValueValidator(20000)], max_digits=10, decimal_places=2)
    juros = models.FloatField()
    valorTotalJuros = models.FloatField()
    valorParcelaJuros = models.FloatField()
    aprovado = models.BooleanField(default=False)

class Movimentacao(models.Model):
    TRANSFERENCIA_PIX = 'PI'
    TRANSFERENCIA_DOC = 'DC' #TRANSFERENCIA DE CONTAS DO MESMO BANCO 
    
    TRANSFERENCIA_CHOICES = (
        (TRANSFERENCIA_PIX,'PIX'),
        (TRANSFERENCIA_DOC,'DOC'),
    )

    cliente = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='transferencias_enviadas')
    destinatario = models.ForeignKey(Conta, on_delete=models.CASCADE, related_name='transferencias_recebidas')
    dataHora = models.DateField(auto_now=True)
    valor = models.DecimalField(max_digits=8, decimal_places=8)
    operacao = models.CharField(max_length=2, choices=TRANSFERENCIA_CHOICES, default=TRANSFERENCIA_PIX)

    def __str__(self) -> str:
        return self.conta_destinatario.cliente.nome


class Investimento(models.Model):
    TPINVEST_CRIPTO ='C'
    TPINVEST_ACAO ='A'
    TPINVEST_POUP ='P'
    TPINVEST_CHOICES = (
        (TPINVEST_CRIPTO,'CRIPTOMOEDA'),
        (TPINVEST_ACAO, 'AÇÃO'),
        (TPINVEST_POUP,'POUPANÇA')
    )
    RISCO_ALTO ='A'
    RISCO_MEDIO ='M'
    RISCO_BAIXO ='B'
    RISCO_CHOICES = (
        (RISCO_ALTO,'ALTO'),
        (RISCO_MEDIO, 'MEDIO'),
        (RISCO_BAIXO,'BAIXO')
    )
    tipo = models.CharField(max_length=1, choices=TPINVEST_CHOICES, default=TPINVEST_CRIPTO)
    aporte = models.DecimalField(validators=[MinValueValidator(1,message='O preço deve ser igual ou maior que 1 real')], max_digits=6, decimal_places=2)
    taxaAdministracao = models.DecimalField(validators=[MinValueValidator(1,message='O preço deve ser igual ou maior que 1 real')], max_digits=6, decimal_places=2)
    prazo = models.DateField()
    grauRisco = models.CharField(max_length=1, choices=RISCO_CHOICES, default=RISCO_MEDIO)
    rentabilidade = models.DecimalField( max_digits=6, decimal_places=2)
    finalizado = models.BooleanField()
    conta = models.ForeignKey(Conta,on_delete=models.PROTECT)

class Cartao(models.Model):
    SIT_CARTAO_BLOQ = 'B'
    SIT_CARTAO_DES = 'D'
    SIT_CARTAO_CHOICES=(
        (SIT_CARTAO_BLOQ,'BLOQUEADO'),
        (SIT_CARTAO_DES,'DESBLOQUEADO'),
    )
    
    numero_cartao = models.CharField(max_length=20)
    cvv = models.IntegerField()
    data_vencimento = models.DateField()
    bandeira = models.CharField(max_length=20)
    nome_titular_cartao = models.CharField(max_length=100)
    cartao_ativo = models.BooleanField(default=True)
    nome_titular = models.CharField(max_length=255)
    numero_conta = models.CharField(max_length=5)
    limite_disponivel = models.DecimalField(decimal_places=2, max_digits=5)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["numero_cartao"],
                name="unique_numero_cartao",
            )
        ]
        verbose_name_plural = "Cartao"
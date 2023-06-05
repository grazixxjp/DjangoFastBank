from .models import * 
from rest_framework import serializers

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario 
        fields = ['email', 'username', 'password']

class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["usuario", "senha"]

class ClienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cliente
        fields =['id','nome','foto','dt_nascimento','dt_abertura','rg','user']

class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields=['id','logradouro','cidade','bairro','uf','cep','cliente']

class ContatoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contato
        fields=['id','telefone','ramal','observacao','email','cliente']


class EmprestimoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emprestimo
        fields = '__all__'

    def validate(self, data):
        # Obtenha os dados da solicitação
        valor_solicitado = data.get('valorSolicitado')
        fk_conta_emprestimo = data.get('fk_conta_emprestimo')

        # Faça a validação dos dados conforme suas regras
        if valor_solicitado < 1 or valor_solicitado > 20000:
            raise serializers.ValidationError('O valor solicitado deve estar entre 1 e 20000.')

        # Verifique se o usuário possui renda suficiente para o empréstimo
        conta_emprestimo = Conta.objects.get(id=fk_conta_emprestimo)
        if conta_emprestimo.renda_mensal < valor_solicitado:
            raise serializers.ValidationError('Sua renda mensal não é suficiente para o empréstimo.')

        # Calcule a porcentagem de juros com base no valor
        porcentagem_juros = self.get_porcentagem_juros(valor_solicitado)

        # Adicione a porcentagem de juros ao response
        self.context['response']['porcentagem_juros'] = porcentagem_juros

        return data

    def get_porcentagem_juros(self, valor):
        if valor >= 1000 and valor <= 5000:
            return 5
        elif valor > 5000 and valor <= 10000:
            return 10
        elif valor > 10000 and valor <= 20000:
            return 15
        else:
            return 0

    def create(self, validated_data):
        # Crie o objeto empréstimo com os dados validados
        emprestimo = Emprestimo.objects.create(**validated_data)

        # Atualize o saldo da conta
        conta_emprestimo = emprestimo.fk_conta_emprestimo
        novo_saldo = conta_emprestimo.limite + emprestimo.valorSolicitado
        conta_emprestimo.limite = novo_saldo
        conta_emprestimo.save()

        return emprestimo


class ContaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conta
        fields = ['id','ativo','agencia','tipo','numero','saldo','cliente']

class CartaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cartao
        fields = ['id','numero','validade','cvv','situacao','bandeira','limite','conta']

class InvestimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Investimento
        fields = ['id','tipo','aporte','taxaAdministracao','prazo','grauRisco','rentabilidade','finalizado','conta']

class MovimentacaoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movimentacao
        fields = ['id_movimentacao', 'dataHora', 'valor', 'operacao']
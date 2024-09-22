import textwrap

from abc import ABC, abstractmethod
from datetime import datetime

def menu():
    menu = """\n
    ================ MENU ================
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNova conta
    [5]\tListar contas
    [6]\tNovo usuário
    [7]\tSair
    => """
    return input(textwrap.dedent(menu))

class Historico:
    def __init__(self):
        self._transacoes = []
    
    @property
    def transacoes(self):
        return self._transacoes
    
    def adicionar_transacao(self, transacao):
        self._transacoes.append({
            "tipo": transacao.__class__.__name__,
            "valor": transacao.valor,
        })
    
class Transacao:
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(conta):
        pass

class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.depositar(int(self.valor))

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor
    
    @property
    def valor(self):
        return self._valor
    
    def registrar(self, conta):
        sucesso_transacao = conta.sacar(int(self.valor))

        if sucesso_transacao:
            conta.historico.adicionar_transacao(self)

class Cliente:
    def __init__(self, endereco):
        self._endereco = endereco
        self.contas = []

    @property
    def endereco(self):
        return self._endereco
    
    def realizar_transacao(self, conta, transacao: Transacao):
        return transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self._contas.append(conta)

class PessoaFisica(Cliente):
    def __init__(self, endereco, cpf, nome, data_nascimento):
        super().__init__(endereco)
        self.cpf = cpf
        self.nome = nome
        self.data_nascimento = data_nascimento

class Conta:
    def __init__(self, num, cliente):
        self._saldo = 0
        self._numero = num
        self._agencia = "0001"
        self._cliente = cliente
        self._historico = Historico()
    
    @property
    def saldo(self):
        return self._saldo
    
    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self):
        return self._cliente

    @property
    def historico(self):
        return self._historico

    @classmethod
    def nova_conta(cls, cliente: Cliente, numero: int):
        return cls(numero, cliente)

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("\n----Valor superior ao saldo atual, operação inválida!----")
        elif valor < 0:
            print("\n----Valor de saque inválido, insira novamente!!----")
        else:
            self._saldo -= valor
            print("\n----Saque realizado com sucesso----")
            return True
        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("\n----Depósito realizado com sucesso----")
            return True
        print("\nOperacao falhou! Valor invalido de deposito.")
        return False        
    
class ContaCorrente(Conta):
    def __init__(self, num, cliente, limite = 500, limite_saques = 3):
        super().__init__(num, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    def sacar(self, valor):
        limite = self.limite
        limite_saque = self.limite_saques

        numero_saque = len(
            [transacao for transacao in self.historico.transacoes if transacao["tipo"] == Saque.__name__]
        )
        
        excedeu_saque = numero_saque >= limite_saque
        excedeu_limite = valor > limite

        if excedeu_limite :
            print("\n----Valor superior ao saldo atual, operação inválida!----")
        elif excedeu_saque:
            print("\n----Limite diários de saques excedidos! Volte amanhã!!----")
        else:
            return super().sacar(valor)
        return False

    def __str__(self):
        return f"""\
            Agência:\t{self.agencia}
            C/C:\t\t{self.numero}
            Titular:\t{self.cliente.nome}
        """
    
def procurar_cliente(cpf, clientes):
    for cliente in clientes:
        if cliente.cpf == cpf:
            return cliente
    return None

def escolher_conta_cliente(cliente):
    if not cliente.contas:
        print("CPF informado não tem contas vinculadas!")
        return None
    num_conta = input("Qual o número da conta que ocorrerá a operação?\n")
    index_conta = 0
    for conta in cliente.contas:
        if conta.numero == num_conta:
            break
        index_conta = index_conta + 1
    return cliente.contas[0]

def depositar(clientes):
    cpf = input("Digite o cpf ligado a conta: ")
    cliente = procurar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Não existe um cliente vinculado à esse cpf!! @@@\n")
        return menu()
    valor = input("\nDigite o valor do depósito: ")
    transacao = Deposito(valor)

    conta = escolher_conta_cliente(cliente)
    if not conta:
        print("\n Conta selecionada não existe. \n")
        return menu()
    cliente.realizar_transacao(conta, transacao)

def sacar(clientes):
    cpf = input("Digite o cpf ligado a conta: ")
    cliente = procurar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Não existe um cliente vinculado à esse cpf!! @@@\n")
        return menu()

    valor = input("\nDigite o valor do saque: ")
    transacao = Saque(valor)

    conta = escolher_conta_cliente(cliente)
    if not conta:
        print("\n Conta selecionada não existe. \n")
        return menu()
    cliente.realizar_transacao(conta, transacao)

def mostrar_extrato(clientes):
    cpf = input("Digite o cpf ligado a conta: ")
    cliente = procurar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Não existe um cliente vinculado à esse cpf!! @@@\n")
        return menu()

    conta = escolher_conta_cliente(cliente)
    if not conta:
        print("\n Conta selecionada não existe. \n")
        return menu()
    print("\n--------------EXTRATO--------------\n")

    transacoes = conta.historico.transacoes
    for transacao in transacoes:
        print(f"{transacao["tipo"]}: R$ {transacao["valor"]}\n")
    print(f"Saldo Atual: R$ {conta.saldo:.2f}")
    print("-----------------------------------")
    
def nova_conta(clientes, contas, num_nova_conta):
    cpf = input("Digite o cpf ligado a conta: ")
    cliente = procurar_cliente(cpf, clientes)

    if not cliente:
        print("\n@@@ Não existe um cliente vinculado à esse cpf!! @@@\n")
        return menu()

    conta = ContaCorrente.nova_conta(cliente = cliente, numero = num_nova_conta)

    contas.append(conta)
    cliente.contas.append(conta)

    print("\n-----CONTA CRIADA COM SUCESSO!!-----\n")

def listar_contas(contas):
    print("---------------CONTAS---------------")

    for conta in contas:
        print(textwrap.dedent(str(conta)))
    print("------------------------------------")


def novo_cliente(clientes):
    cpf = input("\nDigite o cpf ligado a conta.\n")
    cliente = procurar_cliente(cpf, clientes)

    if cliente:
        print("\n@@@ Já existe um cliente vinculado à esse cpf!! @@@\n")
        return
    nome = input("\nInforme o nome completo.\n")
    data_nascimento = input("\nInforme a data de nascimento (dd-mm-yyyy)\n")
    endereco = input("\nInforme o endereço (logradouro, nro bairro estado-sigla)\n")

    cliente = PessoaFisica(nome = nome, data_nascimento = data_nascimento, endereco = endereco, cpf = cpf)

    clientes.append(cliente)

    print("\n------Conta criada com sucesso!!!-------")

def main():
    clientes = []
    contas = []

    while True:

        opcao = menu()

        if opcao == "1":
            depositar(clientes)
        elif opcao == "2":
            sacar(clientes)
        elif opcao == "3":
            mostrar_extrato(clientes)
        elif opcao == "4":
            num_nova_conta = len(contas) + 1
            nova_conta(clientes, contas, num_nova_conta)
        elif opcao == "5":
            listar_contas(contas)
        elif opcao == "6":
            novo_cliente(clientes)
        elif opcao == "7":
            break
        else:
            print("\nOperação inválida, por favor selecione uma operação válida! \n")

main()
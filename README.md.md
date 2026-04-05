# Sistema de Controle de Qualidade Industrial (SCQ-I)

## Descrição do Projeto

Este projeto consiste em um sistema desenvolvido em Python para automatizar o controle de qualidade de peças em uma linha de produção industrial.

O sistema substitui a inspeção manual, avaliando automaticamente cada peça com base em critérios pré-definidos e organizando as peças aprovadas em caixas com capacidade limitada.

Além disso, os dados são armazenados em um banco de dados SQLite, garantindo persistência das informações mesmo após o encerramento do programa.

---

## Funcionalidades

O sistema possui um menu interativo com as seguintes opções:

1. Cadastrar nova peça  
2. Listar peças aprovadas e reprovadas  
3. Remover peça cadastrada  
4. Listar caixas (abertas e fechadas)  
5. Gerar relatório final  

---

## Regras de Validação

Cada peça é analisada com base nos seguintes critérios:

- Peso: entre 95g e 105g  
- Cor: azul ou verde  
- Comprimento: entre 10cm e 20cm  

Caso a peça não atenda aos critérios, o sistema informa todos os erros encontrados.

---

## Armazenamento (SQLite)

O sistema utiliza um banco de dados SQLite chamado:

pecas_industria.db

As informações são armazenadas em duas tabelas:

- pecas → dados das peças (aprovadas e reprovadas)  
- caixas → controle das caixas (abertas/fechadas)  

As caixas são automaticamente fechadas quando atingem 10 peças aprovadas.

---

## Como Executar o Programa

### Pré-requisitos:
- Python 3 instalado

### Passo a passo:

1. Baixe o arquivo:
   trabalho_sqlite_autoincrement_corrigido.py

2. Abra o terminal na pasta do arquivo

3. Execute o comando:
   python trabalho_sqlite_autoincrement_corrigido.py

4. Utilize o menu interativo

---

## Exemplos de Entrada e Saída

### Peça Aprovada
Entrada:
Peso: 100  
Cor: verde  
Comprimento: 15  

Saída:
Peça X APROVADA e armazenada na caixa 1.

---

### Peça Reprovada
Entrada:
Peso: 110  
Cor: vermelho  
Comprimento: 25  

Saída:
Reprovada por: Peso fora do limite (110g) | Cor 'vermelho' nao permitida | Comprimento fora do limite (25cm)

---

### Caixa Cheia
Ao cadastrar a 10ª peça válida:
Caixa 1 cheia e fechada.

---

## Boas Práticas Aplicadas

- Uso de funções com responsabilidade única  
- Validação completa de dados  
- Tratamento de erros com try/except  
- Uso de banco de dados (SQLite)  
- Estrutura organizada  

---

## Possíveis Melhorias Futuras

- Integração com sensores industriais (IoT)  
- Uso de visão computacional  
- Interface gráfica (GUI)  
- Integração com sistemas industriais  

---

## Autor

Aluno: Alexandre Yukio Yamashita  
R.A.: 237220  
Disciplina: Algoritmos e Lógica de Programação  

---

## Repositório

Link do GitHub: (inserir aqui)

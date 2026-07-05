# Base de Conhecimento

## Dados Utilizados

Descreva se usou os arquivos da pasta `data`, por exemplo:

| Arquivo | Formato | Utilização no Agente |
|---------|---------|---------------------|
| `MINIGUIA_SFN_INVESTIMENTOS.md` | MD |Doc. base da pesquisa, estruturando toda a lógica dos jogos inclusivos. |
| `GLOSSÁRIO DE CONCEITOS.md` | MD | Suporte didático para simplificar termos técnicos |
| `Quizzes_investimentos.json` | JSON | Quizzes com feedback explicativo adequados ao perfil |
| `Jogos_inclusivos.json` | JSON | Jogos narrativos e metáforas adaptadas a diferentes públicos (jovens, idosos, pessoas com deficiência visual/auditiva e           neurodivergentes).|
|`historico_atendimento.csv` | CSV | Contextualizar interações anteriores |
| `transacoes.csv` | CSV | Analisar padrão de gastos do cliente |

---

## Adaptações nos Dados

> Você modificou ou expandiu os dados mockados? Descreva aqui.

Foram introduzidos novos dados para expandir o escopo do projeto idealizado e assim, dando continuidade prática ao Miniguia_SFN_Investimentos, projeto desenvolviso no Notebook LM, no qual foi o primeiro Desafio_DIO no bootcamp Bradesco - GenAI & Dados, e logo, é a base deste projeto. 

* MINIGUIA_SFN_INVESTIMENTOS.md: base da pesquisa.
* GLOSSÁRIO DE CONCEITOS.md: suporte didático 
* Quizzes_investimentos.json: método para inclusão e ensino didático e dinâmico focando cada perfil
* Jogos_inclusivos.json: jogos narrativos e metáforas adaptadas a diferentes públicos (jovens, idosos, pessoas com deficiência visual/auditiva e neurodivergentes)

Foram mantidos sem alterações:
* historico_atendimento.csv
* transacoes.csv
---

## Estratégia de Integração

### Como os dados são carregados?
> Descreva como seu agente acessa a base de conhecimento.

Os arquivos JSON/Markdown criados e os CSV originais são carregados no início da sessão. E, o agente acessa dinamicamente os dados conforme o perfil/público-alvo do usuário.

### Como os dados são usados no prompt?
> Os dados vão no system prompt? São consultados dinamicamente?

Os dados não são inseridos diretamente no system prompt. Eles são consultados dinamicamente:

### Exemplo de como funciona

Usuário: "O que é liquidez?"

Agente consulta:
- GLOSSÁRIO DE CONCEITOS.md → definição de liquidez
- MINIGUIA_SFN_INVESTIMENTOS.md → reforço conceitual

Resposta do agente:
"Liquidez é a facilidade de transformar um investimento em dinheiro disponível. Por exemplo, o Tesouro Selic tem liquidez diária, o que significa que você pode resgatar o valor a qualquer momento."

---

## Exemplo de Contexto Montado

> Mostre um exemplo de como os dados são formatados para o agente.

```
### Dados do Cliente
- Nome: João Silva
- Perfil: Moderado
- Saldo disponível: R$ 5.000

### Últimas Transações (transacoes.csv)
- 01/11: Supermercado - R$ 450
- 03/11: Streaming - R$ 55
- 05/11: Farmácia - R$ 120

### Conceito (GLOSSÁRIO DE CONCEITOS.md)
- Liquidez: Facilidade de transformar um investimento em dinheiro disponível.

### Quiz (Quizzes_investimentos.json)
Pergunta: Qual investimento tem liquidez diária?
Opções:  
A) Tesouro Selic  
B) LCI com carência de 90 dias  
C) Ações  
Resposta correta: A) Tesouro Selic  
Feedback: O Tesouro Selic permite resgate diário, ideal para reserva de emergência.

### Jogo Narrativo (Jogos_inclusivos.json)
Contexto: Idoso pergunta sobre reserva de emergência.  
Resposta adaptada: "Imagine um cofre para imprevistos. O Tesouro Selic funciona como esse cofre, pois você pode acessar o dinheiro a qualquer momento."

```


# 📁 Assents — BIA Academy Finance

Esta pasta reúne todos os recursos visuais utilizados na documentação do projeto **BIA Academy Finance**.

Seu objetivo é facilitar o entendimento da arquitetura, do fluxo de funcionamento e da experiência do usuário, servindo como apoio para documentação técnica, apresentações e portfólio.

---

# 🧩 1. Estrutura da Pasta

```text
assents/
├── diagramas/
│   └── arquitetura.md
│
├── screenshots/
│   ├── chat_tela.png
│   ├── quiz_tela.png
│   ├── jogo_tela.png
│   └── api_endpoint.png
│
├── mockups/
│   ├── quiz_mockup.md
│   └── jogo_mockup.md
│
└── imagens_readme/
    ├── logo.png
    ├── fluxo.png
    └── inclusao.png
```

---

# 🧠 2. Arquitetura do Sistema

A BIA Academy Finance possui uma arquitetura modular executada localmente, utilizando IA Generativa, RAG e um modelo LLM local através do Ollama.

```text
+---------+
| Usuário |
+---------+
      │
      ▼
+---------------------------+
| app.py (Streamlit)        |
| Interface do usuário      |
+---------------------------+
      │
      ▼
+---------------------------+
| Lógica da BIA             |
| • Classificação           |
| • Segurança               |
| • Personalização          |
| • Prompt Engineering      |
+---------------------------+
      │
      ▼
+----------------------+----------------------+
| Base Local           | Base RAG            |
| Glossário            | Documentos          |
| CSV                  | FAISS              |
| JSON                 | Embeddings         |
+----------------------+----------------------+
      │
      ▼
+---------------------------+
| LLM Local (Ollama)        |
+---------------------------+
      │
      ▼
+---------------------------+
| Resposta Inteligente      |
+---------------------------+
      │
      ▼
+---------------------------+
| Acessibilidade            |
| • Áudio (gTTS)            |
| • Linguagem Adaptada      |
+---------------------------+
```

---

# 🔄 3. Fluxo Geral do Sistema

O usuário escolhe diretamente qual funcionalidade deseja utilizar.

```text
                 +---------+
                 | Usuário |
                 +---------+
                      │
                      ▼
            +----------------------+
            | app.py (Streamlit)   |
            +----------------------+
                      │
                      ▼
              Escolha do módulo
                      │
     ┌───────────────┼───────────────┐
     ▼               ▼               ▼
+-----------+   +-----------+   +-----------+
| Chat IA   |   | Quiz      |   | Jogo      |
+-----------+   +-----------+   +-----------+
     │               │               │
     ▼               ▼               ▼
Pergunta       Perguntas        Fases
do usuário     educativas       progressivas
     │               │               │
     ▼               ▼               ▼
Busca de       Validação       Feedback
contexto       da resposta     imediato
(RAG)               │               │
     │               ▼               ▼
     │          Pontuação      Pontuação
     │               │               │
     └───────────────┼───────────────┘
                     ▼
             Resposta Adaptada
                     │
                     ▼
             Áudio (Opcional)
```

---

# 🎯 4. Conceitos do Sistema

## Escolha do Usuário

O usuário pode acessar livremente qualquer módulo:

* 💬 Chat Educacional
* 🧠 Quiz Educativo
* 🎮 Jogo Evolutivo

---

## Inteligência Artificial

A BIA utiliza:

* IA Generativa
* Prompt Engineering
* Base de Conhecimento Local
* RAG (Retrieval-Augmented Generation)
* LLM Local (Ollama)

---

## Adaptação por Público

As respostas são adaptadas conforme o perfil selecionado:

* Investidor iniciante
* Idosos
* Pessoas com deficiência visual
* Pessoas com deficiência auditiva
* Pessoas neurodivergentes

---

## Segurança

A BIA não realiza recomendações financeiras.

Ela:

* explica conceitos;
* apresenta exemplos;
* utiliza documentos internos;
* evita aconselhamento financeiro.

---

# 🧠 5. Mockup — Quiz

```text
+--------------------------------------+
|      BIA Academy Finance             |
+--------------------------------------+

Pergunta:

Qual investimento possui maior liquidez?

( ) Tesouro Selic
( ) LCI
( ) Ações

[ Confirmar ]

Feedback:

"O Tesouro Selic pode ser resgatado diariamente."

Pontuação: +10
```

---

# 🎮 6. Mockup — Jogo Evolutivo

```text
+--------------------------------------+
|      BIA Academy Finance             |
+--------------------------------------+

Fase 1

Você recebeu seu salário.

O que deve fazer primeiro?

( ) Gastar tudo

( ) Guardar parte

( ) Ignorar planejamento

[ Responder ]

Feedback:

"Guardar parte da renda ajuda na construção
da reserva de emergência."

Pontuação: +20

Nível:
Iniciante → Intermediário
```

---

# 🏆 7. Sistema de Progressão

## Pontuação

* Quiz → +10 pontos por acerto
* Jogo → +20, +30 ou +50 pontos por fase

---

## Níveis

| Pontuação | Nível         |
| --------- | ------------- |
| 0–49      | Iniciante     |
| 50–99     | Intermediário |
| 100+      | Avançado      |

---

## Conquistas

* 🎯 Primeira conquista
* 🏆 100 pontos
* 🚀 Jornada completa

---

## Ranking

Exibe os cinco usuários com maior pontuação.

---

# 🎧 8. Recursos de Acessibilidade

A plataforma foi desenvolvida seguindo princípios de inclusão.

Recursos disponíveis:

* 🔊 Conversão de texto em áudio (gTTS)
* 👵 Linguagem simplificada para idosos
* 🧠 Respostas estruturadas para neurodivergentes
* 👂 Conteúdo textual simplificado
* ♿ Interface acessível

---

# 🧭 9. Considerações Finais

A pasta **assets** possui finalidade exclusivamente documental.

Ela reúne diagramas, mockups, imagens e recursos visuais utilizados para explicar o funcionamento da **BIA Academy Finance**, apoiando apresentações, documentação técnica e o portfólio do projeto.

Toda a implementação da aplicação encontra-se na pasta **`src/`**.

---


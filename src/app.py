import streamlit as st
import json
from pathlib import Path
import ollama
import re
import os
import subprocess
import unicodedata

from gtts import gTTS
import tempfile
import time
from pydub import AudioSegment

from meu_rag import carregar_documentos, criar_indice, buscar_contexto

# ================= CONFIG ================
st.set_page_config(page_title="BIA Academy", layout="wide")

# ================= FUNÇÃO DE NÍVEL==========
def atualizar_nivel():
    if st.session_state.pontuacao >= 100:
        st.session_state.nivel = "Avançado"
    elif st.session_state.pontuacao >= 50:
        st.session_state.nivel = "Intermediário"
    else:
        st.session_state.nivel = "Iniciante"  

# ================= CONQUISTAS =================
def verificar_conquistas():
    conquistas = st.session_state.get("conquistas", set())

    if st.session_state.pontuacao >= 20:
        conquistas.add("🎯 Primeira conquista")

    if st.session_state.pontuacao >= 100:
        conquistas.add("🏆 100 pontos")

    if st.session_state.get("fase", 1) > 3:
        conquistas.add("🚀 Jornada completa")

    st.session_state.conquistas = conquistas

# ================= RANKING =================
def salvar_ranking(nome="Jogador"):
    ranking = st.session_state.get("ranking", [])

    ranking.append({
        "nome": nome,
        "pontuacao": st.session_state.pontuacao
    })

    ranking = sorted(ranking, key=lambda x: x["pontuacao"], reverse=True)[:5]

    st.session_state.ranking = ranking

# ================= CSS ===================
st.markdown("""
<style>

/* ====== FUNDO ====== */
body {
    font-family: 'Segoe UI', sans-serif;
}

/* ====== TÍTULO ====== */
h1 {
    color: #ffffff;
    text-align: center;
}

/* ====== ABAS ====== */
button[data-baseweb="tab"] {
    font-size: 17px !important;
    padding: 12px 24px !important;
    border-radius: 12px 12px 0 0;
}
            
button[data-baseweb="tab"][aria-selected="true"] {
    border-bottom: 4px solid #ff4b4b;
    color: #ff4b4b;
    font-weight: bold;
}
            
/* ====== BOTÕES ====== */
.stButton > button {
    border-radius: 12px;
    padding: 10px 18px;
    background-color: #262730;
    color: white;
    border: 1px solid #444;
}

.stButton > button:hover {
    background-color: #ff4b4b;
}

/* ====== CHAT ====== */
[data-testid="stChatMessage"] {
    background-color: #1e1e1e;
    padding: 12px;
    border-radius: 12px;
    margin-bottom: 8px;
}

/* ====== INPUT ====== */
textarea {
    border-radius: 10px !important;
}

/* ====== MÉTRICAS ====== */
[data-testid="stMetric"] {
    background-color: #1e1e1e;
    padding: 6px !important;
    border-radius: 12px;
}

/* 🔽 NÚMEROS (Pontuação) */
[data-testid="stMetricValue"] {
    font-size: 20px !important;
    font-weight: 600 !important;
    line-height: 1.2 !important;
}

/* 🔽 TEXTO (Nível / Pontuação) */
[data-testid="stMetricLabel"] {
    font-size: 13px !important;
    color: #aaa !important;
}

</style>
""", unsafe_allow_html=True)

# ================= TÍTULO =================
st.markdown("""
<h1>💡 Academia de Finanças da BIA 🎓</h1>
""", unsafe_allow_html=True)

# ================= INTR ===================
st.markdown("""
<div style="font-size:16px; line-height:1.7">

<h3>👋 Bem-vindo(a) à BIA Academy Finance</h3>

<p>Olá! Sou sua educadora financeira inclusiva.</p>

<p>
Juntos iremos aprender sobre Investimentos de forma simples, acessível e divertido!  
Estou aqui para te apoiar cada passo da sua jornada.
</p>

</div>
""", unsafe_allow_html=True)


st.markdown("""
<div style="font-size:16px; margin-top:10px">

💬 <b>Conversar</b><br>
🧠 <b>Quiz</b><br>
🎮 <b>Jogo interativo</b>

</div>
""", unsafe_allow_html=True)

# ================= ESTADO ==================
if "pontuacao" not in st.session_state:
    st.session_state.pontuacao = 0

if "nivel" not in st.session_state:
    st.session_state.nivel = "Iniciante"

if "fase" not in st.session_state:
    st.session_state.fase = 1

if "messages" not in st.session_state:
    st.session_state.messages = []

if "publico" not in st.session_state:
    st.session_state.publico = "Investidor iniciante"

# ================= DADOS ==================
DATA_PATH = Path("data")

with open(DATA_PATH / "Quizzes_investimentos.json", "r", encoding="utf8") as f:
    quizzes = json.load(f)

with open(DATA_PATH / "Jogos_inclusivos.json", "r", encoding="utf8") as f:
    jogos = json.load(f)

# ================= RAG ===================
@st.cache_resource(show_spinner="🔎 Carregando inteligência da BIA...")
def carregar_rag_base():
    docs = carregar_documentos()
    idx = criar_indice(docs)
    return docs, idx

# 🚀 evita recriação no fluxo do app
if "rag" not in st.session_state:
    documentos, indice = carregar_rag_base()
    st.session_state.rag = {
        "documentos": documentos,
        "indice": indice
    }

documentos = st.session_state.rag["documentos"]
indice = st.session_state.rag["indice"]

# ================= BIBLIOTECA =============
biblioteca = {
    "liquidez": "Liquidez é a facilidade de transformar um ativo em dinheiro disponível.",
    "diversificação": "Distribuir os recursos investindo em vários ativos, essa prática reduz os riscos.",
    "reserva": "Reserva é dinheiro guardado para emergências.",
    "inflação": """Inflação é quando os preços dos produtos e serviços aumentam ao longo do tempo.
Isso faz com que o dinheiro perca poder de compra.
Por exemplo: com R$ 100,00 hoje você compra mais coisas do que compraria no futuro.""",
    "cdb": "CDB é um investimento onde você empresta dinheiro ao banco e recebe juros.",
    "fii": "FII são fundos que investem em imóveis e distribuem renda.",
    "renda variável": "São investimentos cujo valor pode variar, como ações.",
    "rentabilidade": "É o ganho obtido com um investimento ao longo do tempo.",
}

# ================ PROMPT FINAL =============
def gerar_prompt(pergunta, contexto, publico):

    adaptacao = {
    "Investidor iniciante": "Explique de forma simples, com exemplos do dia a dia.",
    "Idoso": "Use linguagem calma, clara e exemplos práticos do cotidiano.",
    "Deficiência visual": "Descreva os conceitos de forma clara e detalhada, facilitando a compreensão por áudio.",
    "Deficiência auditiva": "Seja direto, objetivo e use frases bem claras.",
    "Neurodivergente": "Explique de forma progressiva, lógica e com frases curtas, mantendo uma sequência previsível."
}

    instrucao_publico = adaptacao.get(publico, "Seja clara, acessível e objetiva.")
    contexto = contexto if contexto else "Sem contexto adicional."

    return f"""
```

Você é a Bia Academy Finance, uma educadora financeira inclusiva.

🎯 OBJETIVO:
Ensinar educação financeira de forma clara, prática e acessível.

🧠 PERFIL DO USUÁRIO:
{publico}

📌 ADAPTAÇÃO DE LINGUAGEM:
{instrucao_publico}

📚 CONTEXTO:
{contexto}

❓ PERGUNTA:
{pergunta}

Responda explicando conceitos financeiros de forma simples, sem recomendar investimentos.
Use linguagem clara, frases curtas e exemplos em reais.

📖 COMO RESPONDER:

Sempre seguir esta sequência natural:

1. O que é o conceito
2. Como impacta a vida real
3. Um exemplo simples com valores em R$

---

🧩 FORMATO DA RESPOSTA:

* 2 a 4 parágrafos
* Cada parágrafo com no máximo 3 frases
* Separar parágrafos com linha em branco
* Não usar listas, números ou títulos
* Não usar "Etapa", "Passo", etc

---

💰 FORMATAÇÃO MONETÁRIA:

* Sempre usar: R$ 0,00
* Nunca separar "R$" do valor
* Usar vírgula para centavos

---

🚫 PROIBIDO:

* Não recomendar investimentos
* Não sugerir escolhas
* Não gerar perguntas
* Não gerar quiz
* Não usar alternativas (a, b, c, d)
* Não repetir a pergunta
* Não começar com saudação

---

🧠 ESTILO:

* Frases curtas
* Linguagem simples
* Explicação direta
* Começar direto no conteúdo

---

🎧 OTIMIZAÇÃO PARA ÁUDIO:

* Evitar frases longas
* Criar pausas naturais
* Manter fluidez
* Não quebrar raciocínio no meio
* Finalizar ideias completas

---

🧩 ADAPTAÇÃO FINAL POR PÚBLICO:

👤 Iniciante → simplicidade + exemplos
👵 Idoso → clareza + cotidiano
👁️ Visual → descrição detalhada
👂 Auditivo → objetividade
🧠 Neurodivergente → sequência lógica e previsível

---

🔒 REGRA FINAL ABSOLUTA:

Você é uma educadora, não uma consultora.
Seu papel é ensinar, nunca recomendar.

Se houver qualquer risco de violar isso, NÃO responda normalmente — aplique as regras de bloqueio.
"""

# ================= FORMATAÇÃO VISUAL =================
def formatar_resposta_html(texto: str) -> str:

    if not texto:
        return ""

    paragrafos = [p.strip() for p in texto.split("\n\n") if p.strip()]

    html = ""

    for p in paragrafos:
        html += f"""
        <div style="
            margin-bottom:16px;
            padding:12px 16px;
            background-color:#262730;
            border-radius:10px;
        ">
            <span style="
                color:#EAEAEA;
                font-size:16px;
                line-height:1.7;
                display:block;
            ">
                {p}
            </span>
        </div>
        """

    return html
# ================= AVALIAÇÃO =============
def avaliar_resposta(resposta):

    texto = resposta.lower()

    # 🎯 Assertividade
    if len(texto.split()) > 40:
        assertividade = "Alta"
    else:
        assertividade = "Média"

    # 🔐 Segurança
    palavras_risco = [
    "invista", "investir", "investe",
    "compre", "comprar",
    "lucro garantido",
    "melhor investimento",
    "vale a pena"
]

    if any(p in texto for p in palavras_risco):
        seguranca = "Baixa"
    else:
        seguranca = "Alta"

    # 🤗 Inclusividade
    palavras_inclusivas = ["exemplo", "simples", "passo", "claro", "vamos"]

    if any(p in texto for p in palavras_inclusivas):
        inclusividade = "Alta"
    else:
        inclusividade = "Média"

    return {
        "assertividade": assertividade,
        "seguranca": seguranca,
        "inclusividade": inclusividade
    }

# ================= LIMPEZA DE TEXTO =================
def limpar_texto(texto: str) -> str:

    if not texto:
        return ""

    texto = texto.strip()

 # ================= 🔥 1. REMOVE SAUDAÇÕES =================
    texto = re.sub(
        r'^(olá|ola|oi|olá!|oi!|bom dia|boa tarde|boa noite)[,!\s]*',
        '',
        texto,
        flags=re.IGNORECASE
    )

 # ================= 🔹 2. CORRIGE QUEBRA DE PALAVRA =================
    texto = re.sub(r'(\w)\n(\w)', r'\1\2', texto)

# ================= 🔹 3. NORMALIZA QUEBRAS =================
    texto = texto.replace('\r', '')
    texto = re.sub(r'\n{3,}', '\n\n', texto)

# ================= 💰 4. CORREÇÃO DE MOEDA =================

    # Garante espaço correto
    texto = re.sub(r'R\$\s*(\d)', r'R$ \1', texto)

    # Corrige "R 50" → "R$ 50"
    texto = re.sub(r'\bR\s+(\d)', r'R$ \1', texto)

    # Corrige "50 reais" → "R$ 50"
    texto = re.sub(r'(\d+,\d{2})\s*reais', r'R$ \1', texto)

    # Corrige quebra tipo:
    # R$
    # 50
    texto = re.sub(r'R\$\s*\n\s*(\d)', r'R$ \1', texto)

    # 🔥 REMOVE "R" SOLTO (CRÍTICO)
    texto = re.sub(r'\bR\b(?=\s*$)', '', texto)

# ================= 🧹 5. LIMPEZA CONTROLADA =================

    # Espaços múltiplos (SEM quebrar parágrafo)
    texto = re.sub(r'[ \t]+', ' ', texto)

    # Espaço após pontuação
    texto = re.sub(r'([.,!?])([A-Za-zÀ-ÿ])', r'\1 \2', texto)

    # Remove repetição de palavras
    texto = re.sub(r'\b(\w+)( \1\b)+', r'\1', texto, flags=re.IGNORECASE)

    # Remove títulos markdown
    texto = re.sub(r'^#+\s.*$', '', texto, flags=re.MULTILINE)

# ================= 📚 6. ORGANIZA PARÁGRAFOS =================

    frases = re.split(r'(?<=[.!?])\s+(?=[A-ZÁ-Ú])', texto)

    blocos = []
    for i in range(0, len(frases), 2):
        bloco = ' '.join(frases[i:i+2]).strip()
        if bloco:
            blocos.append(bloco)

    texto = '\n\n'.join(blocos)

# ================= 🔍 7. VALIDAÇÃO FINAL DE MOEDA =================
    def moeda_valida(t):
        erros = [
            r'\bR\s+\d',
            r'R\$\d',
            r'R\$\s*\n',
            r'\bR\s*$'
        ]
        return not any(re.search(e, t) for e in erros)

    if not moeda_valida(texto):
        texto = re.sub(r'R\$\s*(\d)', r'R$ \1', texto)
        texto = re.sub(r'\bR\s+(\d)', r'R$ \1', texto)
        texto = re.sub(r'(\d+,\d{2})\s*reais', r'R$ \1', texto)

# ================= 🎯 8. FINALIZAÇÃO =================

    texto = texto.strip()

    # Garante pontuação final
    if texto and not texto.endswith(('.', '!', '?')):
        texto += '.'

    # Fallback seguro
    if not texto:
        return "Não consegui gerar uma resposta adequada. Pode tentar reformular?"

    return texto

# ================= NORMALIZAÇÃO =================
def normalizar(texto: str) -> str:
    if not texto:
        return ""

    texto = texto.lower()

    texto = unicodedata.normalize("NFD", texto)
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")

    return texto

# ================= CLASSIFICAÇÃO DE PERGUNTA =================
def classificar_pergunta(pergunta: str) -> str:

    # 🔥 CORREÇÃO CRÍTICA
    if not pergunta:
        return "vazia"

    p = pergunta.lower()

    recomendacao = [
        "qual investimento", "onde investir", "melhor investimento",
        "vale a pena investir", "o que você recomenda", "em que investir",
        "qual devo escolher", "onde aplicar"
    ]

    fora_escopo = [
        "previsão do tempo", "clima", "tempo hoje",
        "futebol", "jogo", "política", "receita", "comida"
    ]

    produto = [
        "xyz", "ação", "empresa", "fundo", "cdb do banco x",
        "tesouro específico", "produto x"
    ]

    if any(f" {k} " in f" {p} " for k in recomendacao):
        return "recomendacao"

    elif any(f" {k} " in f" {p} " for k in fora_escopo):
        return "fora_escopo"

    elif any(f" {k} " in f" {p} " for k in produto):
        return "produto_desconhecido"

    return "normal"

# ================= EXPLICAÇÃO QUIZ (IA + RAG) =============
def gerar_explicacao_quiz_rag(pergunta, opcoes, correta, resposta_usuario, publico):

    contexto = buscar_contexto(pergunta, documentos, indice)

    prompt = f"""
    Você é uma educadora financeira inclusiva.

    CONTEXTO:
    {contexto}

    PERGUNTA:
    {pergunta}

    OPÇÕES:
    {opcoes}

    RESPOSTA CORRETA:
    {correta}

    RESPOSTA DO USUÁRIO:
    {resposta_usuario}

    PÚBLICO:
    {publico}

    EXPLIQUE:
    - Por que a correta está certa
    - Por que as outras estão erradas
    - Use exemplos simples do dia a dia
    - Seja didática e acessível
    """

    resposta = ollama.chat(
        model="gemma3:4b",
        messages=[{"role": "user", "content": prompt}]
    )

    return resposta["message"]["content"]

# ================= ABAS =================
tab1, tab2, tab3 = st.tabs([
    "💬 CONVERSA",
    "🧠 QUIZ",
    "🎮 JOGO"
])

# ================= 🔊 ÁUDIO ÚNICO =================
def gerar_audio_unico(texto):
    try:
        if not texto:
            return None

        # 🔥 LIMPEZA PESADA
        texto_limpo = (
            texto
            .replace("\n", " ")
            .replace("  ", " ")
            .strip()
        )

        texto_limpo = re.sub(r'\s+', ' ', texto_limpo)

        # 🔥 GARANTE FINALIZAÇÃO
        if not texto_limpo.endswith(('.', '!', '?')):
            texto_limpo += '.'

        # 🔥 DIVIDE EM PARTES SEGURAS (ANTI CORTE DO gTTS)
        partes = []
        max_chars = 400  # limite seguro

        while len(texto_limpo) > max_chars:
            corte = texto_limpo[:max_chars]

            # tenta cortar em ponto final (mais natural)
            ultimo_ponto = corte.rfind(".")
            if ultimo_ponto != -1:
                partes.append(texto_limpo[:ultimo_ponto + 1])
                texto_limpo = texto_limpo[ultimo_ponto + 1:].strip()
            else:
                partes.append(corte)
                texto_limpo = texto_limpo[max_chars:].strip()

        if texto_limpo:
            partes.append(texto_limpo)

        # 🔥 GERA E JUNTA ÁUDIO
        audios = []
        arquivos_temp = []

        for parte in partes:
            tts = gTTS(text=parte, lang='pt-br', slow=False)

            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
            tmp.close()

            tts.save(tmp.name)
            arquivos_temp.append(tmp.name)

            audio = AudioSegment.from_file(tmp.name)
            audios.append(audio)

        # 🚨 PROTEÇÃO CONTRA ERRO
        if not audios:
            return None

        # 🔥 CONCATENA TUDO (ÁUDIO ÚNICO REAL)
        audio_final = audios[0]
        for a in audios[1:]:
            audio_final += a

        arquivo_final = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        arquivo_final.close()

        audio_final.export(arquivo_final.name, format="mp3")

        # 🧹 LIMPA TEMPORÁRIOS
        for arq in arquivos_temp:
            try:
                os.unlink(arq)
            except:
                pass

        return arquivo_final.name

    except Exception as e:
        print("Erro no áudio único:", e)
        return None
    
# ================= CHAT ================= 
with tab1:

    import time  # 🔥 necessário para métricas

    # 🎯 Público
    opcoes_publico = [
        "Investidor iniciante",
        "Idoso",
        "Deficiência auditiva",
        "Deficiência visual",
        "Neurodivergente"
    ]

    st.session_state.publico = st.selectbox(
        "Selecione o público:",
        opcoes_publico,
        index=opcoes_publico.index(st.session_state.publico)
    )

    # ================= 🔊 CONTROLE DE ÁUDIO =================
    if "audio_gerado" not in st.session_state:
        st.session_state.audio_gerado = False

    if "audio_path" not in st.session_state:
        st.session_state.audio_path = None

    if "ultima_resposta" not in st.session_state:
        st.session_state.ultima_resposta = ""

    if "metricas" not in st.session_state:
        st.session_state.metricas = {}

    # ================= 💬 INPUT =================
    pergunta = st.chat_input("Pergunte sobre investimentos")

    if pergunta:

        # 🔥 RESET DO ÁUDIO
        st.session_state.audio_gerado = False
        st.session_state.audio_path = None

        resposta_texto = ""

        # 💬 Mostra pergunta
        with st.chat_message("user"):
            st.markdown(pergunta)

        # ================= 🧠 CLASSIFICAÇÃO =================
        tipo = classificar_pergunta(pergunta)

        # ================= 🚫 BLOQUEIOS =================
        if tipo == "recomendacao":
            resposta_texto = "Sou uma educadora financeira, e posso apenas ajudar você a entender sobre investimentos."
            tempo_rag = tempo_modelo = tempo_total = 0

        elif tipo == "fora_escopo":
            resposta_texto = "Eu sou a Bia Academy, uma educadora financeira. Só posso responder sobre investimentos e educação financeira."
            tempo_rag = tempo_modelo = tempo_total = 0

        elif tipo == "produto_desconhecido":
            resposta_texto = "Eu não encontrei informações sobre esse produto nos materiais de apoio. Recomendo que verifique no site da CVM ou no da B3."
            tempo_rag = tempo_modelo = tempo_total = 0

        # ================= 🧠 FLUXO NORMAL =================
        else:

            # ================= 🔎 BUSCA LOCAL =================
            contexto_local = None
            contextos_encontrados = []

            pergunta_norm = normalizar(pergunta)

            for termo, conteudo in biblioteca.items():
                if normalizar(termo) in pergunta_norm:
                    contextos_encontrados.append(conteudo)

            if contextos_encontrados:
                contexto_local = " ".join(contextos_encontrados)

            # fallback leve
            if not contexto_local:
                for termo, conteudo in biblioteca.items():
                    if any(p in normalizar(termo) for p in pergunta_norm.split()):
                        contexto_local = conteudo
                        break

            # ================= ⏱️ MÉTRICA RAG =================
            t0 = time.time()

            contexto_rag = None
            try:
                contexto_rag = buscar_contexto(pergunta, documentos, indice)

                print("\n========== DEBUG RAG ==========")
                print("Pergunta:", pergunta)

                if contexto_rag:
                    print("Contexto encontrado:")
                    print(contexto_rag[:500])
                else:
                    print("⚠️ RAG NÃO RETORNOU NADA")

                print("================================\n")

            except Exception as e:
                print("❌ Erro no RAG:", e)
                contexto_rag = None

            t1 = time.time()
            tempo_rag = t1 - t0

            # ================= 🔗 COMBINAÇÃO =================
            if contexto_local and contexto_rag:
                contexto = f"""Base interna:
{contexto_local}

Base aprofundada:
{contexto_rag}"""

            elif contexto_local:
                contexto = contexto_local

            elif contexto_rag:
                contexto = contexto_rag

            else:
                contexto = None

            # ================= 🚫 SEM CONTEXTO =================
            if not contexto:
                resposta_texto = "Ainda não tenho conteúdo educativo suficiente sobre esse tema."
                tempo_modelo = 0
                tempo_total = tempo_rag

            else:
                prompt = gerar_prompt(pergunta, contexto, st.session_state.publico)

                # ================= ⏱️ MÉTRICA MODELO =================
                t2 = time.time()

                try:
                    resposta = ollama.chat(
                        model="gemma3:4b",
                        messages=[{"role": "user", "content": prompt}],
                        options={
                            "num_predict": 500,
                            "temperature": 0.2,
                            "top_p": 0.9,
                            "repeat_penalty": 1.1
                        }
                    )

                    resposta_texto = resposta["message"]["content"]

                except Exception as e:
                    st.error("⚠️ Erro ao gerar resposta. Tente novamente.")
                    print("Erro no modelo:", e)
                    resposta_texto = "⚠️ Tive um problema ao responder. Pode tentar novamente?"

                t3 = time.time()
                tempo_modelo = t3 - t2

                # ================= 🧹 LIMPEZA =================
                resposta_texto = limpar_texto(resposta_texto)

                if not resposta_texto.strip():
                    resposta_texto = "Não consegui gerar uma resposta adequada. Pode tentar reformular?"

                if not resposta_texto.endswith(('.', '!', '?')):
                    resposta_texto += '.'

                # ================= ⏱️ TOTAL =================
                tempo_total = time.time() - t0

        # ================= 💾 SALVA =================
        st.session_state.ultima_resposta = resposta_texto

        st.session_state.metricas = {
            "tempo_rag": tempo_rag,
            "tempo_modelo": tempo_modelo,
            "tempo_total": tempo_total
        }

        # ================= 💬 EXIBE =================
        with st.chat_message("assistant"):
            html_formatado = formatar_resposta_html(resposta_texto)
            st.markdown(html_formatado, unsafe_allow_html=True)

            # ================= 📊 MÉTRICAS VISUAIS =================
            col1, col2, col3 = st.columns(3)

            col1.metric("⏱️ Tempo RAG", f"{tempo_rag:.2f}s")
            col2.metric("🧠 Tempo IA", f"{tempo_modelo:.2f}s")
            col3.metric("⚡ Tempo Total", f"{tempo_total:.2f}s")

        # ================= 🔊 ÁUDIO =================
        if st.session_state.publico == "Deficiência visual":

            if not st.session_state.audio_gerado:
                audio_path = gerar_audio_unico(st.session_state.ultima_resposta)

                if audio_path:
                    st.session_state.audio_path = audio_path
                    st.session_state.audio_gerado = True

            if st.session_state.audio_path:
                st.audio(st.session_state.audio_path)
            else:
                st.info("🔇 Áudio indisponível.")

# ================= QUIZ =================
with tab2:

    # ===== CONTROLE DE ESTADO =====
    if "quiz_index" not in st.session_state:
        st.session_state.quiz_index = 0

    if "respondeu" not in st.session_state:
        st.session_state.respondeu = False

    if "resposta_usuario" not in st.session_state:
        st.session_state.resposta_usuario = None

    if "pontuacao" not in st.session_state:
        st.session_state.pontuacao = 0

    if "nivel" not in st.session_state:
        st.session_state.nivel = "Iniciante"

    quiz = quizzes[st.session_state.quiz_index]

    # ===== PERGUNTA =====
    st.subheader(quiz["pergunta"])

    # ===== OPÇÕES =====
    if not st.session_state.respondeu:

        for i, opcao in enumerate(quiz["opcoes"]):
            if st.button(opcao, key=f"quiz_{st.session_state.quiz_index}_{i}"):

                st.session_state.respondeu = True
                st.session_state.resposta_usuario = opcao

                if opcao == quiz["resposta_correta"]:
                    st.success("🤗 Isso mesmo! Você está aprendendo!")
                    st.session_state.pontuacao += 10
                else:
                    st.error("💡 Quase! Vamos aprender juntos.")

                atualizar_nivel()
                st.rerun()

    # ===== FEEDBACK =====
    if st.session_state.respondeu:

        st.markdown(f"### ✔ Resposta correta: {quiz['resposta_correta']}")

        # 🧠 IA + RAG (com cache)
        @st.cache_data(show_spinner=False)
        def gerar_explicacao_cache(pergunta, opcoes, correta, resposta_usuario, publico):
            return gerar_explicacao_quiz_rag(
                pergunta, opcoes, correta, resposta_usuario, publico
            )

        with st.spinner("🧠 Gerando explicação inteligente..."):
            explicacao = gerar_explicacao_cache(
                quiz["pergunta"],
                quiz["opcoes"],
                quiz["resposta_correta"],
                st.session_state.resposta_usuario,
                st.session_state.publico
            )

        # 📊 AVALIAÇÃO
        avaliacao = avaliar_resposta(explicacao)

        # 🔧 MELHORIA AUTOMÁTICA 
        if avaliacao.get("assertividade") in ["Média", "Baixa"]:
            explicacao += "\n\n💡 Vou simplificar: pense nisso como uma decisão do dia a dia envolvendo seu dinheiro."

        # ✅ AGORA MOSTRA A VERSÃO FINAL
        st.info(explicacao)

        # 🧠 REFLEXÃO
        st.markdown("💭 **Dica:** Pense no impacto dessa decisão no seu futuro financeiro.")

        # ===== PRÓXIMA =====
        if st.button("➡ Próxima pergunta"):

            st.session_state.quiz_index += 1
            st.session_state.respondeu = False

            # 🔁 Reinicia quando acabar
            if st.session_state.quiz_index >= len(quizzes):
                st.success("🎉 Você concluiu o quiz!")
                st.session_state.quiz_index = 0

            st.rerun()

    # ===== PROGRESSO (QUIZ) =====
    st.divider()
    st.metric("Pontuação", st.session_state.pontuacao)
    st.metric("Nível", st.session_state.nivel)
    st.progress(min(st.session_state.pontuacao / 150, 1.0))  

# ================= JOGO EVOLUÍDO =================
with tab3:

    st.subheader("🎮 Jornada Evolutiva")

    # 🔒 Estado
    if "fase" not in st.session_state:
        st.session_state.fase = 1

    if "pontuacao" not in st.session_state:
        st.session_state.pontuacao = 0

    if "resposta_jogo" not in st.session_state:
        st.session_state.resposta_jogo = None

    if "respondido_jogo" not in st.session_state:
        st.session_state.respondido_jogo = False

    if "nivel" not in st.session_state:
        st.session_state.nivel = "Iniciante"

    if "conquistas" not in st.session_state:
        st.session_state.conquistas = set()

    # ================= FASES COM DIFICULDADE =================
    fases = {
        1: {
            "nivel": "facil",
            "pergunta": "Você recebeu seu salário. O que fazer primeiro?",
            "opcoes": ["Gastar tudo", "Guardar parte", "Ignorar planejamento"],
            "correta": "Guardar parte",
            "pontos": 20,
            "explicacao": "Guardar cria base financeira."
        },
        2: {
            "nivel": "medio",
            "pergunta": "Qual estratégia reduz risco?",
            "opcoes": ["Tudo em 1 investimento", "Diversificar", "Apostar tudo"],
            "correta": "Diversificar",
            "pontos": 30,
            "explicacao": "Diversificação protege seu dinheiro."
        },
        3: {
            "nivel": "dificil",
            "pergunta": "Qual prioridade financeira?",
            "opcoes": ["Consumo imediato", "Reserva de emergência", "Evitar planejamento"],
            "correta": "Reserva de emergência",
            "pontos": 50,
            "explicacao": "Reserva evita dívidas."
        }
    }

    total_fases = len(fases)
    fase_atual = fases[st.session_state.fase]

    # ================= UI =================
    st.markdown(f"### 🧩 Fase {st.session_state.fase}")
    st.write(fase_atual["pergunta"])

    escolha = st.radio(
        "Escolha:",
        fase_atual["opcoes"],
        index=None,
        key=f"jogo_{st.session_state.fase}"
    )

    # ================= RESPOSTA =================
    if not st.session_state.respondido_jogo:

        if st.button("Responder", disabled=(escolha is None)):

            st.session_state.resposta_jogo = escolha
            st.session_state.respondido_jogo = True

            if escolha == fase_atual["correta"]:
                st.success("✅ Boa decisão!")
                st.session_state.pontuacao += fase_atual["pontos"]

            else:
                st.error("❌ Vamos melhorar na próxima!")

                # 🔥 DIFICULDADE ADAPTATIVA
                if st.session_state.fase > 1:
                    st.session_state.fase -= 1

            atualizar_nivel()
            verificar_conquistas()

            st.rerun()

    # ================= FEEDBACK =================
    else:
        st.info(f"💡 {fase_atual['explicacao']}")

        if st.button("➡️ Próxima fase"):

            if st.session_state.fase < total_fases:
                st.session_state.fase += 1
                st.session_state.resposta_jogo = None
                st.session_state.respondido_jogo = False
                st.rerun()

            else:
                st.success("🎉 Jornada concluída!")

                salvar_ranking()

                st.write(f"🏆 Pontuação: {st.session_state.pontuacao}")
                st.write(f"📊 Nível: {st.session_state.nivel}")

                # 🏆 CONQUISTAS
                st.markdown("### 🏆 Conquistas")
                for c in st.session_state.conquistas:
                    st.write(c)

                # 🥇 RANKING
                st.markdown("### 🥇 Ranking")
                for i, r in enumerate(st.session_state.ranking, 1):
                    st.write(f"{i}. {r['nome']} - {r['pontuacao']} pts")

                if st.button("🔄 Jogar novamente"):
                    st.session_state.fase = 1
                    st.session_state.pontuacao = 0
                    st.session_state.resposta_jogo = None
                    st.session_state.respondido_jogo = False
                    st.session_state.nivel = "Iniciante"
                    st.session_state.conquistas = set()
                    st.rerun()

    # ================= HUD =================
    st.divider()

    progresso = (st.session_state.fase - 1) / total_fases

    st.metric("Pontuação", st.session_state.pontuacao)
    st.metric("Nível", st.session_state.nivel)
    st.progress(progresso)

# ================= AVISO =================
st.markdown("""
<div style="
background-color:#111;
padding:15px;
border-radius:10px;
border-left:5px solid #f1c40f;
margin-top:10px;
">

<div style="color:#f1c40f; font-weight:bold; font-size:16px;">
⚠️ Aviso Importante
</div>

<div style="color:#ccc; margin-top:8px; font-size:14px;">
A <b>BIA Academy Finance</b> não é uma consultoria financeira.<br><br>
O meu objetivo é apenas <b>educação financeira</b>, explicando conceitos e opções de investimentos.<br><br>
Não realizamos recomendações, não calculamos rentabilidades e não analisamos cenários econômicos.<br><br>

😊 Esperamos ter ajudado!
</div>

</div>
""", unsafe_allow_html=True)




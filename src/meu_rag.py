from pathlib import Path
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss
import streamlit as st
import re

# ---------------- MODELO ----------------
@st.cache_resource
def carregar_modelo():
    try:
        modelo = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        return modelo
    except Exception as e:
        st.error("❌ Erro ao carregar modelo de embeddings")
        print("Erro ao carregar modelo:", e)
        return None

model = carregar_modelo()

# ---------------- LIMPEZA DE TEXTO ----------------
def limpar_texto_rag(texto):
    texto = texto.replace("\n", " ")
    texto = re.sub(r'\s+', ' ', texto)

    # remove caracteres estranhos
    texto = re.sub(r'[^\w\s.,!?À-ÿR$]', '', texto)

    return texto.strip()

# ---------------- CHUNK INTELIGENTE ----------------
def dividir_em_chunks(texto, tamanho=500):
    palavras = texto.split()
    chunks = []
    chunk_atual = []
    tamanho_atual = 0

    for palavra in palavras:
        tamanho_atual += len(palavra) + 1
        chunk_atual.append(palavra)

        if tamanho_atual >= tamanho:
            chunks.append(" ".join(chunk_atual))
            chunk_atual = []
            tamanho_atual = 0

    if chunk_atual:
        chunks.append(" ".join(chunk_atual))

    return chunks

# ---------------- CARREGAR DOCUMENTOS ----------------
@st.cache_data(show_spinner=False)
def carregar_documentos(pasta="data"):
    docs = []

    for arquivo in Path(pasta).glob("*"):
        if arquivo.suffix in [".txt", ".md"]:
            try:
                with open(arquivo, "r", encoding="utf8") as f:
                    texto = f.read()

                    # 🔥 limpeza
                    texto = limpar_texto_rag(texto)

                    # 🔥 chunk inteligente
                    chunks = dividir_em_chunks(texto)

                    for chunk in chunks:
                        if len(chunk.strip()) > 30:  # evita lixo pequeno
                            docs.append({
                                "conteudo": chunk,
                                "fonte": arquivo.name
                            })

            except Exception as e:
                print(f"Erro ao ler {arquivo}: {e}")

    return docs

# ---------------- CRIAR ÍNDICE ----------------
@st.cache_resource(show_spinner=False)
def criar_indice(documentos):

    # 🚨 VALIDAÇÃO 1 — documentos
    if not documentos:
        raise ValueError("Nenhum documento carregado para o RAG.")

    # 🚨 VALIDAÇÃO 2 — modelo
    if model is None:
        raise ValueError("Modelo de embeddings não carregado.")

    textos = [doc["conteudo"] for doc in documentos]

    embeddings = model.encode(
        textos,
        batch_size=32,
        show_progress_bar=True,
        normalize_embeddings=True
    )

    dim = embeddings.shape[1]

    index = faiss.IndexFlatIP(dim)
    index.add(np.array(embeddings).astype("float32"))

    return {
        "index": index,
        "documentos": documentos
    }

# ---------------- BUSCAR CONTEXTO ----------------
def buscar_contexto(pergunta, documentos, indice, top_k=3):

    try:
        pergunta_vec = model.encode(
            [pergunta],
            normalize_embeddings=True
        )

        distancias, indices = indice["index"].search(
            np.array(pergunta_vec).astype("float32"),
            top_k
        )

        contextos = []

        for i in indices[0]:
            if i < len(documentos):
                doc = documentos[i]
                contexto = f"[Fonte: {doc['fonte']}]\n{doc['conteudo']}"
                contextos.append(contexto)

        if not contextos:
            return "Sem contexto relevante encontrado."

        # 🔥 separador melhorado
        return "\n\n---\n\n".join(contextos)

    except Exception as e:
        print("Erro no RAG:", e)
        return None
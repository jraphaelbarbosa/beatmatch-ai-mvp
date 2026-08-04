# 🎧 BeatMatchAI (MVP)

> **[ 🇺🇸 Read in English ](README.md)**

**Sistema de Matching de Identidade Sonora para Produtores Musicais**

O BeatMatchAI é uma ferramenta inteligente desenvolvida para otimizar a prospecção de artistas por produtores musicais. Ele utiliza Agentes de IA avançados para ouvir seus beats, analisar seu "DNA Sonoro" e pareá-los com os artistas mais adequados do seu banco de dados.

Chega de enviar DMs às cegas. Deixe a IA encontrar o encaixe perfeito para o seu som.

## 🚀 Principais Recursos

* **Análise de DNA Sonoro:**
    * Utiliza o **Google Gemini 2.5 Flash** (via LangChain) para ouvir e processar arquivos de áudio.
    * Extrai Estilo (Trap, Drill, Boombap, etc.), Vibe (Dark, Chill, Hype) e BPM.
    * Gera uma descrição musical rica e detalhada da faixa.
* **Matching Inteligente de Artistas:**
    * Compara o "DNA Sonoro" analisado com seu banco de dados/CRM de artistas.
    * (MVP) Filtra artistas com base na compatibilidade de Estilo e Vibe.
* **Assistente de Prospecção (Outreach):**
    * Gera automaticamente mensagens de pitch personalizadas (DMs do Instagram / E-mails) com base nas características do beat.

## 🛠️ Tecnologias Utilizadas (Tech Stack)

* **Interface (Frontend):** Streamlit
* **Motor de IA:** LangChain + Google Gemini 2.5 Flash (`langchain-google-genai`)
* **Linguagem:** Python 3.10+

## ⚙️ Configuração e Instalação

1.  **Clonar o repositório:**
    ```bash
    git clone https://github.com/jraphaelbarbosa/beatmatch-ai-mvp.git
    cd beatmatch-ai-mvp
    ```

2.  **Instalar dependências:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Variáveis de Ambiente:**
    Crie um arquivo `.env` na raiz do projeto e adicione sua chave do Google AI Studio:
    ```env
    AUDIO_AGENT_API_KEY=sua_chave_api_google_aqui
    ```

4.  **Executar a Aplicação:**
    ```bash
    streamlit run src/app.py
    ```

## ⚠️ Nota Importante
Este projeto utiliza o modelo **Gemini 2.5 Flash**. Certifique-se de que sua chave de API tenha acesso aos modelos mais recentes do Google Generative AI.

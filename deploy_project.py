import os
import subprocess

# ENGLISH README - FOCUSED ON UTILITY
readme_en = """# Spotify Artist ➡️ Instagram Extractor 📸

> **Turn a list of Spotify Artists into a list of official Instagram contacts.**

[Ler em Português](README.pt-br.md)

## 🎯 What this tool does
If you have a list of musicians on Spotify, you often need to contact them. This tool automates the process of finding their **official Instagram profile** linked in their Spotify bio.

It does **not** guess usernames. It extracts the exact link the artist pinned on their profile.

## ⚙️ How it works (The "Magic")
Traditional scrapers fail on Spotify because of "Lazy Loading" (buttons don't exist until you click them).
**This tool uses Network Interception.** It listens to the hidden JSON traffic between the Spotify Web Player and their API. When you visit an artist page, the tool "steals" the social links from the data stream before the page even loads.

**Input:** A CSV with Spotify Artist IDs.
**Output:** A CSV with verified Instagram URLs.

## 🚀 Key Features
* **100% Verified Links:** Only gets links provided by the artist themselves.
* **Network Interception:** Bypasses UI bugs and layout changes.
* **Batch Processing:** Handles 50k+ artists with session persistence.

## 📦 Installation & Usage
1. `pip install -r requirements.txt`
2. `playwright install chromium`
3. `python src/setup_auth.py` (Login once manually)
4. `python src/extract_instagrams.py` (Run the extractor)

## ⚠️ Disclaimer
For educational and portfolio purposes (BeatMachAI Project).
"""

# PORTUGUESE README - FOCADO NA UTILIDADE
readme_pt = """# Spotify Artist ➡️ Instagram Extractor 📸

> **Transforme uma lista de Artistas do Spotify em uma lista de contatos do Instagram.**

[Read in English](README.md)

## 🎯 O que esta ferramenta faz
Se você tem uma lista de músicos no Spotify, geralmente precisa contatá-los. Esta ferramenta automatiza o processo de encontrar o **perfil oficial do Instagram** linkado na bio do Spotify.

Ela **não** adivinha nomes de usuário. Ela extrai o link exato que o artista fixou em seu perfil.

## ⚙️ Como funciona (A "Mágica")
Scrapers tradicionais falham no Spotify devido ao "Lazy Loading" (botões não existem até você clicar neles).
**Esta ferramenta usa Interceptação de Rede.** Ela escuta o tráfego JSON oculto entre o Spotify Web Player e a API interna. Quando o robô visita a página, ele captura os links sociais do fluxo de dados antes mesmo da página carregar.

**Entrada:** CSV com IDs de Artistas do Spotify.
**Saída:** CSV com URLs verificadas do Instagram.

## 🚀 Principais Recursos
* **Links 100% Verificados:** Apenas links fornecidos pelo próprio artista.
* **Interceptação de Rede:** Ignora bugs de interface e mudanças de layout.
* **Processamento em Lote:** Lida com mais de 50k artistas mantendo a sessão salva.

## 📦 Instalação e Uso
1. `pip install -r requirements.txt`
2. `playwright install chromium`
3. `python src/setup_auth.py` (Login manual único)
4. `python src/extract_instagrams.py` (Rodar o extrator)
"""

gitignore = """
__pycache__/
*.pyc
.env
venv/
.DS_Store
spotify_auth.json
*.csv
data/
logs/
"""

requirements = """
pandas
playwright
python-dotenv
"""

def write_file(name, content):
    with open(name, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    print(f"✅ {name} criado.")

def run_command(command):
    try:
        subprocess.run(command, shell=True, check=True)
        print(f"✅ Executado: {command}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao executar: {command}")
        print(e)

if __name__ == "__main__":
    # 1. Criar Arquivos
    write_file("README.md", readme_en)
    write_file("README.pt-br.md", readme_pt)
    write_file(".gitignore", gitignore)
    write_file("requirements.txt", requirements)
    
    if not os.path.exists("src"):
        os.makedirs("src")
        print("📂 Pasta 'src' garantida.")

    # 2. Executar Git
    print("\\n🤖 Inicializando Git...")
    run_command("git init")
    run_command("git add .")
    run_command('git commit -m "Initial: Spotify to Instagram Extraction Logic"')
    run_command("git branch -M main")
    
    print("\\n🏁 Repositório local pronto!")
    print("Para subir, rode apenas:")
    print("git remote add origin SEU_LINK_DO_GITHUB")
    print("git push -u origin main")

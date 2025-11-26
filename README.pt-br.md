# Spotify Artist ➡️ Instagram Extractor 📸

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
# HospVilarejo - Assistente de Feedback Inteligente para Hotelaria


## 1. Visão Geral do Projeto
**HospVilarejo** é um ecossistema completo de gestão de feedback para o setor hoteleiro, desenhado para transformar a experiência do hóspede de **reativa** para **proativa**.  
Utilizando Inteligência Artificial, a solução permite que a equipa do hotel identifique e resolva problemas **durante a estadia** do cliente, antes que se tornem reclamações públicas e avaliações negativas.

O projeto é composto por dois componentes principais:

- **Bot Assistente (Telegram):** Um chatbot que interage com os hóspedes, analisa as suas mensagens em tempo real e alerta a equipa sobre problemas e solicitações.
- **Painel de BI (Dashboard):** Uma aplicação web que visualiza os dados recolhidos, fornecendo à gestão insights valiosos sobre os principais pontos de atrito na operação do hotel.

---

## 2. O Problema
No modelo tradicional, o feedback é recolhido **no check-out**, quando já é tarde demais para reverter uma experiência negativa.  
Hóspedes insatisfeitos muitas vezes **não comunicam** os problemas, resultando em:

- **Avaliações Negativas Online:** Danos à reputação em plataformas como TripAdvisor e Google.
- **Perda de Fidelização:** Clientes que não retornam.
- **Falta de Dados Estratégicos:** A gestão não consegue identificar as causas-raiz dos problemas de forma sistemática.

---

## 3. Funcionalidades Principais

### Bot Assistente
- **Análise com IA (Google Gemini):** Processa a linguagem natural para identificar **Intenção**, **Sentimento** e **Categoria** de cada solicitação (ex: "Problema no Banheiro", "Solicitação de Itens").
- **Acesso Seguro por Código Único:** Funcionários geram códigos temporários (`/gerar_codigo`) que os hóspedes usam para se autenticar (`/checkin`), garantindo que apenas o utilizador correto aceda à reserva.
- **Alertas em Tempo Real:** Reclamações e pedidos disparam notificações instantâneas para um grupo da equipa, com todos os detalhes necessários para uma ação rápida.
- **Tratamento de Falhas:** Sistema de retentativa e mecanismo de fallback que alerta a equipa manualmente se a análise da IA falhar, garantindo que nenhuma solicitação seja perdida.

### Painel de BI
- **Visualização de Dados:** Gráficos interativos mostram as principais categorias de reclamações, a distribuição geral de sentimentos e o volume de solicitações ao longo do tempo.
- **Tomada de Decisão Estratégica:** Transforma feedback solto em inteligência de negócio, ajudando a gestão a priorizar investimentos em manutenção e treino.
- **Atualização Automática:** Reflete os dados mais recentes, servindo como ferramenta de monitorização em tempo real.

---

## 4. Estrutura do Projeto
```plaintext
HospVilarejo/
|
|-- main.py             # Ponto de entrada para executar o bot
|-- dashboard.py        # Ponto de entrada para executar o painel de BI
|-- config.py           # Armazena chaves de API e configurações
|-- db_manager.py       # Funções para interagir com o banco de dados (SQLite)
|-- ai_analyzer.py      # Módulo de comunicação com a API do Gemini
|-- requirements.txt    # Lista de dependências do projeto
|
|-- bot_handlers/
|   |-- admin_commands.py  # Lógica para comandos de funcionários
|   |-- guest_commands.py  # Lógica para comandos de hóspedes
|   |-- message_handler.py # Lógica para o tratamento de mensagens de texto
```
---

## 5. Tecnologias Utilizadas
- **Backend:** Python  
- **Bot Framework:** [python-telegram-bot](https://python-telegram-bot.org)  
- **Inteligência Artificial:** Google Gemini API (`gemini-1.5-flash`)  
- **Base de Dados:** SQLite  
- **Dashboard:** Dash & Plotly  
- **Análise de Dados:** Pandas  

---

## 6. Como Executar o Projeto

### Pré-requisitos
- Python 3.9 ou superior  
- Chave de API do Google Gemini  
- Token de bot do Telegram  

### Passos para Instalação
Clone o repositório:
```bash
git clone https://github.com/seu-usuario/HospVilarejo.git
cd HospVilarejo
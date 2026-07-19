<div align="center">

# 🤖 Klaus Bot

### Bot multifuncional para Discord com economia, diversao, moderacao e muito mais

[![Discord](https://img.shields.io/badge/Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](https://discord.gg/klaus)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-00ff00?style=for-the-badge)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Online-22C55E?style=for-the-badge)](https://klaus-dashboard-delta.vercel.app)

[Dashboard](https://klaus-dashboard-delta.vercel.app) | [Suporte](https://discord.gg/klaus) | [Invite](https://discord.com/oauth2/authorize)

</div>

---

## 📋 Index

- [Sobre](#-sobre)
- [Features](#-features)
- [Comandos](#-comandos)
- [Instalacao](#-instalacao)
- [Configuracao](#configuracao)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Dashboard](#-dashboard)
- [Tecnologias](#-tecnologias)
- [Contribuindo](#-contribuindo)
- [Licenca](#-licenca)

---

## 🎯 Sobre

O **Klaus Bot** e um bot Discord multifuncional inspirado em bots como Loritta e Mudae. Ele oferece um sistema completo de economia com koins, minigames, moderacao avancada, sistema de perfil personalizavel com gerador de imagens, e muito mais.

### Principais Diferenciais

- **Economia Completa**: 30+ comandos economicos com sistema de moedas (Koins), cofre com juros, investimentos, loteria, e mais
- **Minigames**: Blackjack, slot machine, pedra-papel-tesoura, batalha PvP, corrida, e quiz
- **Perfil Personalizavel**: Gerador de imagens com 100+ temas, bordas e efeitos visuais
- **Moderacao Avancada**: Ban, kick, mute, warn, auto-mod, tickets, e logs
- **Sistema de XP**: Leveling com recompensas por cargo e anuncios de level-up
- **Dashboard Web**: Painel de configuracao completo via navegador
- **Sistema de Pets**: Adote e cuide do seu pet virtual
- **Giveaways**: Sistema completo com botoes persistentes
- **Social**: Sistema de casamento, AFK, e interacoes sociais

---

## ⭐ Features

### 💰 Economia
| Comando | Descricao |
|---------|-----------|
| `/daily` | Recompensa diaria com streak |
| `/weekly` | Recompensa semanal |
| `/trabalhar` | Trabalhe e ganhe koins |
| `/minerar` | Minere koins e minerais raros |
| `/apostar` | Roleta com jackpot |
| `/blackjack` | Blackjack 21 contra o dealer |
| `/slot` | Caca-niquel com multiplicadores |
| `/crime` | Cometa crimes (com chance de prisao) |
| `/heist` | Assalte um banco |
| `/invest` | Invista em cripto, acoes, imoveis ou NFTs |
| `/cofre` | Poupanca com juros de 2% ao hora |
| `/lottery` | Compre tickets da loteria |
| `/case` | Abra cases gacha com raridades |
| `/loja` | Loja com itens especiais |
| `/perfil` | Seu perfil completo com imagem gerada |

### 🎮 Diversao
| Comando | Descricao |
|---------|-----------|
| `/ship` | Calcule compatibilidade com imagem |
| `/hug` `/kiss` `/slap` `/pat` | Interacoes sociais com GIFs |
| `/batalha` | Batalha de dados PvP |
| `/rps` | Pedra, papel ou tesoura |
| `/quiz` | Quiz de conhecimento geral |
| `/aventura` | Aventura de texto com escolhas |
| `/poll` | Enquetas com votacao |
| `/reacao` | Teste seus reflexos |
| `/piada` `/meme` | Piadas e memes aleatorios |
| `/8ball` | Bola 8 magica |

### 🛡️ Moderacao
| Comando | Descricao |
|---------|-----------|
| `/ban` `/kick` | Banir ou expulsar membros |
| `/mute` `/unmute` | Silenciar membros |
| `/warn` `/warnings` | Sistema de advertencias |
| `/lock` `/unlock` | Trancar/destravar canais |
| `/clearchannel` | Limpar mensagens |
| `/nuke` | Nuke um canal |
| `/ticket_panel` | Painel de suporte |
| `/giveaway` | Sistema de sorteios |
| `/add_badword` | Auto-moderacao |

### ⚙️ Utilidades
| Comando | Descricao |
|---------|-----------|
| `/ping` | Latencia do bot |
| `/uptime` | Tempo online |
| `/userinfo` `/whois` | Informacoes de usuarios |
| `/serverinfo` | Informacoes do servidor |
| `/botinfo` | Informacoes do bot |
| `/avatar` | Avatar de membros |
| `/rank` `/xpleaderboard` | Sistema de XP |
| `/reminder` | Lembretes |
| `/calcular` | Calculadora |
| `/embed` | Criar embeds customizados |
| `/dashboard` | Abrir painel web |

---

## 🚀 Instalacao

### Requisitos
- Python 3.11 ou superior
- MongoDB (local ou Atlas)
- Bot Token do Discord

### 1. Clone o repositorio

```bash
git clone https://github.com/ew2k26/klaus-bot.git
cd klaus-bot
```

### 2. Crie um ambiente virtual

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Instale as dependencias

```bash
pip install -r requirements.txt
```

### 4. Configure as variaveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas credenciais:

```env
TOKEN=seu_token_discord_aqui
MONGODB=sua_url_mongodb_aqui
```

### 5. Execute o bot

```bash
python klaus.py
```

---

## ⚙️ Configuracao

### Variaveis de Ambiente

| Variavel | Obrigatorio | Descricao |
|----------|-------------|-----------|
| `TOKEN` | Sim | Token do bot Discord |
| `MONGODB` | Sim | URL de conexao do MongoDB |
| `COMMAND_PREFIX` | Nao | Prefixo do bot (default: `!`) |
| `OWNER_ID` | Nao | ID do dono do bot |

### Criando o Bot no Discord

1. Acesse o [Discord Developer Portal](https://discord.com/developers/applications)
2. Crie uma nova aplicacao
3. Vá em **Bot** e copie o token
4. Habilite **Message Content Intent** e **Server Members Intent**
5. Vá em **OAuth2 > URL Generator**
6. Selecione os scopes: `bot`, `applications.commands`
7. Selecione as permissoes necessarias
8. Use o URL gerado para adicionar o bot ao servidor

### MongoDB

O Klaus Bot usa MongoDB para persistencia de dados. Você pode usar:

- **MongoDB Atlas** (recomendado): [mongodb.com/atlas](https://www.mongodb.com/atlas/database)
- **MongoDB Local**: Para desenvolvimento

---

## 📁 Estrutura do Projeto

```
klaus-bot/
├── klaus.py              # Arquivo principal do bot
├── config.py             # Configuracoes e settings
├── database.py           # Sistema de banco de dados (Motor/MongoDB)
├── embed_builder.py      # Construtor de embeds profissionais
├── helpers.py            # Funcoes utilitarias
├── profile_generator.py  # Gerador de imagens de perfil
├── ship_generator.py     # Gerador de imagens de ship
├── theme_art.py          # Efeitos visuais para perfis
├── logger_config.py      # Configuracao de logging
├── send_commands.py      # Script para enviar comandos
├── requirements.txt      # Dependencias Python
├── pyproject.toml        # Configuracoes do projeto
├── Procfile              # Para deploy em Heroku
├── runtime.txt           # Versao do Python
├── .env.example          # Template de variaveis
├── .gitignore            # Arquivos ignorados pelo git
├── cogs/                 # Modulos de funcionalidades
│   ├── economia.py       # Sistema economico (30+ comandos)
│   ├── diversao.py       # Diversao e minigames (19 comandos)
│   ├── moderacao.py      # Moderacao (14 comandos)
│   ├── utilidades.py     # Utilidades (14 comandos)
│   ├── eventos.py        # Eventos e sistema de XP
│   ├── automod.py        # Auto-moderacao
│   ├── giveaway.py       # Sistema de giveaways
│   ├── social.py         # Recursos sociais
│   ├── tickets.py        # Sistema de tickets
│   ├── reaction_roles.py # Reaction roles
│   ├── utilidades_extra.py  # Utilidades extras
│   ├── diversao_extra.py    # Diversao extra
│   └── __init__.py
└── tests/                # Testes
```

---

## 🌐 Dashboard

O Klaus Bot possui um dashboard web completo para configuracao do bot.

**URL:** [klaus-dashboard-delta.vercel.app](https://klaus-dashboard-delta.vercel.app)

### Funcionalidades do Dashboard
- Login via Discord OAuth2
- Configuracao de boas-vindas e adeus
- Auto-cargo automatico
- Sistema de logs (mensagens, membros, moderacao)
- Configuracao de XP e economia
- Auto-moderacao configuravel
- Perfil do usuario com personalizacao
- Leaderboard publico

---

## 🛠️ Tecnologias

### Bot
- **Python 3.11+** - Linguagem principal
- **discord.py 2.3+** - Biblioteca Discord
- **Motor** - Driver assincrono para MongoDB
- **MongoDB** - Banco de dados NoSQL
- **Pillow** - Geracao de imagens de perfil
- **Pydantic** - Validacao de configuracoes

### Dashboard
- **Flask** - Framework web
- **Jinja2** - Templates HTML
- **MongoDB** - Banco de dados
- **Vercel** - Hospedagem

---

## 🤝 Contribuindo

Contribuicoes sao bem-vindas! Siga estes passos:

1. Fork o repositorio
2. Crie uma branch para sua feature (`git checkout -b feature/nova-feature`)
3. Commit suas mudancas (`git commit -m 'Add nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

---

## 📄 Licenca

Este projeto esta licenciado sob a Licenca MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🙏 Agradecimentos

- [Discord.py](https://discordpy.readthedocs.io/) - Biblioteca para bots Discord
- [MongoDB](https://www.mongodb.com/) - Banco de dados NoSQL
- [Loritta](https://loritta.website/) - Inspiracao para o bot
- [Mudae](https://mudae.net/) - Inspiracao para o sistema de waifus
- Todos os usuarios que usam e apoiam o Klaus Bot

---

<div align="center">

**Feito com 💜 pela equipe Klaus Bot**

[⬆ Voltar ao topo](#-klaus-bot)

</div>

from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, Field


class Settings(BaseSettings):
    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # Discord
    discord_token: str = Field(..., alias="TOKEN")

    # MongoDB
    mongodb_url: str = Field(..., alias="MONGODB")

    # Bot Configuration
    command_prefix: str = "!"
    owner_id: int = 1230185414808047666
    welcome_channel_id: int = 1502466578594271293

    # Economy Settings
    starting_koins: int = 1000
    daily_min: int = 1567
    daily_max: int = 5456
    daily_cooldown_hours: int = 24
    daily_streak_bonus: int = 500
    work_cooldown_hours: int = 1
    rob_cooldown_hours: int = 2

    # Gambling Settings
    jackpot_base_chance: int = 15
    big_bet_threshold: int = 15000
    jackpot_bonus_min: int = 500
    jackpot_bonus_max: int = 2500
    loss_extra_min: int = 300
    loss_extra_max: int = 1700
    rob_success_chance: int = 45
    rob_min_amount: int = 200
    rob_max_amount: int = 2000
    crime_success_chance: int = 40
    crime_min_amount: int = 500
    crime_max_amount: int = 5000
    crime_bail_multiplier: int = 2
    cofre_max: int = 500000
    cofre_interest_rate: float = 0.02
    lottery_ticket_price: int = 500
    lottery_jackpot_base: int = 10000
    pet_hunger_rate: float = 0.1
    heist_min_amount: int = 5000
    heist_max_amount: int = 50000
    heist_success_chance: int = 35
    heist_cooldown: int = 3600
    bounty_min: int = 1000
    bounty_max: int = 100000
    investment_types: dict = {
        "cripto": {"min": 1000, "max_return": 0.3, "risk": 0.4},
        "acoes": {"min": 500, "max_return": 0.15, "risk": 0.25},
        "imoveis": {"min": 10000, "max_return": 0.08, "risk": 0.1},
        "nft": {"min": 2000, "max_return": 0.5, "risk": 0.6},
    }
    daily_challenges: list = [
        {"name": "Apostar 5 vezes", "type": "bet", "target": 5, "reward": 3000},
        {"name": "Ganhe 5000 koins", "type": "earn", "target": 5000, "reward": 2000},
        {"name": "Use 10 comandos", "type": "commands", "target": 10, "reward": 1500},
        {"name": "Minere 3 vezes", "type": "mine", "target": 3, "reward": 2500},
        {"name": "Trabalhe 2 vezes", "type": "work", "target": 2, "reward": 2000},
        {"name": "Cometa 1 crime", "type": "crime", "target": 1, "reward": 1000},
        {"name": "Alimente seu pet", "type": "feed_pet", "target": 1, "reward": 500},
    ]
    lucky_wheel_cooldown: int = 7200
    lucky_wheel_rewards: list = [100, 250, 500, 1000, 2500, 5000, 10000, 25000, 50000, 100000]
    giveaway_duration: int = 3600
    ticket_category: str = "Suporte"
    automod_max_links: int = 3
    automod_max_mentions: int = 5
    automod_bad_words: list = ["palavrao1", "palavrao2"]

    # Social Tracking
    social_actions: list = ["hug", "kiss", "slap", "pat"]

    # Quiz Settings
    quiz_reward: int = 500
    quiz_time_limit: int = 15
    quiz_questions: list = [
        {
            "question": "Qual e o planeta mais proximo do Sol?",
            "options": ["Venus", "Mercurio", "Marte", "Terra"],
            "answer": 1,
        },
        {
            "question": "Quem pintou a Mona Lisa?",
            "options": ["Michelangelo", "Rafael", "Leonardo da Vinci", "Caravaggio"],
            "answer": 2,
        },
        {
            "question": "Qual e o maior oceano do mundo?",
            "options": ["Atlantico", "Indico", "Pacifico", "Artico"],
            "answer": 2,
        },
        {
            "question": "Em que ano o Brasil se tornou independente?",
            "options": ["1808", "1822", "1889", "1500"],
            "answer": 1,
        },
        {
            "question": "Qual e o elemento quimico com simbolo O?",
            "options": ["Ouro", "Oxigenio", "Osmio", "Oganesson"],
            "answer": 1,
        },
        {
            "question": "Quantos continentes existem no mundo?",
            "options": ["5", "6", "7", "8"],
            "answer": 2,
        },
        {
            "question": "Qual e o rio mais longo do mundo?",
            "options": ["Amazonas", "Nilo", "Mississippi", "Yangtze"],
            "answer": 1,
        },
        {
            "question": "Quem escreveu 'Cem Anos de Solidao'?",
            "options": ["Pablo Neruda", "Gabriel Garcia Marquez", "Jorge Luis Borges", "Mario Vargas Llosa"],
            "answer": 1,
        },
        {
            "question": "Qual e a capital da Australia?",
            "options": ["Sydney", "Melbourne", "Canberra", "Brisbane"],
            "answer": 2,
        },
        {
            "question": "Qual e a velocidade da luz em km/s (aproximadamente)?",
            "options": ["150.000", "200.000", "300.000", "400.000"],
            "answer": 2,
        },
        {
            "question": "Em que ano caiu o Muro de Berlim?",
            "options": ["1987", "1989", "1991", "1993"],
            "answer": 1,
        },
        {
            "question": "Qual e o animal terrestre mais rapido do mundo?",
            "options": ["Leao", "Guepardo", "Gazela", "Cavalo"],
            "answer": 1,
        },
        {
            "question": "Quantos ossos tem o corpo humano adulto?",
            "options": ["186", "206", "226", "256"],
            "answer": 1,
        },
        {
            "question": "Qual e o pais com maior populacao do mundo?",
            "options": ["Estados Unidos", "India", "Indonesia", "China"],
            "answer": 1,
        },
        {
            "question": "Quem inventou a lâmpada eletrica?",
            "options": ["Nikola Tesla", "Thomas Edison", "Albert Einstein", "Alexander Bell"],
            "answer": 1,
        },
        {
            "question": "Qual e o gas mais abundante na atmosfera terrestre?",
            "options": ["Oxigenio", "Hidrogenio", "Nitrogenio", "Gas Carbonico"],
            "answer": 2,
        },
        {
            "question": "Em que ano terminou a Segunda Guerra Mundial?",
            "options": ["1943", "1944", "1945", "1946"],
            "answer": 2,
        },
        {
            "question": "Qual e o menor pais do mundo?",
            "options": ["Monaco", "Vaticano", "San Marino", "Liechtenstein"],
            "answer": 1,
        },
        {
            "question": "Qual e o metal liquido a temperatura ambiente?",
            "options": ["Chumbo", "Aluminio", "Mercurio", "Cobre"],
            "answer": 2,
        },
        {
            "question": "Quantos planetas tem no Sistema Solar?",
            "options": ["7", "8", "9", "10"],
            "answer": 1,
        },
    ]

    # Adventure Settings
    adventure_reward_min: int = 100
    adventure_reward_max: int = 5000
    adventure_scenarios: list = [
        {
            "name": "A Floresta Sombria",
            "description": "Voce entra em uma floresta escura e ouve rugidos ao longe.",
            "choices": [
                {"text": "Seguir o caminho principal", "outcome": "win", "reward": 500, "message": "Voce encontra um bau escondido entre as arvores!"},
                {"text": "Ir pelo atalho escuro", "outcome": "lose", "reward": 0, "message": "Voce caiu em uma armadilha e perdeu seus koins!"},
                {"text": "Subir em uma arvore para observar", "outcome": "win", "reward": 300, "message": "Voce avistou um caminho seguro e encontrou moedas no chao!"},
                {"text": "Voltar pelo caminho original", "outcome": "draw", "reward": 100, "message": "Voce voltou sem ganhar nada, mas pelo menos esta seguro!"},
            ],
        },
        {
            "name": "A Caverna Maldita",
            "description": "Uma caverna misteriosa brilha com cristais luminosos.",
            "choices": [
                {"text": "Entrar na caverna", "outcome": "win", "reward": 700, "message": "Voce extraiu cristais valiosos das paredes!"},
                {"text": "Coletar cristais da entrada", "outcome": "win", "reward": 200, "message": "Voce pegou alguns cristais da entrada sem entrar."},
                {"text": "Ignorar e seguir viagem", "outcome": "draw", "reward": 100, "message": "Voce seguiu viagem e encontrou moedas no caminho."},
                {"text": "Jogar uma pedra dentro", "outcome": "lose", "reward": 0, "message": "A caverna desabou e voce perdeu seus itens!"},
            ],
        },
        {
            "name": "O Rio Perigoso",
            "description": "Um rio caudaloso bloqueia seu caminho. Ha um barco velho na margem.",
            "choices": [
                {"text": "Usar o barco para atravessar", "outcome": "win", "reward": 600, "message": "Voce atravessou o rio e encontrou um baú nas margens opostas!"},
                {"text": "Nadar ate a outra margem", "outcome": "lose", "reward": 0, "message": "A corrente era forte demais e voce perdeu koins tentando!"},
                {"text": "Procurar uma ponte mais a frente", "outcome": "win", "reward": 400, "message": "Voce encontrou uma ponte antiga e tesouros no caminho!"},
                {"text": "Acampar na margem e esperar", "outcome": "draw", "reward": 150, "message": "Voce encontrou algumas moedas na areia da margem."},
            ],
        },
        {
            "name": "A Vila Abandonada",
            "description": "Voce encontra uma vila desertada com casas abandonadas.",
            "choices": [
                {"text": "Explorar a casa principal", "outcome": "win", "reward": 800, "message": "Voce encontrou um cofre escondido com ouro!"},
                {"text": "Procurar na igreja", "outcome": "win", "reward": 500, "message": "Havia doacoes esquecidas no altar!"},
                {"text": "Revirar os celeiros", "outcome": "draw", "reward": 200, "message": "Voce encontrou apenas grãos velhos, mas vendeu por koins."},
                {"text": "Dormir na vila e seguir viagem", "outcome": "lose", "reward": 0, "message": "Bandidos roubaram seus koins enquanto voce dormia!"},
            ],
        },
        {
            "name": "O Monte Gélido",
            "description": "Voce escala uma montanha coberta de neve com tempestades se aproximando.",
            "choices": [
                {"text": "Continuar subindo rapido", "outcome": "win", "reward": 900, "message": "No topo voce encontrou um deposito de minerais raros!"},
                {"text": "Procurar um abrigo", "outcome": "win", "reward": 350, "message": "Voce encontrou um abrigo com suprimentos e moedas!"},
                {"text": "Descer e rodear a montanha", "outcome": "draw", "reward": 200, "message": "O caminho era longo mas seguro, com algumas moedas no chao."},
                {"text": "Acampar na neve", "outcome": "lose", "reward": 0, "message": "A hipotermia quase te pegou! Voce perdeu koins com o frio."},
            ],
        },
        {
            "name": "O Portao Antigo",
            "description": "Um enorme portao de pedra com inscricoes antigas bloqueia uma passagem.",
            "choices": [
                {"text": "Decifrar as inscricoes", "outcome": "win", "reward": 1000, "message": "Voce abriu o portao e encontrou uma sala do tesouro!"},
                {"text": "Forcar o portao", "outcome": "lose", "reward": 0, "message": "Armadilhas foram ativadas e voce perdeu seus koins!"},
                {"text": "Procurar uma entrada alternativa", "outcome": "win", "reward": 600, "message": "Voce encontrou um tunel secreto com ouro!"},
                {"text": "Desistir e voltar", "outcome": "draw", "reward": 150, "message": "Voce encontrou moedas no caminho de volta."},
            ],
        },
        {
            "name": "O Mercado Negro",
            "description": "Voce entra em um mercado clandestino cheio de vendedores misteriosos.",
            "choices": [
                {"text": "Comprar um mapa do tesouro", "outcome": "win", "reward": 1200, "message": "O mapa levou voce a um tesouro escondido!"},
                {"text": "Apostar no jogo de dados", "outcome": "lose", "reward": 0, "message": "Voce perdeu todos os koins na aposta!"},
                {"text": "Vender seus itens raros", "outcome": "win", "reward": 700, "message": "Voce fez um otimo negocio e lucrou bastante!"},
                {"text": "Apenas observar e sair", "outcome": "draw", "reward": 250, "message": "Voce encontrou moedas caídas no chao."},
            ],
        },
        {
            "name": "A Torre do Mago",
            "description": "Uma torre alta se ergue com magia brilhando em suas janelas.",
            "choices": [
                {"text": "Subir os degraus magicos", "outcome": "win", "reward": 1500, "message": "O mago recompensou voce por sua coragem!"},
                {"text": "Falar com o mago pela janela", "outcome": "win", "reward": 800, "message": "O mago te deu uma poção de fortuna!"},
                {"text": "Procurar itens na base da torre", "outcome": "draw", "reward": 300, "message": "Voce encontrou alguns componentes magicos valiosos."},
                {"text": "Roubar o jardim do mago", "outcome": "lose", "reward": 0, "message": "O mago te transformou em sapo por um tempo!"},
            ],
        },
        {
            "name": "O Navio Fantasma",
            "description": "Um navio abandonado flutua na neblina com portas rangendo.",
            "choices": [
                {"text": "Entrar na cabine do capitao", "outcome": "win", "reward": 1100, "message": "Voce encontrou o diario do capitao e um bau de ouro!"},
                {"text": "Explorar o porao", "outcome": "win", "reward": 500, "message": "Ha espécies raras no porao que valem fortuna!"},
                {"text": "Procurar no convés", "outcome": "draw", "reward": 200, "message": "Voce encontrou apenas cordas e velas velhas."},
                {"text": "Sair do navio rapidamente", "outcome": "lose", "reward": 0, "message": "O navio afundou e voce perdeu seus koins!"},
            ],
        },
        {
            "name": "A Cidade Perdida",
            "description": "Ruinas de uma cidade antiga se revelam diante de voce.",
            "choices": [
                {"text": "Explorar o templo central", "outcome": "win", "reward": 2000, "message": "Voce encontrou o altar dourado da cidade!"},
                {"text": "Revirar as casas abandonadas", "outcome": "win", "reward": 600, "message": "Cada casa guardava pequenos tesouros esquecidos!"},
                {"text": "Seguir o rio subterraneo", "outcome": "win", "reward": 900, "message": "O rio levou a uma caverna com cristais preciosos!"},
                {"text": "Acampar na entrada da cidade", "outcome": "lose", "reward": 0, "message": "Bandidos atacaram seu acampamento durante a noite!"},
            ],
        },
        {
            "name": "A Fortaleza Inimiga",
            "description": "Uma fortaleza inimiga bloqueia o caminho para o reino.",
            "choices": [
                {"text": "Infiltrar-se pelo esgoto", "outcome": "win", "reward": 1800, "message": "Voce roubou o tesouro da fortaleza sem ser visto!"},
                {"text": "Atacar de frente", "outcome": "lose", "reward": 0, "message": "Voce foi capturado e perdeu todos os seus koins!"},
                {"text": "Subornar os guardas", "outcome": "win", "reward": 1000, "message": "Os guardas te deixaram passar e voce encontrou ouro!"},
                {"text": "Esperar a noite cair", "outcome": "win", "reward": 1500, "message": "Na escuridao, voce pilhou a fortaleza com sucesso!"},
            ],
        },
        {
            "name": "O Oceano Profundo",
            "description": "Voce mergulha em águas profundas em busca de tesouros submarinos.",
            "choices": [
                {"text": "Explorar o naufragio", "outcome": "win", "reward": 1400, "message": "Voce encontrou lingotes de ouro no navio afundado!"},
                {"text": "Coletar coral raro", "outcome": "win", "reward": 600, "message": "O coral raro vale uma fortuna nos mercados!"},
                {"text": "Mergulhar na caverna subaquatica", "outcome": "lose", "reward": 0, "message": "Uma corrente te arrastou e voce perdeu seus equipamentos!"},
                {"text": "Pescar na superficie", "outcome": "draw", "reward": 250, "message": "Voce pescou alguns peixes que vendeu por koins."},
            ],
        },
    ]

    # Poll Settings
    poll_default_duration: int = 3600
    poll_max_options: int = 4

    # Battle Settings
    battle_tax: float = 0.05
    battle_min_bet: int = 500
    battle_max_bet: int = 50000

    # Profile Shop - Backgrounds
    profile_backgrounds: dict = {
        "padrao": {"name": "Padrao", "emoji": "⬜", "price": 0, "colors": {"bg": "#0a0a0a", "accent": "#3a3a3a", "border": "#8a8a8a"}, "effects": {"particles": 20, "sparkles": 0, "stripes": False, "grid": False, "glow": 0}},
        "madeira": {"name": "Madeira", "emoji": "🪵", "price": 500, "colors": {"bg": "#0d0805", "accent": "#6b4423", "border": "#b87333"}, "effects": {"particles": 30, "sparkles": 5, "stripes": False, "grid": False, "glow": 1}},
        "argila": {"name": "Argila", "emoji": "🏺", "price": 500, "colors": {"bg": "#0d0a08", "accent": "#8b5a2b", "border": "#cd853f"}, "effects": {"particles": 30, "sparkles": 5, "stripes": False, "grid": False, "glow": 1}},
        "musgo": {"name": "Musgo", "emoji": "🌿", "price": 500, "colors": {"bg": "#050a05", "accent": "#2d5a27", "border": "#4caf50"}, "effects": {"particles": 30, "sparkles": 5, "stripes": False, "grid": False, "glow": 1}},
        "pedra": {"name": "Pedra", "emoji": "🪨", "price": 750, "colors": {"bg": "#0a0a08", "accent": "#5a5a55", "border": "#8b8b80"}, "effects": {"particles": 15, "sparkles": 0, "stripes": False, "grid": False, "glow": 0}},
        "areia": {"name": "Areia", "emoji": "🏖️", "price": 750, "colors": {"bg": "#0d0c08", "accent": "#8b7355", "border": "#daa520"}, "effects": {"particles": 30, "sparkles": 5, "stripes": False, "grid": False, "glow": 1}},
        "cinza_prata": {"name": "Cinza Prata", "emoji": "🔘", "price": 800, "colors": {"bg": "#0a0a0a", "accent": "#4a4a4a", "border": "#b0b0b0"}, "effects": {"particles": 20, "sparkles": 3, "stripes": False, "grid": False, "glow": 1}},
        "tartaruga": {"name": "Tartaruga", "emoji": "🐢", "price": 800, "colors": {"bg": "#050a05", "accent": "#2a5a2a", "border": "#3cb371"}, "effects": {"particles": 20, "sparkles": 3, "stripes": False, "grid": False, "glow": 1}},
        "ferro": {"name": "Ferro", "emoji": "⚙️", "price": 1000, "colors": {"bg": "#080808", "accent": "#5a5a5a", "border": "#a0a0a0"}, "effects": {"particles": 25, "sparkles": 8, "stripes": True, "grid": False, "glow": 1}},
        "carvao": {"name": "Carvao", "emoji": "⬛", "price": 1000, "colors": {"bg": "#050505", "accent": "#3a3a3a", "border": "#5a5a5a"}, "effects": {"particles": 15, "sparkles": 0, "stripes": False, "grid": False, "glow": 0}},
        "turfa": {"name": "Turfa", "emoji": "🟤", "price": 1000, "colors": {"bg": "#0a0805", "accent": "#6b4423", "border": "#8b6914"}, "effects": {"particles": 15, "sparkles": 0, "stripes": False, "grid": False, "glow": 0}},
        "bambu": {"name": "Bambu", "emoji": "🎋", "price": 1500, "colors": {"bg": "#050a05", "accent": "#3a6b27", "border": "#7cfc00"}, "effects": {"particles": 30, "sparkles": 8, "stripes": False, "grid": False, "glow": 1}},
        "cacto": {"name": "Cacto", "emoji": "🌵", "price": 1500, "colors": {"bg": "#050a08", "accent": "#1a7b3a", "border": "#32cd32"}, "effects": {"particles": 30, "sparkles": 8, "stripes": False, "grid": False, "glow": 1}},
        "aloe": {"name": "Aloe", "emoji": "🌱", "price": 1500, "colors": {"bg": "#050a05", "accent": "#2e8b22", "border": "#90ee90"}, "effects": {"particles": 30, "sparkles": 8, "stripes": False, "grid": False, "glow": 1}},
        "chimarra": {"name": "Chimarra", "emoji": "🧉", "price": 2000, "colors": {"bg": "#0d0a05", "accent": "#5a4a1a", "border": "#8b7355"}, "effects": {"particles": 25, "sparkles": 5, "stripes": False, "grid": False, "glow": 1}},
        "melancia": {"name": "Melancia", "emoji": "🍉", "price": 3000, "colors": {"bg": "#0d0505", "accent": "#4a2a1a", "border": "#ff6b6b"}, "effects": {"particles": 40, "sparkles": 10, "stripes": False, "grid": False, "glow": 1}},
        "cerveja": {"name": "Cerveja", "emoji": "🍺", "price": 5000, "colors": {"bg": "#0d0a05", "accent": "#6a5a1a", "border": "#daa520"}, "effects": {"particles": 40, "sparkles": 10, "stripes": False, "grid": False, "glow": 1}},
        "cafe": {"name": "Cafe", "emoji": "☕", "price": 6000, "colors": {"bg": "#0d0805", "accent": "#6b3317", "border": "#d2691e"}, "effects": {"particles": 50, "sparkles": 12, "stripes": False, "grid": False, "glow": 1}},
        "cha": {"name": "Cha", "emoji": "🍵", "price": 6000, "colors": {"bg": "#080a05", "accent": "#5a7b2a", "border": "#9acd32"}, "effects": {"particles": 50, "sparkles": 12, "stripes": False, "grid": False, "glow": 1}},
        "frutas_tropicais": {"name": "Frutas Tropicais", "emoji": "🍊", "price": 8000, "colors": {"bg": "#0d0a05", "accent": "#5a4a1a", "border": "#ff8c00"}, "effects": {"particles": 60, "sparkles": 15, "stripes": True, "grid": False, "glow": 1}},
        "mandacaru": {"name": "Mandacaru", "emoji": "🌵", "price": 10000, "colors": {"bg": "#050a05", "accent": "#1a4a1a", "border": "#32cd32"}, "effects": {"particles": 40, "sparkles": 10, "stripes": False, "grid": False, "glow": 1}},
        "amarelo_solar": {"name": "Amarelo Solar", "emoji": "☀️", "price": 10000, "colors": {"bg": "#0d0d05", "accent": "#5a5a1a", "border": "#ffd700"}, "effects": {"particles": 60, "sparkles": 15, "stripes": True, "grid": False, "glow": 2}},
        "tucano": {"name": "Tucano", "emoji": "🦜", "price": 12000, "colors": {"bg": "#050d05", "accent": "#1a5a1a", "border": "#ff8c00"}, "effects": {"particles": 60, "sparkles": 15, "stripes": False, "grid": False, "glow": 1}},
        "planicie": {"name": "Planicie", "emoji": "🌾", "price": 12000, "colors": {"bg": "#0a0d05", "accent": "#4a6a2a", "border": "#9acd32"}, "effects": {"particles": 50, "sparkles": 12, "stripes": False, "grid": False, "glow": 1}},
        "chocolate": {"name": "Chocolate", "emoji": "🍫", "price": 12000, "colors": {"bg": "#0d0805", "accent": "#6b3317", "border": "#8b4513"}, "effects": {"particles": 40, "sparkles": 8, "stripes": False, "grid": False, "glow": 1}},
        "caramelo": {"name": "Caramelo", "emoji": "🍮", "price": 12000, "colors": {"bg": "#0d0a05", "accent": "#7b5423", "border": "#daa520"}, "effects": {"particles": 40, "sparkles": 8, "stripes": False, "grid": False, "glow": 1}},
        "sake": {"name": "Sake", "emoji": "🍶", "price": 12000, "colors": {"bg": "#0d0d0d", "accent": "#4a4a4a", "border": "#f5f5f5"}, "effects": {"particles": 40, "sparkles": 10, "stripes": False, "grid": False, "glow": 1}},
        "neblina": {"name": "Neblina", "emoji": "🌫️", "price": 15000, "colors": {"bg": "#0a0a0a", "accent": "#3a3a3a", "border": "#c0c0c0"}, "effects": {"particles": 40, "sparkles": 10, "stripes": False, "grid": False, "glow": 2, "type": "shadow_waves", "intensity": 1}},
        "vinho_tinto": {"name": "Vinho Tinto", "emoji": "🍷", "price": 15000, "colors": {"bg": "#100508", "accent": "#4a1a2a", "border": "#800020"}, "effects": {"particles": 50, "sparkles": 10, "stripes": False, "grid": False, "glow": 1}},
        "bronze": {"name": "Bronze", "emoji": "🟠", "price": 15000, "colors": {"bg": "#0d0a05", "accent": "#8b6a2a", "border": "#cd9b1d"}, "effects": {"particles": 60, "sparkles": 15, "stripes": True, "grid": False, "glow": 1}},
        "latao": {"name": "Latao", "emoji": "🟡", "price": 15000, "colors": {"bg": "#0d0c05", "accent": "#8b7a2a", "border": "#daa520"}, "effects": {"particles": 60, "sparkles": 15, "stripes": True, "grid": False, "glow": 1}},
        "royal": {"name": "Royal", "emoji": "👑", "price": 15000, "colors": {"bg": "#0a050d", "accent": "#3a1a5a", "border": "#9400d3"}, "effects": {"particles": 80, "sparkles": 25, "stripes": True, "grid": False, "glow": 2}},
        "imperial": {"name": "Imperial", "emoji": "🥇", "price": 15000, "colors": {"bg": "#0d0a05", "accent": "#6a5a1a", "border": "#ffd700"}, "effects": {"particles": 80, "sparkles": 25, "stripes": True, "grid": False, "glow": 2, "type": "nebula", "intensity": 1}},
        "coral_vibrante": {"name": "Coral Vibrante", "emoji": "🪸", "price": 15000, "colors": {"bg": "#0d0808", "accent": "#5a3a3a", "border": "#ff7f50"}, "effects": {"particles": 70, "sparkles": 20, "stripes": True, "grid": False, "glow": 2}},
        "samurai": {"name": "Samurai", "emoji": "⚔️", "price": 15000, "colors": {"bg": "#0d0505", "accent": "#5a1a1a", "border": "#b22222"}, "effects": {"particles": 90, "sparkles": 30, "stripes": True, "grid": False, "glow": 2}},
        "vinho": {"name": "Vinho", "emoji": "🍷", "price": 18000, "colors": {"bg": "#100508", "accent": "#5a1a2a", "border": "#722f37"}, "effects": {"particles": 50, "sparkles": 10, "stripes": False, "grid": False, "glow": 1}},
        "oasis": {"name": "Oasis", "emoji": "🏝️", "price": 18000, "colors": {"bg": "#0d0c08", "accent": "#4a6a2a", "border": "#40e0d0"}, "effects": {"particles": 50, "sparkles": 12, "stripes": False, "grid": False, "glow": 1}},
        "geada": {"name": "Geada", "emoji": "🥶", "price": 20000, "colors": {"bg": "#050a0d", "accent": "#1a4a5a", "border": "#87ceeb"}, "effects": {"particles": 80, "sparkles": 30, "stripes": False, "grid": True, "glow": 2, "type": "crystal", "intensity": 1}},
        "lobo_guara": {"name": "Lobo Guara", "emoji": "🐺", "price": 20000, "colors": {"bg": "#0a0a08", "accent": "#4a3a2a", "border": "#b87333"}, "effects": {"particles": 60, "sparkles": 15, "stripes": False, "grid": False, "glow": 1}},
        "retro": {"name": "Retro", "emoji": "📺", "price": 20000, "colors": {"bg": "#0d0a08", "accent": "#5a4a2a", "border": "#daa520"}, "effects": {"particles": 70, "sparkles": 18, "stripes": True, "grid": False, "glow": 2}},
        "neon": {"name": "Neon", "emoji": "💡", "price": 20000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#00ff00"}, "effects": {"particles": 100, "sparkles": 40, "stripes": True, "grid": True, "glow": 3, "type": "neon_pulse", "intensity": 2}},
        "ninja": {"name": "Ninja", "emoji": "🥷", "price": 20000, "colors": {"bg": "#050505", "accent": "#2a2a2a", "border": "#ff4444"}, "effects": {"particles": 90, "sparkles": 30, "stripes": True, "grid": False, "glow": 2, "type": "shadow_waves", "intensity": 2}},
        "viking": {"name": "Viking", "emoji": "🪓", "price": 20000, "colors": {"bg": "#0a0a0d", "accent": "#2a2a4a", "border": "#c0c0c0"}, "effects": {"particles": 90, "sparkles": 30, "stripes": True, "grid": False, "glow": 2}},
        "azul_profundo": {"name": "Azul Profundo", "emoji": "💙", "price": 20000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#00008b"}, "effects": {"particles": 80, "sparkles": 25, "stripes": True, "grid": False, "glow": 2}},
        "sol_nascente": {"name": "Sol Nascente", "emoji": "🌅", "price": 22000, "colors": {"bg": "#100805", "accent": "#6a4a1a", "border": "#ff8c00"}, "effects": {"particles": 70, "sparkles": 20, "stripes": False, "grid": False, "glow": 2}},
        "arara": {"name": "Arara", "emoji": "🦜", "price": 22000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#4169e1"}, "effects": {"particles": 70, "sparkles": 20, "stripes": False, "grid": False, "glow": 2}},
        "canela_dourada": {"name": "Canela Dourada", "emoji": "✨", "price": 22000, "colors": {"bg": "#0d0a05", "accent": "#6a4a1a", "border": "#daa520"}, "effects": {"particles": 80, "sparkles": 25, "stripes": True, "grid": False, "glow": 2}},
        "polaridade": {"name": "Polaridade", "emoji": "🧲", "price": 25000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#e0e0e0"}, "effects": {"particles": 80, "sparkles": 25, "stripes": True, "grid": True, "glow": 2}},
        "agate": {"name": "Agata", "emoji": "🟤", "price": 25000, "colors": {"bg": "#0d0a08", "accent": "#5a4a2a", "border": "#cd853f"}, "effects": {"particles": 50, "sparkles": 12, "stripes": False, "grid": False, "glow": 1}},
        "verde_esmeralda": {"name": "Verde Esmeralda", "emoji": "💚", "price": 25000, "colors": {"bg": "#050d05", "accent": "#1a5a2a", "border": "#2e8b57"}, "effects": {"particles": 80, "sparkles": 25, "stripes": True, "grid": False, "glow": 2}},
        "tufao": {"name": "Tufao", "emoji": "🌪️", "price": 25000, "colors": {"bg": "#0a0a0d", "accent": "#2a2a4a", "border": "#708090"}, "effects": {"particles": 80, "sparkles": 20, "stripes": False, "grid": False, "glow": 2, "type": "shadow_waves", "intensity": 2}},
        "cafe_eterno": {"name": "Cafe Eterno", "emoji": "☕", "price": 25000, "colors": {"bg": "#0d0805", "accent": "#5a3317", "border": "#a0522d"}, "effects": {"particles": 40, "sparkles": 8, "stripes": False, "grid": False, "glow": 1}},
        "zirconio": {"name": "Zirconio", "emoji": "💙", "price": 25000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#4169e1"}, "effects": {"particles": 60, "sparkles": 18, "stripes": False, "grid": False, "glow": 2}},
        "prata": {"name": "Prata", "emoji": "🔘", "price": 30000, "colors": {"bg": "#0a0a0d", "accent": "#7a7a8a", "border": "#c0c0c0"}, "effects": {"particles": 40, "sparkles": 15, "stripes": True, "grid": False, "glow": 1}},
        "platina": {"name": "Platina", "emoji": "⚪", "price": 30000, "colors": {"bg": "#0a0a0a", "accent": "#8a8a8a", "border": "#e5e5e5"}, "effects": {"particles": 40, "sparkles": 15, "stripes": True, "grid": False, "glow": 1}},
        "niquel": {"name": "Niquel", "emoji": "⚙️", "price": 30000, "colors": {"bg": "#0a0a0a", "accent": "#6a6a7a", "border": "#a8a8a8"}, "effects": {"particles": 40, "sparkles": 15, "stripes": True, "grid": False, "glow": 1}},
        "lofi": {"name": "Lo-Fi", "emoji": "🎧", "price": 30000, "colors": {"bg": "#0d0a08", "accent": "#5a4a2a", "border": "#cd853f"}, "effects": {"particles": 70, "sparkles": 18, "stripes": True, "grid": False, "glow": 2, "type": "shadow_waves", "intensity": 1}},
        "sakura": {"name": "Sakura", "emoji": "🌸", "price": 30000, "colors": {"bg": "#0d0508", "accent": "#5a1a2a", "border": "#ffb7c5"}, "effects": {"particles": 70, "sparkles": 20, "stripes": True, "grid": False, "glow": 2, "type": "petals", "intensity": 2}},
        "esmeralda": {"name": "Esmeralda", "emoji": "💎", "price": 30000, "colors": {"bg": "#050d08", "accent": "#1a5a2a", "border": "#50c878"}, "effects": {"particles": 80, "sparkles": 25, "stripes": True, "grid": False, "glow": 2}},
        "tropical": {"name": "Tropical", "emoji": "🌴", "price": 30000, "colors": {"bg": "#050d05", "accent": "#1a5a1a", "border": "#00fa9a"}, "effects": {"particles": 60, "sparkles": 15, "stripes": False, "grid": False, "glow": 1, "type": "petals", "intensity": 2}},
        "primavera": {"name": "Primavera", "emoji": "🌷", "price": 30000, "colors": {"bg": "#0d0508", "accent": "#5a1a3a", "border": "#ff69b4"}, "effects": {"particles": 60, "sparkles": 18, "stripes": False, "grid": False, "glow": 2, "type": "petals", "intensity": 3}},
        "rosa_champagne": {"name": "Rosa Champagne", "emoji": "🥂", "price": 30000, "colors": {"bg": "#0d0508", "accent": "#4a2a3a", "border": "#f7cac9"}, "effects": {"particles": 70, "sparkles": 22, "stripes": True, "grid": False, "glow": 2}},
        "prisma": {"name": "Prisma", "emoji": "🔺", "price": 30000, "colors": {"bg": "#0a0a0d", "accent": "#3a3a4a", "border": "#ff69b4"}, "effects": {"particles": 90, "sparkles": 30, "stripes": True, "grid": True, "glow": 2, "type": "sacred_geometry", "intensity": 1}},
        "mercurio": {"name": "Mercurio", "emoji": "☿️", "price": 30000, "colors": {"bg": "#0a0a0a", "accent": "#6a6a6a", "border": "#c0c0c0"}, "effects": {"particles": 40, "sparkles": 15, "stripes": True, "grid": False, "glow": 1}},
        "geleira": {"name": "Geleira", "emoji": "🧊", "price": 35000, "colors": {"bg": "#050510", "accent": "#1a3a5a", "border": "#00bfff"}, "effects": {"particles": 100, "sparkles": 40, "stripes": False, "grid": True, "glow": 2, "type": "crystal", "intensity": 2}},
        "cristal": {"name": "Cristal", "emoji": "💎", "price": 35000, "colors": {"bg": "#0a0a0d", "accent": "#5a5a7a", "border": "#e0e0ff"}, "effects": {"particles": 100, "sparkles": 35, "stripes": False, "grid": True, "glow": 2, "type": "crystal", "intensity": 2}},
        "quartzo": {"name": "Quartzo", "emoji": "🔮", "price": 35000, "colors": {"bg": "#0d0a0d", "accent": "#7a5a7a", "border": "#dda0dd"}, "effects": {"particles": 100, "sparkles": 35, "stripes": False, "grid": True, "glow": 2, "type": "crystal", "intensity": 2}},
        "vanadio": {"name": "Vanadio", "emoji": "🟣", "price": 35000, "colors": {"bg": "#0d050d", "accent": "#4a1a4a", "border": "#9932cc"}, "effects": {"particles": 80, "sparkles": 22, "stripes": True, "grid": False, "glow": 2}},
        "fantasma": {"name": "Fantasma", "emoji": "👻", "price": 35000, "colors": {"bg": "#0a0a0d", "accent": "#3a3a4a", "border": "#e0e0ff"}, "effects": {"particles": 80, "sparkles": 20, "stripes": True, "grid": False, "glow": 2, "type": "shadow_waves", "intensity": 2}},
        "neve_sakura": {"name": "Neve Sakura", "emoji": "🌺", "price": 35000, "colors": {"bg": "#0d080a", "accent": "#5a2a3a", "border": "#ffc0cb"}, "effects": {"particles": 90, "sparkles": 35, "stripes": False, "grid": True, "glow": 2, "type": "petals", "intensity": 2}},
        "outono": {"name": "Outono", "emoji": "🍂", "price": 35000, "colors": {"bg": "#0d0a05", "accent": "#6a4a1a", "border": "#ff8c00"}, "effects": {"particles": 60, "sparkles": 15, "stripes": False, "grid": False, "glow": 1, "type": "petals", "intensity": 2}},
        "cripta": {"name": "Cripta", "emoji": "⚰️", "price": 35000, "colors": {"bg": "#0a0a0a", "accent": "#3a3a3a", "border": "#696969"}, "effects": {"particles": 60, "sparkles": 10, "stripes": False, "grid": False, "glow": 1, "type": "shadow_waves", "intensity": 1}},
        "obsidiana": {"name": "Obsidiana", "emoji": "🖤", "price": 35000, "colors": {"bg": "#050505", "accent": "#2a2a2a", "border": "#5a5a5a"}, "effects": {"particles": 50, "sparkles": 10, "stripes": False, "grid": False, "glow": 1, "type": "shadow_waves", "intensity": 1}},
        "lila_mistico": {"name": "Lila Mistico", "emoji": "🔮", "price": 35000, "colors": {"bg": "#0d050d", "accent": "#4a1a4a", "border": "#c8a2c8"}, "effects": {"particles": 80, "sparkles": 25, "stripes": True, "grid": False, "glow": 2}},
        "obsidiana_v2": {"name": "Obsidiana II", "emoji": "🖤", "price": 35000, "colors": {"bg": "#050505", "accent": "#1a1a1a", "border": "#3a3a3a"}, "effects": {"particles": 40, "sparkles": 8, "stripes": False, "grid": False, "glow": 1, "type": "shadow_waves", "intensity": 1}},
        "safira_bg": {"name": "Safira", "emoji": "🔵", "price": 40000, "colors": {"bg": "#05050d", "accent": "#1a1a8b", "border": "#4169e1"}, "effects": {"particles": 80, "sparkles": 25, "stripes": False, "grid": False, "glow": 2}},
        "aquamarina": {"name": "Aquamarina", "emoji": "🩵", "price": 40000, "colors": {"bg": "#050d0d", "accent": "#1a7a8b", "border": "#7fffd4"}, "effects": {"particles": 90, "sparkles": 30, "stripes": False, "grid": False, "glow": 2, "type": "aurora", "intensity": 1}},
        "turquesa": {"name": "Turquesa", "emoji": "🩵", "price": 40000, "colors": {"bg": "#050d0d", "accent": "#1a8b8b", "border": "#40e0d0"}, "effects": {"particles": 90, "sparkles": 30, "stripes": False, "grid": False, "glow": 2, "type": "aurora", "intensity": 1}},
        "opala": {"name": "Opala", "emoji": "🤍", "price": 40000, "colors": {"bg": "#0d0a0d", "accent": "#7a7a8a", "border": "#f0f8ff"}, "effects": {"particles": 100, "sparkles": 40, "stripes": False, "grid": True, "glow": 2, "type": "crystal", "intensity": 2}},
        "jade": {"name": "Jade", "emoji": "🟢", "price": 40000, "colors": {"bg": "#050d08", "accent": "#1a8b5a", "border": "#00fa9a"}, "effects": {"particles": 80, "sparkles": 22, "stripes": False, "grid": False, "glow": 2}},
        "peridot": {"name": "Peridote", "emoji": "🟩", "price": 40000, "colors": {"bg": "#080d05", "accent": "#4a8b2a", "border": "#7fff00"}, "effects": {"particles": 80, "sparkles": 22, "stripes": False, "grid": False, "glow": 2}},
        "aventurina": {"name": "Aventurina", "emoji": "💚", "price": 40000, "colors": {"bg": "#050d08", "accent": "#2a7a3a", "border": "#3cb371"}, "effects": {"particles": 80, "sparkles": 22, "stripes": False, "grid": False, "glow": 2}},
        "topazio": {"name": "Topazio", "emoji": "🟡", "price": 40000, "colors": {"bg": "#0d0c05", "accent": "#8b7a14", "border": "#ffd700"}, "effects": {"particles": 80, "sparkles": 22, "stripes": False, "grid": False, "glow": 2}},
        "citrino": {"name": "Citrino", "emoji": "🟨", "price": 40000, "colors": {"bg": "#0d0c05", "accent": "#8b6a14", "border": "#ffb347"}, "effects": {"particles": 80, "sparkles": 22, "stripes": False, "grid": False, "glow": 2}},
        "ambra": {"name": "Ambra", "emoji": "🟠", "price": 40000, "colors": {"bg": "#0d0a05", "accent": "#8b5a14", "border": "#ff8c00"}, "effects": {"particles": 80, "sparkles": 22, "stripes": False, "grid": False, "glow": 2}},
        "rubi_bg": {"name": "Rubi", "emoji": "🔴", "price": 40000, "colors": {"bg": "#0d0505", "accent": "#8b1a1a", "border": "#dc143c"}, "effects": {"particles": 80, "sparkles": 22, "stripes": False, "grid": False, "glow": 2}},
        "granada": {"name": "Granada", "emoji": "🟥", "price": 40000, "colors": {"bg": "#0d0505", "accent": "#7a1a1a", "border": "#b22222"}, "effects": {"particles": 80, "sparkles": 22, "stripes": False, "grid": False, "glow": 2}},
        "coral": {"name": "Coral", "emoji": "🪸", "price": 40000, "colors": {"bg": "#0d0808", "accent": "#8b4a4a", "border": "#ff7f50"}, "effects": {"particles": 80, "sparkles": 22, "stripes": False, "grid": False, "glow": 2}},
        "inverno": {"name": "Inverno", "emoji": "☃️", "price": 40000, "colors": {"bg": "#050a0d", "accent": "#1a3a4a", "border": "#add8e6"}, "effects": {"particles": 80, "sparkles": 25, "stripes": True, "grid": False, "glow": 2, "type": "rain", "intensity": 1}},
        "verao": {"name": "Verao", "emoji": "☀️", "price": 40000, "colors": {"bg": "#0d0d05", "accent": "#5a5a1a", "border": "#ffd700"}, "effects": {"particles": 80, "sparkles": 25, "stripes": True, "grid": False, "glow": 2}},
        "luz_estrelas": {"name": "Luz das Estrelas", "emoji": "✨", "price": 40000, "colors": {"bg": "#0a050d", "accent": "#3a1a4a", "border": "#e6e6fa"}, "effects": {"particles": 130, "sparkles": 50, "stripes": True, "grid": True, "glow": 3}},
        "neon_rosa": {"name": "Neon Rosa", "emoji": "💗", "price": 40000, "colors": {"bg": "#0d050a", "accent": "#4a1a2a", "border": "#ff1493"}, "effects": {"particles": 110, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "neon_pulse", "intensity": 2}},
        "cromo": {"name": "Cromo", "emoji": "🪞", "price": 40000, "colors": {"bg": "#0a0a0a", "accent": "#4a4a4a", "border": "#d4d4d4"}, "effects": {"particles": 40, "sparkles": 15, "stripes": True, "grid": False, "glow": 1}},
        "berilo": {"name": "Berilo", "emoji": "💎", "price": 40000, "colors": {"bg": "#050d0d", "accent": "#1a5a5a", "border": "#7fffd4"}, "effects": {"particles": 90, "sparkles": 30, "stripes": False, "grid": True, "glow": 2}},
        "fractal": {"name": "Fractal", "emoji": "🔮", "price": 40000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#7b68ee"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": True, "glow": 2, "type": "sacred_geometry", "intensity": 2}},
        "vermelho_sangue": {"name": "Vermelho Sangue", "emoji": "🩸", "price": 40000, "colors": {"bg": "#100505", "accent": "#5a1a1a", "border": "#8b0000"}, "effects": {"particles": 80, "sparkles": 20, "stripes": True, "grid": False, "glow": 2}},
        "lapis_lazuli": {"name": "Lapis Lazuli", "emoji": "🔵", "price": 42000, "colors": {"bg": "#050510", "accent": "#1a1a5a", "border": "#1f3fb5"}, "effects": {"particles": 90, "sparkles": 30, "stripes": False, "grid": True, "glow": 2}},
        "difracao": {"name": "Difracao", "emoji": "🌈", "price": 42000, "colors": {"bg": "#0a0a0d", "accent": "#3a3a5a", "border": "#ff69b4"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": True, "glow": 2}},
        "aurora": {"name": "Aurora", "emoji": "🌈", "price": 45000, "colors": {"bg": "#050a0d", "accent": "#1a4a4a", "border": "#00ffff"}, "effects": {"particles": 140, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "aurora", "intensity": 3}},
        "borboleta": {"name": "Borboleta", "emoji": "🦋", "price": 45000, "colors": {"bg": "#0d050a", "accent": "#4a1a3a", "border": "#da70d6"}, "effects": {"particles": 80, "sparkles": 22, "stripes": True, "grid": False, "glow": 2, "type": "petals", "intensity": 2}},
        "gravitacional": {"name": "Gravitacional", "emoji": "🌀", "price": 45000, "colors": {"bg": "#050510", "accent": "#1a1a5a", "border": "#4169e1"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": False, "glow": 2, "type": "vortex", "intensity": 2}},
        "relampago": {"name": "Relampago", "emoji": "⚡", "price": 45000, "colors": {"bg": "#0d0d05", "accent": "#5a5a1a", "border": "#ffff00"}, "effects": {"particles": 100, "sparkles": 30, "stripes": False, "grid": False, "glow": 3, "type": "neon_pulse", "intensity": 3}},
        "niobio": {"name": "Niobio", "emoji": "⚡", "price": 45000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#4682b4"}, "effects": {"particles": 80, "sparkles": 22, "stripes": True, "grid": False, "glow": 2, "type": "neon_pulse", "intensity": 1}},
        "resonancia": {"name": "Resonancia", "emoji": "🔊", "price": 45000, "colors": {"bg": "#0a0510", "accent": "#3a1a4a", "border": "#ff1493"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": True, "glow": 2}},
        "aurora_boreal": {"name": "Aurora Boreal", "emoji": "🌌", "price": 45000, "colors": {"bg": "#050510", "accent": "#0a3a4a", "border": "#00ff88"}, "effects": {"particles": 140, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "aurora", "intensity": 3}},
        "branco_perola": {"name": "Branco Perola", "emoji": "🤍", "price": 50000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#fdeef4"}, "effects": {"particles": 80, "sparkles": 25, "stripes": True, "grid": False, "glow": 2}},
        "meia_noite": {"name": "Meia-Noite", "emoji": "🌙", "price": 50000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#6a5acd"}, "effects": {"particles": 80, "sparkles": 22, "stripes": False, "grid": False, "glow": 2, "type": "aurora", "intensity": 1}},
        "perola": {"name": "Perola", "emoji": "🤍", "price": 50000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#fdeef4"}, "effects": {"particles": 80, "sparkles": 28, "stripes": False, "grid": False, "glow": 2}},
        "crimson": {"name": "Crimson", "emoji": "🩸", "price": 50000, "colors": {"bg": "#100505", "accent": "#4a1a1a", "border": "#ff4444"}, "effects": {"particles": 70, "sparkles": 18, "stripes": False, "grid": False, "glow": 2, "type": "embers", "intensity": 1}},
        "floresta": {"name": "Floresta", "emoji": "🌲", "price": 50000, "colors": {"bg": "#050a05", "accent": "#1a4a1a", "border": "#228b22"}, "effects": {"particles": 60, "sparkles": 15, "stripes": False, "grid": False, "glow": 1, "type": "petals", "intensity": 1}},
        "floresta_sombria": {"name": "Floresta Sombria", "emoji": "🌑", "price": 50000, "colors": {"bg": "#050a05", "accent": "#1a3a1a", "border": "#006400"}, "effects": {"particles": 60, "sparkles": 12, "stripes": False, "grid": False, "glow": 1, "type": "shadow_waves", "intensity": 2}},
        "dourado": {"name": "Dourado", "emoji": "🏆", "price": 50000, "colors": {"bg": "#0d0a05", "accent": "#6a5a1a", "border": "#ffd700"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": False, "glow": 2, "type": "nebula", "intensity": 1}},
        "fenix": {"name": "Fenix", "emoji": "🔥", "price": 50000, "colors": {"bg": "#100505", "accent": "#5a1a1a", "border": "#ff4500"}, "effects": {"particles": 120, "sparkles": 35, "stripes": True, "grid": False, "glow": 3, "type": "embers", "intensity": 2}},
        "trovao": {"name": "Trovao", "emoji": "🌩️", "price": 50000, "colors": {"bg": "#0a0a0d", "accent": "#2a2a5a", "border": "#9370db"}, "effects": {"particles": 100, "sparkles": 25, "stripes": False, "grid": False, "glow": 2, "type": "neon_pulse", "intensity": 2}},
        "glitch": {"name": "Glitch", "emoji": "📟", "price": 50000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#00ff00"}, "effects": {"particles": 120, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "neon_pulse", "intensity": 3}},
        "cobre": {"name": "Cobre", "emoji": "🔶", "price": 55000, "colors": {"bg": "#0d0805", "accent": "#8b4513", "border": "#cd7f32"}, "effects": {"particles": 60, "sparkles": 18, "stripes": True, "grid": False, "glow": 1}},
        "turmalina": {"name": "Turmalina", "emoji": "🩷", "price": 55000, "colors": {"bg": "#0d050a", "accent": "#4a1a3a", "border": "#ff69b4"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": True, "glow": 2}},
        "vulcanico": {"name": "Vulcanico", "emoji": "🌋", "price": 55000, "colors": {"bg": "#100505", "accent": "#5a1a1a", "border": "#ff6600"}, "effects": {"particles": 120, "sparkles": 35, "stripes": True, "grid": False, "glow": 3, "type": "embers", "intensity": 3}},
        "roxo_real": {"name": "Roxo Real", "emoji": "🟣", "price": 55000, "colors": {"bg": "#0a050d", "accent": "#3a1a5a", "border": "#8a2be2"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": True, "glow": 2}},
        "terremoto": {"name": "Terremoto", "emoji": "🏚️", "price": 55000, "colors": {"bg": "#0d0a08", "accent": "#5a4a2a", "border": "#a0522d"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": True, "glow": 2, "type": "shadow_waves", "intensity": 3}},
        "monsoon": {"name": "Monsoon", "emoji": "🌧️", "price": 55000, "colors": {"bg": "#050510", "accent": "#1a2a4a", "border": "#4682b4"}, "effects": {"particles": 80, "sparkles": 20, "stripes": False, "grid": False, "glow": 2, "type": "rain", "intensity": 2}},
        "sakura_noite": {"name": "Sakura Noite", "emoji": "🌸", "price": 55000, "colors": {"bg": "#0d050a", "accent": "#5a2a3a", "border": "#ff69b4"}, "effects": {"particles": 120, "sparkles": 40, "stripes": True, "grid": True, "glow": 3, "type": "petals", "intensity": 3}},
        "onda_sonora": {"name": "Onda Sonora", "emoji": "🎵", "price": 55000, "colors": {"bg": "#0a0510", "accent": "#3a1a4a", "border": "#ff69b4"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": True, "glow": 2}},
        "cobalto": {"name": "Cobalto", "emoji": "🔵", "price": 60000, "colors": {"bg": "#05050d", "accent": "#1a1a6a", "border": "#0047ab"}, "effects": {"particles": 50, "sparkles": 15, "stripes": True, "grid": False, "glow": 1}},
        "neon_v2": {"name": "Neon II", "emoji": "💜", "price": 60000, "colors": {"bg": "#050510", "accent": "#1a1a5a", "border": "#ff00ff"}, "effects": {"particles": 110, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "neon_pulse", "intensity": 3}},
        "lava": {"name": "Lava", "emoji": "🔴", "price": 60000, "colors": {"bg": "#100505", "accent": "#6a1a1a", "border": "#ff0000"}, "effects": {"particles": 120, "sparkles": 35, "stripes": True, "grid": False, "glow": 3, "type": "embers", "intensity": 3}},
        "toxico": {"name": "Toxico", "emoji": "☢️", "price": 60000, "colors": {"bg": "#050d05", "accent": "#1a5a1a", "border": "#00ff00"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": True, "glow": 3, "type": "neon_pulse", "intensity": 2}},
        "tempestade_gelo": {"name": "Tempestade de Gelo", "emoji": "🧊", "price": 60000, "colors": {"bg": "#050a0d", "accent": "#1a4a5a", "border": "#b0e0e6"}, "effects": {"particles": 100, "sparkles": 40, "stripes": False, "grid": True, "glow": 2, "type": "rain", "intensity": 2}},
        "metal": {"name": "Metal", "emoji": "🔩", "price": 60000, "colors": {"bg": "#0a0a0a", "accent": "#4a4a4a", "border": "#c0c0c0"}, "effects": {"particles": 40, "sparkles": 15, "stripes": True, "grid": False, "glow": 1}},
        "cromado": {"name": "Cromado", "emoji": "🪞", "price": 60000, "colors": {"bg": "#0a0a0a", "accent": "#4a4a4a", "border": "#d4d4d4"}, "effects": {"particles": 50, "sparkles": 18, "stripes": True, "grid": False, "glow": 1}},
        "vaporwave": {"name": "Vaporwave", "emoji": "🌴", "price": 60000, "colors": {"bg": "#0d050d", "accent": "#4a1a4a", "border": "#ff71ce"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": True, "glow": 2, "type": "neon_pulse", "intensity": 2}},
        "oceano_lunar": {"name": "Oceano Lunar", "emoji": "🌙", "price": 65000, "colors": {"bg": "#050510", "accent": "#1a2a4a", "border": "#87ceeb"}, "effects": {"particles": 100, "sparkles": 35, "stripes": False, "grid": False, "glow": 2, "type": "aurora", "intensity": 2}},
        "rubelita": {"name": "Rubelita", "emoji": "❤️", "price": 65000, "colors": {"bg": "#0d0508", "accent": "#5a1a2a", "border": "#e0115f"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": False, "glow": 2}},
        "interferencia": {"name": "Interferencia", "emoji": "📡", "price": 65000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#00ffff"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": True, "glow": 2, "type": "neon_pulse", "intensity": 2}},
        "sinestesia": {"name": "Sinestesia", "emoji": "🎨", "price": 70000, "colors": {"bg": "#0d050d", "accent": "#4a1a3a", "border": "#da70d6"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": True, "glow": 2, "type": "nebula", "intensity": 2}},
        "lua_sangue": {"name": "Lua de Sangue", "emoji": "🌑", "price": 70000, "colors": {"bg": "#100505", "accent": "#4a1a1a", "border": "#8b0000"}, "effects": {"particles": 60, "sparkles": 12, "stripes": False, "grid": False, "glow": 1, "type": "embers", "intensity": 1}},
        "abismo": {"name": "Abismo", "emoji": "🕳️", "price": 70000, "colors": {"bg": "#050505", "accent": "#0f0f1a", "border": "#3a3a5f"}, "effects": {"particles": 60, "sparkles": 10, "stripes": False, "grid": False, "glow": 1, "type": "shadow_waves", "intensity": 2}},
        "eclipse": {"name": "Eclipse", "emoji": "🌑", "price": 70000, "colors": {"bg": "#0a0a0a", "accent": "#2a2a2a", "border": "#5a5a7a"}, "effects": {"particles": 60, "sparkles": 12, "stripes": False, "grid": False, "glow": 2, "type": "aurora", "intensity": 1}},
        "espiral": {"name": "Espiral", "emoji": "🔮", "price": 75000, "colors": {"bg": "#0d050d", "accent": "#4a1a4a", "border": "#da70d6"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": True, "glow": 2, "type": "vortex", "intensity": 2}},
        "seda": {"name": "Seda", "emoji": "🎀", "price": 75000, "colors": {"bg": "#0d0508", "accent": "#4a1a2a", "border": "#ffb6c1"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": True, "glow": 2}},
        "diamante": {"name": "Diamante", "emoji": "💎", "price": 75000, "colors": {"bg": "#0a0a0d", "accent": "#4a4a6a", "border": "#b9f2ff"}, "effects": {"particles": 110, "sparkles": 45, "stripes": False, "grid": True, "glow": 2, "type": "crystal", "intensity": 3}},
        "matrix": {"name": "Matrix", "emoji": "🔢", "price": 75000, "colors": {"bg": "#050d05", "accent": "#0a4a0a", "border": "#00ff00"}, "effects": {"particles": 110, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "rain", "intensity": 3}},
        "labirinto": {"name": "Labirinto", "emoji": "🏛️", "price": 75000, "colors": {"bg": "#0a0a0d", "accent": "#3a3a5a", "border": "#c0c0c0"}, "effects": {"particles": 70, "sparkles": 18, "stripes": True, "grid": True, "glow": 2, "type": "sacred_geometry", "intensity": 1}},
        "steampunk": {"name": "Steampunk", "emoji": "⚙️", "price": 75000, "colors": {"bg": "#0d0a05", "accent": "#6a4a1a", "border": "#b87333"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": True, "glow": 2}},
        "cyberpunk": {"name": "Cyberpunk", "emoji": "🤖", "price": 80000, "colors": {"bg": "#0d050d", "accent": "#4a1a3a", "border": "#ff00ff"}, "effects": {"particles": 120, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "neon_pulse", "intensity": 3}},
        "holograma": {"name": "Holograma", "emoji": "📱", "price": 80000, "colors": {"bg": "#0a0a0d", "accent": "#3a3a4a", "border": "#00ffff"}, "effects": {"particles": 120, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "neon_pulse", "intensity": 3}},
        "synthwave": {"name": "Synthwave", "emoji": "🌆", "price": 80000, "colors": {"bg": "#0a0510", "accent": "#3a1a4a", "border": "#ff00ff"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": True, "glow": 2, "type": "neon_pulse", "intensity": 2}},
        "veludo": {"name": "Veludo", "emoji": "🎭", "price": 80000, "colors": {"bg": "#0a050d", "accent": "#3a1a4a", "border": "#800080"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": True, "glow": 2, "type": "shadow_waves", "intensity": 2}},
        "tornada": {"name": "Tornada", "emoji": "🌪️", "price": 80000, "colors": {"bg": "#0a0a0a", "accent": "#3a3a3a", "border": "#a0a0a0"}, "effects": {"particles": 80, "sparkles": 20, "stripes": False, "grid": False, "glow": 2, "type": "vortex", "intensity": 2}},
        "cyborg": {"name": "Cyborg", "emoji": "🦾", "price": 80000, "colors": {"bg": "#0a0a0a", "accent": "#4a4a5a", "border": "#4682b4"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": True, "glow": 2, "type": "neon_pulse", "intensity": 1}},
        "digital": {"name": "Digital", "emoji": "💻", "price": 80000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#00ff00"}, "effects": {"particles": 110, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "rain", "intensity": 2}},
        "druida": {"name": "Druida", "emoji": "🌿", "price": 85000, "colors": {"bg": "#050a05", "accent": "#2a5a2a", "border": "#32cd32"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "petals", "intensity": 3}},
        "carmesim": {"name": "Carmesim", "emoji": "❤️", "price": 85000, "colors": {"bg": "#100505", "accent": "#5a1a1a", "border": "#dc143c"}, "effects": {"particles": 90, "sparkles": 28, "stripes": True, "grid": False, "glow": 2}},
        "vortex": {"name": "Vortex", "emoji": "🌀", "price": 85000, "colors": {"bg": "#050510", "accent": "#1a1a5a", "border": "#4169e1"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": True, "glow": 2, "type": "vortex", "intensity": 2}},
        "granito": {"name": "Granito", "emoji": "🪨", "price": 90000, "colors": {"bg": "#0a0a0a", "accent": "#4a4a4a", "border": "#808080"}, "effects": {"particles": 50, "sparkles": 15, "stripes": True, "grid": False, "glow": 1}},
        "nanotech": {"name": "Nanotech", "emoji": "🔬", "price": 90000, "colors": {"bg": "#0a0a0d", "accent": "#3a3a4a", "border": "#00bfff"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": True, "glow": 2, "type": "crystal", "intensity": 2}},
        "quantico": {"name": "Quantico", "emoji": "⚛️", "price": 90000, "colors": {"bg": "#050510", "accent": "#1a1a5a", "border": "#9370db"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": True, "glow": 2, "type": "vortex", "intensity": 2}},
        "sonico": {"name": "Sonico", "emoji": "🔊", "price": 90000, "colors": {"bg": "#0a050d", "accent": "#3a1a4a", "border": "#ff1493"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": True, "glow": 2}},
        "tsunami": {"name": "Tsunami", "emoji": "🌊", "price": 90000, "colors": {"bg": "#050510", "accent": "#0a2a4a", "border": "#0080ff"}, "effects": {"particles": 90, "sparkles": 25, "stripes": False, "grid": False, "glow": 2, "type": "aurora", "intensity": 2}},
        "alexandrita": {"name": "Alexandrita", "emoji": "🟣", "price": 90000, "colors": {"bg": "#0d050d", "accent": "#4a1a4a", "border": "#9b59b6"}, "effects": {"particles": 110, "sparkles": 40, "stripes": True, "grid": True, "glow": 2}},
        "elfico": {"name": "El fico", "emoji": "🧝", "price": 100000, "colors": {"bg": "#050d08", "accent": "#1a5a2a", "border": "#98fb98"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "petals", "intensity": 3}},
        "dragao": {"name": "Dragao", "emoji": "🐉", "price": 100000, "colors": {"bg": "#100505", "accent": "#5a1a1a", "border": "#ff4500"}, "effects": {"particles": 120, "sparkles": 35, "stripes": True, "grid": False, "glow": 3, "type": "embers", "intensity": 2}},
        "hydra": {"name": "Hidra", "emoji": "🐍", "price": 100000, "colors": {"bg": "#050d05", "accent": "#1a5a1a", "border": "#228b22"}, "effects": {"particles": 120, "sparkles": 35, "stripes": True, "grid": False, "glow": 2, "type": "shadow_waves", "intensity": 2}},
        "poseidon": {"name": "Poseidon", "emoji": "🔱", "price": 100000, "colors": {"bg": "#050510", "accent": "#1a1a5a", "border": "#1e90ff"}, "effects": {"particles": 100, "sparkles": 30, "stripes": False, "grid": False, "glow": 2, "type": "aurora", "intensity": 2}},
        "titanio": {"name": "Titanio", "emoji": "🔩", "price": 100000, "colors": {"bg": "#0a0a0d", "accent": "#4a4a5a", "border": "#b0c4de"}, "effects": {"particles": 50, "sparkles": 18, "stripes": True, "grid": False, "glow": 1}},
        "marmore": {"name": "Marmore", "emoji": "🏛️", "price": 100000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#f0f0f0"}, "effects": {"particles": 80, "sparkles": 25, "stripes": True, "grid": True, "glow": 2}},
        "anoes_brancos": {"name": "Anoes Brancos", "emoji": "⚪", "price": 100000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#ffffff"}, "effects": {"particles": 110, "sparkles": 35, "stripes": True, "grid": True, "glow": 3, "type": "crystal", "intensity": 2}},
        "cyber_goth": {"name": "Cyber Goth", "emoji": "🤖", "price": 100000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#ff00ff"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": True, "glow": 2, "type": "neon_pulse", "intensity": 2}},
        "topazio_imperial": {"name": "Topazio Imperial", "emoji": "🟡", "price": 110000, "colors": {"bg": "#0d0c05", "accent": "#7a6a1a", "border": "#ffd700"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": False, "glow": 2, "type": "nebula", "intensity": 1}},
        "cristal_arcoiris": {"name": "Cristal Arco-iris", "emoji": "💎", "price": 120000, "colors": {"bg": "#0a0a0d", "accent": "#4a4a6a", "border": "#ff69b4"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "crystal", "intensity": 3}},
        "vazio": {"name": "Vazio", "emoji": "🕳️", "price": 120000, "colors": {"bg": "#050505", "accent": "#0f0f0f", "border": "#4a4a4a"}, "effects": {"particles": 40, "sparkles": 8, "stripes": False, "grid": False, "glow": 1, "type": "shadow_waves", "intensity": 1}},
        "hades": {"name": "Hades", "emoji": "💀", "price": 120000, "colors": {"bg": "#0a0505", "accent": "#3a1a1a", "border": "#8b0000"}, "effects": {"particles": 70, "sparkles": 15, "stripes": False, "grid": False, "glow": 2, "type": "embers", "intensity": 2}},
        "zeus": {"name": "Zeus", "emoji": "⚡", "price": 120000, "colors": {"bg": "#0d0d05", "accent": "#5a5a1a", "border": "#ffd700"}, "effects": {"particles": 110, "sparkles": 35, "stripes": True, "grid": False, "glow": 3, "type": "neon_pulse", "intensity": 3}},
        "reliquia": {"name": "Reliquia", "emoji": "🏺", "price": 120000, "colors": {"bg": "#0d0a05", "accent": "#6a5a1a", "border": "#daa520"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": False, "glow": 2, "type": "nebula", "intensity": 1}},
        "nebulosa": {"name": "Nebulosa", "emoji": "🔭", "price": 120000, "colors": {"bg": "#050510", "accent": "#2a1a4a", "border": "#8a2be2"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "nebula", "intensity": 3}},
        "noir": {"name": "Noir", "emoji": "🎩", "price": 120000, "colors": {"bg": "#050505", "accent": "#1a1a1a", "border": "#4a4a4a"}, "effects": {"particles": 50, "sparkles": 10, "stripes": False, "grid": False, "glow": 1, "type": "rain", "intensity": 1}},
        "vulcao": {"name": "Vulcao", "emoji": "🌋", "price": 120000, "colors": {"bg": "#100505", "accent": "#5a1a1a", "border": "#ff3300"}, "effects": {"particles": 110, "sparkles": 35, "stripes": True, "grid": True, "glow": 3, "type": "embers", "intensity": 3}},
        "feiteiceiro": {"name": "Feiticeiro", "emoji": "🧙", "price": 125000, "colors": {"bg": "#0a0510", "accent": "#3a1a4a", "border": "#9370db"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "nebula", "intensity": 3}},
        "feiticeiro": {"name": "Feiticeiro", "emoji": "🧙", "price": 125000, "colors": {"bg": "#0a0510", "accent": "#3a1a4a", "border": "#9370db"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "nebula", "intensity": 3}},
        "medusa": {"name": "Medusa", "emoji": "🐍", "price": 130000, "colors": {"bg": "#050d05", "accent": "#1a5a2a", "border": "#00fa9a"}, "effects": {"particles": 110, "sparkles": 35, "stripes": False, "grid": True, "glow": 2, "type": "vortex", "intensity": 2}},
        "tungstenio": {"name": "Tungstenio", "emoji": "⚙️", "price": 150000, "colors": {"bg": "#0a0a0a", "accent": "#3a3a3a", "border": "#696969"}, "effects": {"particles": 50, "sparkles": 18, "stripes": True, "grid": False, "glow": 1}},
        "piramide": {"name": "Piramide", "emoji": "🔺", "price": 150000, "colors": {"bg": "#0d0a05", "accent": "#6a5a1a", "border": "#ffd700"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": True, "glow": 3, "type": "sacred_geometry", "intensity": 2}},
        "arco_iris": {"name": "Arco-Iris", "emoji": "🌈", "price": 150000, "colors": {"bg": "#0a0a0d", "accent": "#3a3a4a", "border": "#ff00ff"}, "effects": {"particles": 110, "sparkles": 40, "stripes": True, "grid": True, "glow": 3, "type": "aurora", "intensity": 3}},
        "cometa": {"name": "Cometa", "emoji": "☄️", "price": 150000, "colors": {"bg": "#0a050d", "accent": "#3a1a4a", "border": "#ffa500"}, "effects": {"particles": 110, "sparkles": 40, "stripes": True, "grid": True, "glow": 3, "type": "vortex", "intensity": 3}},
        "athena": {"name": "Athena", "emoji": "🦉", "price": 150000, "colors": {"bg": "#0a0a0d", "accent": "#3a3a4a", "border": "#c0c0c0"}, "effects": {"particles": 110, "sparkles": 35, "stripes": True, "grid": False, "glow": 2}},
        "egipcio": {"name": "Egipcio", "emoji": "🏛️", "price": 150000, "colors": {"bg": "#0d0a05", "accent": "#6a5a1a", "border": "#ffd700"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": False, "glow": 2, "type": "sacred_geometry", "intensity": 2}},
        "deserto_glacial": {"name": "Deserto Glacial", "emoji": "🏜️", "price": 150000, "colors": {"bg": "#0d0c08", "accent": "#5a5a3a", "border": "#daa520"}, "effects": {"particles": 100, "sparkles": 30, "stripes": True, "grid": True, "glow": 2, "type": "rain", "intensity": 1}},
        "osmio": {"name": "Osmio", "emoji": "💎", "price": 150000, "colors": {"bg": "#0a0a0d", "accent": "#3a3a5a", "border": "#4169e1"}, "effects": {"particles": 50, "sparkles": 18, "stripes": True, "grid": False, "glow": 1}},
        "iridio": {"name": "Iridio", "emoji": "🪞", "price": 150000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#e0e0e0"}, "effects": {"particles": 50, "sparkles": 18, "stripes": True, "grid": False, "glow": 1}},
        "art_deco": {"name": "Art Deco", "emoji": "🏛️", "price": 150000, "colors": {"bg": "#0d0a05", "accent": "#6a5a1a", "border": "#c5a258"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": True, "glow": 2, "type": "sacred_geometry", "intensity": 2}},
        "paradoxo": {"name": "Paradoxo", "emoji": "♾️", "price": 150000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#9370db"}, "effects": {"particles": 100, "sparkles": 35, "stripes": True, "grid": True, "glow": 2, "type": "vortex", "intensity": 3}},
        "paladino": {"name": "Paladino", "emoji": "⚔️", "price": 160000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a3a", "border": "#ffd700"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "crystal", "intensity": 3}},
        "arcana": {"name": "Arcana", "emoji": "🔮", "price": 175000, "colors": {"bg": "#0d050d", "accent": "#4a1a4a", "border": "#ba55d3"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "nebula", "intensity": 3}},
        "pulsar": {"name": "Pulsar", "emoji": "⚡", "price": 180000, "colors": {"bg": "#050510", "accent": "#1a1a5a", "border": "#00bfff"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "neon_pulse", "intensity": 3}},
        "troia": {"name": "Troia", "emoji": "🏛️", "price": 180000, "colors": {"bg": "#0d0a05", "accent": "#5a4a2a", "border": "#daa520"}, "effects": {"particles": 90, "sparkles": 30, "stripes": True, "grid": False, "glow": 2}},
        "tempestade_neon": {"name": "Tempestade Neon", "emoji": "⚡", "price": 180000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#00ffff"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "neon_pulse", "intensity": 3}},
        "sombras_eternas": {"name": "Sombras Eternas", "emoji": "🌑", "price": 190000, "colors": {"bg": "#050505", "accent": "#1a1a2a", "border": "#483d8b"}, "effects": {"particles": 60, "sparkles": 10, "stripes": False, "grid": False, "glow": 1, "type": "shadow_waves", "intensity": 2}},
        "neon_dreams": {"name": "Neon Dreams", "emoji": "💡", "price": 200000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#00ffff"}, "effects": {"particles": 120, "sparkles": 40, "stripes": True, "grid": True, "glow": 3, "type": "neon_pulse", "intensity": 3}},
        "obsidiana_arcoiris": {"name": "Obsidiana Arco-iris", "emoji": "🌈", "price": 200000, "colors": {"bg": "#050505", "accent": "#2a2a2a", "border": "#ff69b4"}, "effects": {"particles": 140, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "aurora", "intensity": 3}},
        "supernova": {"name": "Supernova", "emoji": "💥", "price": 200000, "colors": {"bg": "#100505", "accent": "#6a1a1a", "border": "#ff6600"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "embers", "intensity": 3}},
        "buraco_negro": {"name": "Buraco Negro", "emoji": "🕳️", "price": 200000, "colors": {"bg": "#050505", "accent": "#0a0a0a", "border": "#5a0080"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "vortex", "intensity": 3}},
        "big_bang": {"name": "Big Bang", "emoji": "💫", "price": 200000, "colors": {"bg": "#0d0505", "accent": "#5a1a1a", "border": "#ff0000"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": False, "glow": 3, "type": "embers", "intensity": 3}},
        "pixel": {"name": "Pixel", "emoji": "🎮", "price": 200000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#00ff00"}, "effects": {"particles": 120, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "rain", "intensity": 3}},
        "japones": {"name": "Japones", "emoji": "⛩️", "price": 200000, "colors": {"bg": "#0d0505", "accent": "#5a1a1a", "border": "#ff0000"}, "effects": {"particles": 120, "sparkles": 40, "stripes": True, "grid": True, "glow": 3, "type": "petals", "intensity": 3}},
        "anjo": {"name": "Anjo", "emoji": "😇", "price": 200000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#fffacd"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "crystal", "intensity": 3}},
        "portal": {"name": "Portal", "emoji": "🌀", "price": 200000, "colors": {"bg": "#050510", "accent": "#1a1a5a", "border": "#9370db"}, "effects": {"particles": 140, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "vortex", "intensity": 3}},
        "ouro_liquido": {"name": "Ouro Liquido", "emoji": "🫗", "price": 200000, "colors": {"bg": "#0d0a05", "accent": "#7a6a1a", "border": "#ffc107"}, "effects": {"particles": 120, "sparkles": 40, "stripes": True, "grid": True, "glow": 3, "type": "nebula", "intensity": 3}},
        "quasar": {"name": "Quasar", "emoji": "💫", "price": 200000, "colors": {"bg": "#0d0505", "accent": "#5a1a1a", "border": "#ff6347"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "embers", "intensity": 3}},
        "entropia": {"name": "Entropia", "emoji": "🔥", "price": 200000, "colors": {"bg": "#100505", "accent": "#5a1a1a", "border": "#ff4500"}, "effects": {"particles": 120, "sparkles": 35, "stripes": True, "grid": False, "glow": 3, "type": "embers", "intensity": 3}},
        "magnetar": {"name": "Magnetar", "emoji": "🧲", "price": 220000, "colors": {"bg": "#05050d", "accent": "#1a1a4a", "border": "#0000cd"}, "effects": {"particles": 120, "sparkles": 40, "stripes": True, "grid": True, "glow": 3, "type": "vortex", "intensity": 3}},
        "necromante": {"name": "Necromante", "emoji": "💀", "price": 225000, "colors": {"bg": "#050505", "accent": "#2a1a2a", "border": "#8b008b"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "shadow_waves", "intensity": 3}},
        "infernal": {"name": "Infernal", "emoji": "🔥", "price": 250000, "colors": {"bg": "#100505", "accent": "#6a1a1a", "border": "#ff4500"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": False, "glow": 3, "type": "embers", "intensity": 3}},
        "divino": {"name": "Divino", "emoji": "👼", "price": 250000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#ffd700"}, "effects": {"particles": 110, "sparkles": 40, "stripes": True, "grid": False, "glow": 3, "type": "crystal", "intensity": 3}},
        "eterno": {"name": "Eterno", "emoji": "♾️", "price": 250000, "colors": {"bg": "#0a0a0d", "accent": "#3a3a4a", "border": "#e6e6fa"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "aurora", "intensity": 3}},
        "infinito": {"name": "Infinito", "emoji": "🔮", "price": 250000, "colors": {"bg": "#0d050d", "accent": "#4a1a4a", "border": "#ff00ff"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "vortex", "intensity": 3}},
        "tempestade": {"name": "Tempestade", "emoji": "⛈️", "price": 250000, "colors": {"bg": "#0a0a0d", "accent": "#3a3a5a", "border": "#4169e1"}, "effects": {"particles": 100, "sparkles": 25, "stripes": False, "grid": False, "glow": 3, "type": "rain", "intensity": 3}},
        "platina_negra": {"name": "Platina Negra", "emoji": "⚫", "price": 250000, "colors": {"bg": "#050505", "accent": "#3a3a3a", "border": "#8a8a8a"}, "effects": {"particles": 120, "sparkles": 40, "stripes": True, "grid": True, "glow": 3, "type": "crystal", "intensity": 2}},
        "wormhole": {"name": "Wormhole", "emoji": "🕳️", "price": 250000, "colors": {"bg": "#050505", "accent": "#0a0a2a", "border": "#4b0082"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "vortex", "intensity": 3}},
        "esfinge": {"name": "Esfinge", "emoji": "🗿", "price": 250000, "colors": {"bg": "#0d0a05", "accent": "#5a4a2a", "border": "#daa520"}, "effects": {"particles": 110, "sparkles": 38, "stripes": True, "grid": True, "glow": 3, "type": "sacred_geometry", "intensity": 2}},
        "sangue_sagrado": {"name": "Sangue Sagrado", "emoji": "🩸", "price": 275000, "colors": {"bg": "#0d0505", "accent": "#5a1a1a", "border": "#b22222"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "embers", "intensity": 2}},
        "jade_imperial": {"name": "Jade Imperial", "emoji": "💚", "price": 275000, "colors": {"bg": "#050d08", "accent": "#1a6a3a", "border": "#00a86b"}, "effects": {"particles": 120, "sparkles": 40, "stripes": True, "grid": True, "glow": 3, "type": "petals", "intensity": 3}},
        "perola_imperial": {"name": "Perola Imperial", "emoji": "🤍", "price": 300000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#fdeef4"}, "effects": {"particles": 120, "sparkles": 40, "stripes": True, "grid": True, "glow": 3, "type": "crystal", "intensity": 3}},
        "demonio": {"name": "Demonio", "emoji": "😈", "price": 300000, "colors": {"bg": "#100505", "accent": "#5a1a1a", "border": "#ff0000"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "embers", "intensity": 3}},
        "mitico": {"name": "Mitico", "emoji": "⚜️", "price": 300000, "colors": {"bg": "#0d0a05", "accent": "#6a5a1a", "border": "#ffd700"}, "effects": {"particles": 120, "sparkles": 40, "stripes": True, "grid": False, "glow": 3, "type": "nebula", "intensity": 2}},
        "lendario": {"name": "Lendario", "emoji": "🏆", "price": 300000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#ffd700"}, "effects": {"particles": 120, "sparkles": 40, "stripes": True, "grid": False, "glow": 3, "type": "crystal", "intensity": 3}},
        "ascensao": {"name": "Ascensao", "emoji": "🕊️", "price": 300000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#f0f8ff"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "aurora", "intensity": 3}},
        "via_lactea": {"name": "Via Lactea", "emoji": "🌌", "price": 300000, "colors": {"bg": "#050510", "accent": "#1a1a3a", "border": "#e6e6fa"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "nebula", "intensity": 3}},
        "dimensional": {"name": "Dimensional", "emoji": "🕳️", "price": 300000, "colors": {"bg": "#050510", "accent": "#0a0a3a", "border": "#4b0082"}, "effects": {"particles": 120, "sparkles": 40, "stripes": True, "grid": True, "glow": 3, "type": "vortex", "intensity": 3}},
        "buraco_branco": {"name": "Buraco Branco", "emoji": "🕳️", "price": 325000, "colors": {"bg": "#0d0d0d", "accent": "#4a4a4a", "border": "#f5f5f5"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "crystal", "intensity": 3}},
        "celestial": {"name": "Celestial", "emoji": "☁️", "price": 350000, "colors": {"bg": "#0a0510", "accent": "#3a1a5a", "border": "#dda0dd"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": True, "glow": 3, "type": "aurora", "intensity": 3}},
        "tita": {"name": "Tita", "emoji": "💪", "price": 350000, "colors": {"bg": "#0a0a0a", "accent": "#4a4a4a", "border": "#c0c0c0"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3}},
        "colossal": {"name": "Colossal", "emoji": "🗿", "price": 350000, "colors": {"bg": "#0a0a0a", "accent": "#4a4a4a", "border": "#808080"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3}},
        "supernova_v2": {"name": "Supernova II", "emoji": "💥", "price": 350000, "colors": {"bg": "#100505", "accent": "#6a2a1a", "border": "#ff8c00"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "embers", "intensity": 3}},
        "ouro_rosa": {"name": "Ouro Rosa", "emoji": "🌹", "price": 350000, "colors": {"bg": "#0d0508", "accent": "#5a2a3a", "border": "#e8b4b8"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "petals", "intensity": 3}},
        "cosmico_v2": {"name": "Cosmico II", "emoji": "🌌", "price": 400000, "colors": {"bg": "#050510", "accent": "#1a1a5a", "border": "#9370db"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "nebula", "intensity": 3}},
        "divino_v2": {"name": "Divino II", "emoji": "✨", "price": 400000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#ffd700"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "crystal", "intensity": 3}},
        "ascendente": {"name": "Ascendente", "emoji": "🌟", "price": 400000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#fffacd"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "aurora", "intensity": 3}},
        "estrela_negra": {"name": "Estrela Negra", "emoji": "⭐", "price": 400000, "colors": {"bg": "#050505", "accent": "#1a1a1a", "border": "#4a4a6a"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "vortex", "intensity": 3}},
        "safira_imperial": {"name": "Safira Imperial", "emoji": "👑", "price": 400000, "colors": {"bg": "#050510", "accent": "#0a1a5a", "border": "#0f52ba"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "aurora", "intensity": 3}},
        "esmeralda_colombiana": {"name": "Esmeralda Colombiana", "emoji": "💚", "price": 425000, "colors": {"bg": "#050d05", "accent": "#1a5a2a", "border": "#046307"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "petals", "intensity": 3}},
        "dragao_fogo": {"name": "Dragao de Fogo", "emoji": "🐉", "price": 450000, "colors": {"bg": "#100505", "accent": "#6a1a1a", "border": "#ff4500"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "embers", "intensity": 3}},
        "eterno_v2": {"name": "Eterno II", "emoji": "♾️", "price": 450000, "colors": {"bg": "#0a0a0d", "accent": "#3a3a4a", "border": "#e6e6fa"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "aurora", "intensity": 3}},
        "infinito_v2": {"name": "Infinito II", "emoji": "🔮", "price": 450000, "colors": {"bg": "#0d050d", "accent": "#4a1a4a", "border": "#ff00ff"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "vortex", "intensity": 3}},
        "rubi_birman": {"name": "Rubis Birman", "emoji": "❤️", "price": 450000, "colors": {"bg": "#100505", "accent": "#5a1a1a", "border": "#9b111e"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "embers", "intensity": 3}},
        "supremo": {"name": "Supremo", "emoji": "👑", "price": 500000, "colors": {"bg": "#0d0a05", "accent": "#6a5a1a", "border": "#ffd700"}, "effects": {"particles": 130, "sparkles": 45, "stripes": True, "grid": False, "glow": 3, "type": "nebula", "intensity": 3}},
        "absoluto": {"name": "Absoluto", "emoji": "🌟", "price": 500000, "colors": {"bg": "#0d0d0d", "accent": "#5a5a5a", "border": "#ffffff"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "crystal", "intensity": 3}},
        "ultima": {"name": "Ultima", "emoji": "💫", "price": 500000, "colors": {"bg": "#050510", "accent": "#1a1a5a", "border": "#00ffff"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "neon_pulse", "intensity": 3}},
        "cosmica_infinita": {"name": "Cosmica Infinita", "emoji": "✨", "price": 500000, "colors": {"bg": "#050510", "accent": "#1a1a4a", "border": "#ff00ff"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "nebula", "intensity": 3}},
        "diamante_negro": {"name": "Diamante Negro", "emoji": "💎", "price": 500000, "colors": {"bg": "#050505", "accent": "#1a1a1a", "border": "#4a4a4a"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "crystal", "intensity": 3}},
        "big_crunch": {"name": "Big Crunch", "emoji": "💥", "price": 550000, "colors": {"bg": "#0a0505", "accent": "#3a1a1a", "border": "#ff4444"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "embers", "intensity": 3}},
        "licor_estelar": {"name": "Licor Estelar", "emoji": "🍸", "price": 600000, "colors": {"bg": "#0a0510", "accent": "#3a1a5a", "border": "#ff1493"}, "effects": {"particles": 150, "sparkles": 50, "stripes": True, "grid": True, "glow": 3, "type": "nebula", "intensity": 3}},
    }



    # Profile Shop - Borders

    profile_borders: dict = {

        "default": {"name": "Padrão", "emoji": "⬜", "price": 0, "color": "#d946ef"},
        "gold": {"name": "Dourado", "emoji": "🥇", "price": 10000, "color": "#ffd700"},
        "diamond": {"name": "Diamante", "emoji": "💎", "price": 20000, "color": "#22d3ee"},
        "ruby": {"name": "Rubi", "emoji": "❤️", "price": 15000, "color": "#ef4444"},
        "emerald": {"name": "Esmeralda", "emoji": "💚", "price": 15000, "color": "#22c55e"},
        "sapphire": {"name": "Safira", "emoji": "💙", "price": 15000, "color": "#3b82f6"},
        "amethyst": {"name": "Ametista", "emoji": "💜", "price": 20000, "color": "#a855f7"},
        "rainbow": {"name": "Arco-Íris", "emoji": "🌈", "price": 50000, "color": "#f59e0b"},
        "fire": {"name": "Fogo", "emoji": "🔥", "price": 30000, "color": "#f97316"},
        "ice": {"name": "Gelo", "emoji": "❄️", "price": 30000, "color": "#7dd3fc"},
        "galaxy": {"name": "Galáxia", "emoji": "🌌", "price": 40000, "color": "#c084fc"},
        "shadow": {"name": "Shadow", "emoji": "🖤", "price": 60000, "color": "#525252"},
        "neon_pink": {"name": "Neon Rosa", "emoji": "💗", "price": 25000, "color": "#f472b6"},
        "neon_cyan": {"name": "Neon Cyan", "emoji": "🩵", "price": 25000, "color": "#22d3ee"},
        "cherry": {"name": "Cereja", "emoji": "🍒", "price": 20000, "color": "#e11d48"},
        "blood": {"name": "Sangue", "emoji": "🩸", "price": 35000, "color": "#991b1b"},
        "platinum": {"name": "Platina", "emoji": "⚪", "price": 45000, "color": "#e2e8f0"},
        "obsidian": {"name": "Obsidiana", "emoji": "🖤", "price": 30000, "color": "#18181b"},
        "neon_green": {"name": "Neon Verde", "emoji": "💚", "price": 25000, "color": "#4ade80"},
        "neon_yellow": {"name": "Neon Amarelo", "emoji": "💛", "price": 25000, "color": "#facc15"},
        "chrome": {"name": "Cromado", "emoji": "🪞", "price": 50000, "color": "#d4d4d8"},
        "sakura": {"name": "Sakura", "emoji": "🌸", "price": 20000, "color": "#ec4899"},
        "ocean": {"name": "Oceano", "emoji": "🌊", "price": 20000, "color": "#0ea5e9"},
        "toxic": {"name": "Tóxico", "emoji": "☢️", "price": 40000, "color": "#a3e635"},
        "royal": {"name": "Real", "emoji": "👑", "price": 35000, "color": "#facc15"},
        "dragon": {"name": "Dragão", "emoji": "🐉", "price": 55000, "color": "#f97316"},
        "void": {"name": "Vazio", "emoji": "🕳️", "price": 70000, "color": "#09090b"},
        "cosmic": {"name": "Cósmico", "emoji": "🪐", "price": 45000, "color": "#c084fc"},
        "ember": {"name": "Brasa", "emoji": "🔥", "price": 32000, "color": "#ff6347"},
        "moonlight": {"name": "Luar", "emoji": "🌙", "price": 28000, "color": "#c0c0c0"},
        "aurora_border": {"name": "Aurora", "emoji": "🌈", "price": 55000, "color": "#00ffff"},
        "sakura_border": {"name": "Sakura", "emoji": "🌸", "price": 25000, "color": "#ffb7c5"},
        "golden_dust": {"name": "Poeira Dourada", "emoji": "✨", "price": 40000, "color": "#ffd700"},
        "deep_sea": {"name": "Mar Profundo", "emoji": "🌊", "price": 35000, "color": "#0077be"},
        "lavender": {"name": "Lavanda", "emoji": "💜", "price": 22000, "color": "#b57edc"},
        "jade_border": {"name": "Jade", "emoji": "💚", "price": 30000, "color": "#00a86b"},
        "crimson_border": {"name": "Carmesim", "emoji": "❤️", "price": 45000, "color": "#dc143c"},
        "frost": {"name": "Geada", "emoji": "❄️", "price": 28000, "color": "#e0f0ff"},
        "neon_purple": {"name": "Neon Roxo", "emoji": "💜", "price": 35000, "color": "#bf00ff"},
        "copper_border": {"name": "Cobre", "emoji": "🔶", "price": 18000, "color": "#b87333"},
        "emerald_border": {"name": "Esmeralda", "emoji": "💚", "price": 50000, "color": "#50c878"},
        "void_border": {"name": "Vazio", "emoji": "🕳️", "price": 75000, "color": "#1a1a2e"},
        "solar_flare": {"name": "Explosao Solar", "emoji": "☀️", "price": 60000, "color": "#ff8c00"},
        "infernal_border": {"name": "Infernal", "emoji": "😈", "price": 80000, "color": "#ff0000"},
        "ethereal_border": {"name": "Etereo", "emoji": "👻", "price": 65000, "color": "#e0e0ff"},
    }

    # Shop Items
    shop_items: dict = {
        "caixa_ferro": {
            "name": "Caixa de Ferro",
            "emoji": "📦",
            "price": 5000,
            "description": "Uma caixa comum que pode conter itensbasicos.",
            "effect": {"type": "lootbox", "tier": "common", "min_reward": 100, "max_reward": 5000},
        },
        "caixa_prata": {
            "name": "Caixa de Prata",
            "emoji": "📦",
            "price": 15000,
            "description": "Uma caixa de prata com chance de itens raros.",
            "effect": {"type": "lootbox", "tier": "rare", "min_reward": 500, "max_reward": 20000},
        },
        "caixa_ouro": {
            "name": "Caixa de Ouro",
            "emoji": "📦",
            "price": 50000,
            "description": "Uma caixa dourada com alta chance de itens epicos.",
            "effect": {"type": "lootbox", "tier": "epic", "min_reward": 2000, "max_reward": 75000},
        },
        "caixa_diamante": {
            "name": "Caixa de Diamante",
            "emoji": "📦",
            "price": 150000,
            "description": "A caixa mais rara. Contem lendarios!",
            "effect": {"type": "lootbox", "tier": "legendary", "min_reward": 10000, "max_reward": 300000},
        },
        "pocao_sortudo": {
            "name": "Pocao da Sorte",
            "emoji": "🍀",
            "price": 10000,
            "description": "Aumenta sua sorte em apostas por 1 hora.",
            "effect": {"type": "boost", "stat": "luck", "multiplier": 1.5, "duration": 3600},
        },
        "pocao_exp": {
            "name": "Pocao de Experiencia",
            "emoji": "🧪",
            "price": 8000,
            "description": "Dobra o XP ganho por 1 hora.",
            "effect": {"type": "boost", "stat": "xp", "multiplier": 2.0, "duration": 3600},
        },
        "escudo": {
            "name": "Escudo Protetor",
            "emoji": "🛡️",
            "price": 25000,
            "description": "Protege voce de um roubo por 6 horas.",
            "effect": {"type": "protection", "anti_rob": True, "duration": 21600},
        },
        "chave_misteriosa": {
            "name": "Chave Misteriosa",
            "emoji": "🗝️",
            "price": 20000,
            "description": "Abre portas secretas em aventuras com recompensas extras.",
            "effect": {"type": "adventure_bonus", "bonus_reward": 5000},
        },
        "amuleto_fortuna": {
            "name": "Amuleto da Fortuna",
            "emoji": "🔮",
            "price": 75000,
            "description": "Aumenta o premio da roda da sorte em 50%.",
            "effect": {"type": "boost", "stat": "wheel", "multiplier": 1.5},
        },
        "capa_invisivel": {
            "name": "Capa Invisivel",
            "emoji": "🧥",
            "price": 40000,
            "description": "Torna voce invisível por 30 min, impossivel de ser roubado.",
            "effect": {"type": "protection", "anti_rob": True, "duration": 1800},
        },
        "martelo_gigante": {
            "name": "Martelo Gigante",
            "emoji": "🔨",
            "price": 30000,
            "description": "Dobra o dano em batalhas PvP por 2 horas.",
            "effect": {"type": "boost", "stat": "attack", "multiplier": 2.0, "duration": 7200},
        },
        "anel_rubí": {
            "name": "Anel de Rubi",
            "emoji": "💍",
            "price": 100000,
            "description": "Aumenta todas as recompensas em 25% por 3 horas.",
            "effect": {"type": "boost", "stat": "all_rewards", "multiplier": 1.25, "duration": 10800},
        },
        "bilhete_sorte": {
            "name": "Bilhete da Sorte",
            "emoji": "🎫",
            "price": 3000,
            "description": "Garante uma tentativa extra na loteria.",
            "effect": {"type": "consumable", "action": "extra_lottery_ticket"},
        },
        "token_duelo": {
            "name": "Token de Duelo",
            "emoji": "⚔️",
            "price": 12000,
            "description": "Permite desafiar qualquer jogador sem cooldown.",
            "effect": {"type": "consumable", "action": "skip_duel_cooldown"},
        },
        "baú_arte": {
            "name": "Bau Artefato",
            "emoji": "🏺",
            "price": 60000,
            "description": "Contem artefatos raros que podem ser vendidos ou colecionados.",
            "effect": {"type": "lootbox", "tier": "artifact", "min_reward": 5000, "max_reward": 100000},
        },
        "grito_guerra": {
            "name": "Grito de Guerra",
            "emoji": "📯",
            "price": 5000,
            "description": "Aumenta sua reputacao em +10 nos rankings sociais.",
            "effect": {"type": "reputation", "amount": 10},
        },
    }

    # Moderation Settings
    max_warnings: int = 5
    mute_role_name: str = "Mutado"

    # Rank Thresholds
    rank_thresholds: dict = {
        1000000: ("👑 MAGNATA IMPERIAL", 0xFFD700),
        500000: ("💎 BILIONÁRIO", 0x00E5FF),
        250000: ("🔥 ELITE", 0xFF5500),
        100000: ("💰 RICO", 0x2ECC71),
        50000: ("💵 PROSPERO", 0x3498DB),
        10000: ("💴 TRABALHADOR", 0x9B59B6),
        0: ("🪙 INICIANTE", 0x95A5A6),
    }

    # Achievements
    achievements: dict = {
        "first_daily": "🏦 Primeiro Daily",
        "streak_7": "🔥 Sequência de 7 dias",
        "streak_30": "🌟 Sequência de 30 dias",
        "rich_100k": "💰 100K Koins",
        "rich_1m": "💎 1M Koins",
        "first_bet": "🎰 Primeira Aposta",
        "jackpot": "💎 Jackpot!",
        "first_rob": "🦹 Primeiro Roubo",
        "rich_500k": "👑 500K Koins",
        "commands_100": "📜 100 Comandos",
        "commands_1000": "🏆 1000 Comandos",
        "first_mine": "⛏️ Primeira Mineração",
        "mines_50": "💎 Minerador Expert",
        "first_crime": "🕵️ Primeiro Crime",
        "crime_10": "🎭 Membro da Mafia",
        "crime_50": "👑 Rei do Crime",
        "blackjack_21": "🃏 Blackjack Natural",
        "duel_win_5": "⚔️ Mestre do Duelo",
        "duel_win_10": "🏆 Lenda do Duelo",
        "cofre_100k": "🏦 Poupança 100K",
        "cofre_500k": "👑 Poupança 500K",
        "lottery_win": "🎰 Ganhador da Loteria",
        "coinflip_10": "🪙 Cara ou Coroa Expert",
        "all_commands": "🌟 Mestre dos Comandos",
        "social_100": "🤗 100 interações sociais",
        "quiz_master": "🧠 Acerte 10 quizzes",
        "adventurer": "🗺️ Complete 10 aventuras",
        "lucky_7": "🍀 Ganhe 7 vezes seguidas",
        "big_spender": "💸 Gaste 100000 koins",
        "collector": "🎒 Colete 50 itens",
    }


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

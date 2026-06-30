from __future__ import annotations

import asyncio
import random
import time
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from embed_builder import KlausEmbed as make_embed

if TYPE_CHECKING:
    from klaus import KlausBot

HUG_GIFS = [
    "https://media.giphy.com/media/l2QDM9Jnim1YVILXa/giphy.gif",
    "https://media.giphy.com/media/od5H3PmEG5EVq/giphy.gif",
    "https://media.giphy.com/media/HaC1WdpkL3W00/giphy.gif",
    "https://media.giphy.com/media/wnsgren9NtITS/giphy.gif",
]

KISS_GIFS = [
    "https://media.giphy.com/media/bm2O3nXTcKACU/giphy.gif",
    "https://media.giphy.com/media/G3va31oEEnIkM/giphy.gif",
    "https://media.giphy.com/media/FqBTvSNjNzeZG/giphy.gif",
]

SLAP_GIFS = [
    "https://media.giphy.com/media/Gf3AUz3eBNbTW/giphy.gif",
    "https://media.giphy.com/media/jLeyZWgtwgr2U/giphy.gif",
    "https://media.giphy.com/media/RXGNsyRb1hDJm/giphy.gif",
]

PAT_GIFS = [
    "https://media.giphy.com/media/109ltuoSQT212w/giphy.gif",
    "https://media.giphy.com/media/ARSp9T7wwxNcs/giphy.gif",
    "https://media.giphy.com/media/L2z7dnOduqEow/giphy.gif",
]


# =========================
# VIEW: Revidar (social)
# =========================

SOCIAL_MAP: dict[str, dict[str, object]] = {
    "hug": {
        "emoji": "\U0001f917",
        "label": "Revidar Abraço",
        "gifs": HUG_GIFS,
        "color": 0xD946EF,
        "verb": "abraçou",
    },
    "kiss": {
        "emoji": "\U0001f48b",
        "label": "Revidar Beijo",
        "gifs": KISS_GIFS,
        "color": 0xEC4899,
        "verb": "beijou",
    },
    "slap": {
        "emoji": "\U0001f44b",
        "label": "Revidar Tapa",
        "gifs": SLAP_GIFS,
        "color": 0xEF4444,
        "verb": "deu um tapa em",
    },
    "pat": {
        "emoji": "\U0001f970",
        "label": "Revidar Carinho",
        "gifs": PAT_GIFS,
        "color": 0xF0ABFC,
        "verb": "fez carinho em",
    },
}

SOCIAL_STATS: dict[int, dict[str, int]] = {}


def _track_social(guild_id: int, action: str) -> None:
    if guild_id not in SOCIAL_STATS:
        SOCIAL_STATS[guild_id] = {}
    SOCIAL_STATS[guild_id][action] = SOCIAL_STATS[guild_id].get(action, 0) + 1


class SocialRevidarButton(discord.ui.Button["SocialView"]):
    def __init__(self, action: str) -> None:
        info = SOCIAL_MAP[action]
        super().__init__(
            style=discord.ButtonStyle.primary,
            label=str(info["label"]),
            emoji=str(info["emoji"]),
            custom_id=f"social_revidar_{action}",
        )
        self.action = action

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        original_author_id = self.view.original_author_id
        target_id = self.view.target_id

        if interaction.user.id != target_id:
            await interaction.response.send_message(
                embed=make_embed.error("Ei!", "Só quem recebeu pode revidar!"),
                ephemeral=True,
            )
            return

        info = SOCIAL_MAP[self.action]
        gifs = list(info["gifs"])
        random.shuffle(gifs)

        if interaction.guild:
            _track_social(interaction.guild.id, self.action)

        embed = (
            make_embed(int(info["color"]))
            .title(f"{info['emoji']} {info['label']}!")
            .desc(f"{interaction.user.mention} revidou para <@{original_author_id}>!")
            .image(gifs[0])
            .timestamp()
            .footer("Klaus Social - Revanche")
            .build()
        )
        await interaction.response.send_message(embed=embed)


class SocialView(discord.ui.View):
    def __init__(self, original_author_id: int, target_id: int, action: str) -> None:
        super().__init__(timeout=60)
        self.original_author_id = original_author_id
        self.target_id = target_id
        self.add_item(SocialRevidarButton(action))


# =========================
# VIEW: Batalha Revanche (enhanced)
# =========================

DICE_FACES = ["⚀", "⚁", "⚂", "⚃", "⚄", "⚅"]


class BatalhaRevancheButton(discord.ui.Button["BatalhaView"]):
    def __init__(self) -> None:
        super().__init__(
            style=discord.ButtonStyle.danger,
            label="Revanche!",
            emoji="\u2694\ufe0f",
            custom_id="batalha_revanche",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        p1_id = self.view.p1_id
        p2_id = self.view.p2_id

        if interaction.user.id not in (p1_id, p2_id):
            await interaction.response.send_message(
                embed=make_embed.error("Ei!", "Só os jogadores podem pedir revanche!"),
                ephemeral=True,
            )
            return

        p1 = interaction.guild.get_member(p1_id) if interaction.guild else None
        p2 = interaction.guild.get_member(p2_id) if interaction.guild else None
        if not p1 or not p2:
            await interaction.response.send_message(
                embed=make_embed.error("Membros não encontrados", "Um ou ambos os jogadores não estão no servidor."),
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        hp1, hp2 = 100, 100
        for i in range(3):
            r1, r2 = random.randint(1, 6), random.randint(1, 6)
            d1 = DICE_FACES[r1 - 1]
            d2 = DICE_FACES[r2 - 1]
            hp1 -= r2 * 3
            hp2 -= r1 * 3
            hp1 = max(0, hp1)
            hp2 = max(0, hp2)
            bar1 = "\u2588" * (hp1 // 5) + "\u2591" * (20 - hp1 // 5)
            bar2 = "\u2588" * (hp2 // 5) + "\u2591" * (20 - hp2 // 5)
            embed = (
                make_embed("purple")
                .title(f"Revanche! - Turno {i + 1}/3")
                .desc(
                    f"```\n  {p1.display_name}  vs  {p2.display_name}\n```\n"
                    f"**{p1.display_name}**: {d1} **{r1}**\n`{bar1}` **{hp1}** HP\n\n"
                    f"**{p2.display_name}**: {d2} **{r2}**\n`{bar2}` **{hp2}** HP"
                )
                .footer("Klaus Battle Arena - Revanche")
                .build()
            )
            await interaction.edit_original_response(embed=embed)
            await asyncio.sleep(1.0)

        if hp1 > hp2:
            winner = p1
        elif hp2 > hp1:
            winner = p2
        else:
            winner = None

        final_bar1 = "\u2588" * (hp1 // 5) + "\u2591" * (20 - hp1 // 5)
        final_bar2 = "\u2588" * (hp2 // 5) + "\u2591" * (20 - hp2 // 5)

        if winner:
            result_text = f"\U0001f3c6 **{winner.display_name}** venceu a revanche!"
        else:
            result_text = f"\U0001f91d **Empate!**"

        embed = (
            make_embed("purple")
            .title("Revanche! - Resultado Final")
            .desc(
                f"```\n  {p1.display_name}  vs  {p2.display_name}\n```\n"
                f"**{p1.display_name}**\n`{final_bar1}` **{hp1}** HP\n\n"
                f"**{p2.display_name}**\n`{final_bar2}` **{hp2}** HP\n\n{result_text}"
            )
            .footer("Klaus Battle Arena - Revanche")
            .build()
        )
        await interaction.edit_original_response(embed=embed)


class BatalhaView(discord.ui.View):
    def __init__(self, p1_id: int, p2_id: int) -> None:
        super().__init__(timeout=60)
        self.p1_id = p1_id
        self.p2_id = p2_id
        self.add_item(BatalhaRevancheButton())


# =========================
# VIEW: Coin Jogar Novamente
# =========================

class CoinReplayButton(discord.ui.Button["CoinView"]):
    def __init__(self) -> None:
        super().__init__(
            style=discord.ButtonStyle.success,
            label="Jogar Novamente",
            emoji="\U0001fa99",
            custom_id="coin_replay",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        result = random.choice(["Cara", "Coroa"])
        cor = 0xF59E0B if result == "Cara" else 0x8B5CF6

        embed = (
            make_embed(cor)
            .title("Moeda!")
            .desc(f"Resultado: **{result}**")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .footer("Klaus Coin")
            .build()
        )
        await interaction.response.send_message(embed=embed, view=CoinView())


class CoinView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=30)
        self.add_item(CoinReplayButton())


# =========================
# VIEW: Dado Jogar Novamente
# =========================

class DadoReplayButton(discord.ui.Button["DadoView"]):
    def __init__(self, faces: int) -> None:
        super().__init__(
            style=discord.ButtonStyle.success,
            label="Jogar Novamente",
            emoji="\U0001f3b2",
            custom_id="dado_replay",
        )
        self.faces = faces

    async def callback(self, interaction: discord.Interaction) -> None:
        result = random.randint(1, self.faces)
        embed = (
            make_embed("purple")
            .title("Dado!")
            .desc(f"```\nDado de {self.faces} faces\n```\nResultado: **{result}**")
            .thumb(interaction.user.display_avatar.url)
            .footer(f"Jogado por {interaction.user.display_name}")
            .build()
        )
        await interaction.response.send_message(embed=embed, view=DadoView(self.faces))


class DadoView(discord.ui.View):
    def __init__(self, faces: int) -> None:
        super().__init__(timeout=30)
        self.add_item(DadoReplayButton(faces))


# =========================
# VIEW: Adivinha Novamente
# =========================

class AdivinhaReplayButton(discord.ui.Button["AdivinhaView"]):
    def __init__(self) -> None:
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="Tentar Novamente",
            emoji="\U0001f3b1",
            custom_id="adivinha_replay",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        answer = random.randint(1, 10)
        embed = (
            make_embed("purple")
            .title("Novo Jogo!")
            .desc("Adivinhe um número de **1 a 10**!\nUse `/adivinha <número>` para jogar.")
            .timestamp()
            .footer("O número foi sorteado! Use /adivinha")
            .build()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


class AdivinhaView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=30)
        self.add_item(AdivinhaReplayButton())


# =========================
# VIEW: Eightball Novamente
# =========================

class EightballReplayButton(discord.ui.Button["EightballView"]):
    def __init__(self) -> None:
        super().__init__(
            style=discord.ButtonStyle.primary,
            label="Perguntar Novamente",
            emoji="\U0001f3b1",
            custom_id="eightball_replay",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        answers = [
            ("\u2705 Sim.", 0x22C55E),
            ("\u274c N\u00e3o.", 0xEF4444),
            ("\U0001f914 Talvez.", 0xF59E0B),
            ("\U0001f525 Com certeza!", 0x8B5CF6),
            ("\U0001f6ab N\u00e3o conte com isso.", 0xEF4444),
            ("\U0001f4ca Provavelmente.", 0x8B5CF6),
            ("\u23f0 Pergunte de novo mais tarde.", 0x8B5CF6),
            ("\U0001f48e Sem d\u00favida.", 0xD946EF),
        ]
        answer_text, answer_color = random.choice(answers)

        embed = (
            make_embed(answer_color)
            .title("Bola 8 M\u00e1gica")
            .desc(f"**Resposta:** _{answer_text}_\n\n_Pergunte novamente com /8ball_")
            .thumb(interaction.client.user.display_avatar.url)
            .timestamp()
            .footer("Klaus 8Ball")
            .build()
        )
        await interaction.response.send_message(embed=embed, view=EightballView())


class EightballView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=30)
        self.add_item(EightballReplayButton())


# =========================
# VIEW: Piada Outra
# =========================

class PiadaNextButton(discord.ui.Button["PiadaView"]):
    def __init__(self) -> None:
        super().__init__(
            style=discord.ButtonStyle.success,
            label="Outra Piada",
            emoji="\U0001f399\ufe0f",
            custom_id="piada_next",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        piadas = [
            ("Por que o programador usa óculos?", "Porque ele não consegue C#!"),
            ("O que o JavaScript disse para o CSS?", "Você não me entende!"),
            ("Por que o foguete não usa WiFi?", "Porque ele prefere ir ao espaço!"),
            ("O que um bit disse ao outro?", "Você está mutado!"),
            ("Por que o relógio foi preso?", "Porque ele deu meia-noite!"),
            ("Qual a comida favorita do fantasma?", "Bolo de fantasminha!"),
            ("Por que o livro de matemática ficou triste?", "Porque ele tinha muitos problemas!"),
            ("O que o zero disse para o oito?", "Bonito cinto!"),
            ("Por que a calculadora foi ao bar?", "Para fazer contas!"),
            ("Qual o animal mais antigo?", "A zebra, porque ela é em preto e branco!"),
        ]
        pergunta, resposta = random.choice(piadas)

        embed = (
            make_embed("purple")
            .title("Piada do Klaus")
            .desc(f"**P:** {pergunta}\n\n**R:** {resposta}")
            .footer("Klaus Comedy Club")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed, view=PiadaView())


class PiadaView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=30)
        self.add_item(PiadaNextButton())


# =========================
# VIEW: Meme Outro
# =========================

class MemeNextButton(discord.ui.Button["MemeView"]):
    def __init__(self) -> None:
        super().__init__(
            style=discord.ButtonStyle.success,
            label="Outro Meme",
            emoji="\U0001f4ac",
            custom_id="meme_next",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        memes = [
            "https://i.imgflip.com/anm8fd.jpg",
            "https://i.imgflip.com/aohzhe.jpg",
            "https://i.imgflip.com/3yhgyo.jpg",
            "https://i.imgflip.com/9lu40v.jpg",
            "https://i.imgflip.com/aqld2c.jpg",
        ]
        embed = (
            make_embed("purple")
            .title("Meme Aleatório")
            .image(random.choice(memes))
            .footer("Klaus Memes")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed, view=MemeView())


class MemeView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=30)
        self.add_item(MemeNextButton())


# =========================
# VIEW: Casal Recalcular
# =========================

class CasalRecalcButton(discord.ui.Button["CasalView"]):
    def __init__(self, user1_id: int, user2_id: int) -> None:
        super().__init__(
            style=discord.ButtonStyle.secondary,
            label="Recalcular",
            emoji="\U0001f504",
            custom_id="casal_recalc",
        )
        self.user1_id = user1_id
        self.user2_id = user2_id

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        if interaction.guild:
            g1 = interaction.guild.get_member(self.user1_id)
            g2 = interaction.guild.get_member(self.user2_id)
        else:
            g1, g2 = None, None
        if not g1 or not g2:
            await interaction.response.send_message(
                embed=make_embed.error("Membros não encontrados", "Um ou ambos os membros não estão no servidor."),
                ephemeral=True,
            )
            return

        embed = _build_casal_embed(g1, g2)
        await interaction.response.send_message(embed=embed, view=CasalView(self.user1_id, self.user2_id))


class CasalView(discord.ui.View):
    def __init__(self, user1_id: int, user2_id: int) -> None:
        super().__init__(timeout=60)
        self.add_item(CasalRecalcButton(user1_id, user2_id))


def _build_casal_embed(user1: discord.Member, user2: discord.Member) -> discord.Embed:
    name1 = user1.display_name.lower()
    name2 = user2.display_name.lower()

    ship_name = (name1[:3] + name2[:3]).title()

    len_factor = min(len(name1) + len(name2), 30) / 30
    id_factor = ((user1.id + user2.id) % 100) / 100
    random_factor = random.random()

    compat = int(len_factor * 30 + id_factor * 30 + random_factor * 40)
    compat = max(5, min(100, compat))

    if compat >= 80:
        color = 0xF59E0B
        destiny = "Vocês foram escritos nas estrelas! Um casal destiny!"
        destiny_emoji = "\U0001f31f"
    elif compat >= 60:
        color = 0xD946EF
        destiny = "Muita química! O universo conspira a favor de vocês!"
        destiny_emoji = "\U0001f496"
    elif compat >= 40:
        color = 0xEC4899
        destiny = "Tem potencial! Um pouco de esforço e vira algo lindo."
        destiny_emoji = "\U0001f525"
    elif compat >= 20:
        color = 0xF97316
        destiny = "Hmm... talvez como amigos? Deixa rolar!"
        destiny_emoji = "\U0001f914"
    else:
        color = 0xEF4444
        destiny = "Melhor manter distância... ou não?!"
        destiny_emoji = "\U0001f494"

    filled = compat // 5
    bar = "\u2588" * filled + "\u25a1" * (20 - filled)

    embed = (
        make_embed(color)
        .title(f"\U0001f496 Klaus Casal Calculator")
        .desc(
            f"**{ship_name}**\n\n"
            f"**{user1.display_name}** \U00002764 \U00002764 \U00002764 **{user2.display_name}**\n\n"
            f"```\n{bar}\n```\n"
            f"**{compat}%** compatibilidade!\n\n"
            f"**Fatores:**\n"
            f"\u2022 Nomes: `{int(len_factor * 30)}/30`\n"
            f"\u2022 IDs: `{int(id_factor * 30)}/30`\n"
            f"\u2022 Destino: `{int(random_factor * 40)}/40`\n\n"
            f"{destiny_emoji} _{destiny}_"
        )
        .thumb(user1.display_avatar.url)
        .image(user2.display_avatar.url)
        .footer("Klaus Casal Calculator")
        .timestamp()
        .build()
    )
    return embed


# =========================
# VIEW: Aventura Continuar
# =========================

ADVENTURES = [
    {
        "title": "\U0001f3f0 Castelo Assombrado",
        "scene": (
            "Você entra em um castelo abandonado. Velas flutuam sozinhas e susurros ecoam pelos "
            "corredores. Um baú brilhante está no centro do salão."
        ),
        "choices": [
            {"label": "Abrir o baú", "emoji": "\U0001f4e6", "outcome": "O baú contém **50 koins** e uma poção!", "koins": 50},
            {"label": "Explorar os corredores", "emoji": "\U0001f56f\ufe0f", "outcome": "Você encontra um mapa antigo e **30 koins**!", "koins": 30},
            {"label": "Sair correndo", "emoji": "\U0001f3c3", "outcome": "Saiu ileso, mas com as mãos vazias.", "koins": 0},
        ],
    },
    {
        "title": "\U0001f30a Oceano Profundo",
        "scene": (
            "Você mergulha em águas cristalinas e encontra um navio afundado. Uma pirata fantasma "
            "aparece e oferece um jogo de adivinhação."
        ),
        "choices": [
            {"label": "Jogar o jogo", "emoji": "\U0001f3b2", "outcome": "Acertou! A pirata te dá **100 koins**!", "koins": 100},
            {"label": "Negociar", "emoji": "\U0001f91d", "outcome": "Ela aceita trocar um tesouro por **60 koins**.", "koins": 60},
            {"label": "Mergulhar mais fundo", "emoji": "\U0001f30a", "outcome": "Encontrou uma pérola gigante! **80 koins**!", "koins": 80},
        ],
    },
    {
        "title": "\U0001f525 Monte Vulcânico",
        "scene": (
            "Lava borbulha ao seu redor. No topo da montanha, um dragão dorme sobre uma pilha de "
            "tesouros brilhantes."
        ),
        "choices": [
            {"label": "Roubar o tesouro", "emoji": "\U0001f4b0", "outcome": "O dragão acorda! Você foge com **70 koins**!", "koins": 70},
            {"label": "Acordar o dragão", "emoji": "\U0001f409", "outcome": "O dragão te dá asas voadoras e **90 koins**!", "koins": 90},
            {"label": "Descer a montanha", "emoji": "\u2b07\ufe0f", "outcome": "Escorregou na lava! Perdeu **20 koins**.", "koins": -20},
        ],
    },
    {
        "title": "\U0001f319 Floresta Sombria",
        "scene": (
            "Uma floresta escura se estende à sua frente. Fadas minúsculas dançam ao redor de "
            "um círculo de cogumelos luminosos."
        ),
        "choices": [
            {"label": "Dançar com as fadas", "emoji": "\U0001f483", "outcome": "Elas encantam você com **40 koins** e um chapéu mágico!", "koins": 40},
            {"label": "Seguir o trilha dos cogumelos", "emoji": "\U0001f344", "outcome": "Encontra um poço de desejos com **55 koins**!", "koins": 55},
            {"label": "Acender uma tocha", "emoji": "\U0001f525", "outcome": "As fadas fogem, mas você encontra **25 koins** no chão.", "koins": 25},
        ],
    },
    {
        "title": "\u2b50 Estação Espacial",
        "scene": (
            "Você flutua em gravidade zero numa estação espacial abandonada. Painéis piscam e um "
            "robô com defeito oferece missões."
        ),
        "choices": [
            {"label": "Aceitar a missão", "emoji": "\U0001f680", "outcome": "Missão completa! **120 koins** de recompensa!", "koins": 120},
            {"label": "Consertar o robô", "emoji": "\U0001f916", "outcome": "Robô amigo! Ele te dá **45 koins** e um upgrade.", "koins": 45},
            {"label": "Explorar o espaço", "emoji": "\U0001f30c", "outcome": "Coletou meteoritos valiosos! **65 koins**!", "koins": 65},
        ],
    },
    {
        "title": "\U0001f3a8 Galeria de Arte Mágica",
        "scene": (
            "Quadros ganham vida quando você passa! Uma pintora te desafia a completar uma obra "
            "para ganhar o prêmio da galeria."
        ),
        "choices": [
            {"label": "Pintar um retrato", "emoji": "\U0001f3a8", "outcome": "A obra-prima rende **75 koins**!", "koins": 75},
            {"label": "Adivinhar o mistério", "emoji": "\U0001f50d", "outcome": "Acertou! **50 koins** e um quadro raro!", "koins": 50},
            {"label": "Sair pela porta dos fundos", "emoji": "\U0001f6aa", "outcome": "Caíu numa armadilha! Perdeu **10 koins**.", "koins": -10},
        ],
    },
]

AVENTURA_USER_DATA: dict[int, dict[str, object]] = {}


class AventuraChoiceButton(discord.ui.Button["AventuraView"]):
    def __init__(self, idx: int, choice: dict) -> None:
        super().__init__(
            style=discord.ButtonStyle.primary,
            label=choice["label"],
            emoji=choice["emoji"],
            custom_id=f"aventura_choice_{idx}",
        )
        self.idx = idx
        self.choice = choice

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        adventure = self.view.adventure
        uid = interaction.user.id

        current_koins = AVENTURA_USER_DATA.get(uid, {}).get("koins", 0)
        new_koins = current_koins + self.choice["koins"]
        if uid not in AVENTURA_USER_DATA:
            AVENTURA_USER_DATA[uid] = {}
        AVENTURA_USER_DATA[uid]["koins"] = new_koins

        koins_text = f"+{self.choice['koins']}" if self.choice["koins"] >= 0 else str(self.choice["koins"])
        color = 0x22C55E if self.choice["koins"] > 0 else 0xEF4444 if self.choice["koins"] < 0 else 0x8B5CF6

        embed = (
            make_embed(color)
            .title(f"{adventure['title']} - Resultado")
            .desc(
                f"**Escolha:** {self.choice['emoji']} {self.choice['label']}\n\n"
                f"_{self.choice['outcome']}_\n\n"
                f"\U0001fa99 **Koins totais:** {new_koins}"
            )
            .footer("Klaus Aventura")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)


class AventuraView(discord.ui.View):
    def __init__(self, adventure: dict) -> None:
        super().__init__(timeout=60)
        self.adventure = adventure
        for i, choice in enumerate(adventure["choices"]):
            self.add_item(AventuraChoiceButton(i, choice))


# =========================
# VIEW: Quiz
# =========================

QUIZ_QUESTIONS = [
    {
        "q": "Qual é a capital do Brasil?",
        "options": ["São Paulo", "Brasília", "Rio de Janeiro", "Salvador"],
        "correct": 1,
    },
    {
        "q": "Qual é o maior planeta do sistema solar?",
        "options": ["Saturno", "Júpiter", "Netuno", "Urano"],
        "correct": 1,
    },
    {
        "q": "Quem pintou a Mona Lisa?",
        "options": ["Michelangelo", "Rafael", "Leonardo da Vinci", "Donatello"],
        "correct": 2,
    },
    {
        "q": "Qual linguagem é usada para estilos web?",
        "options": ["HTML", "JavaScript", "CSS", "Python"],
        "correct": 2,
    },
    {
        "q": "Qual é o elemento químico da água?",
        "options": ["Hidrogênio", "Oxigênio", "CO2", "H2O"],
        "correct": 3,
    },
    {
        "q": "Em que ano o homem pisou na Lua?",
        "options": ["1965", "1969", "1972", "1960"],
        "correct": 1,
    },
    {
        "q": "Qual é o animal terrestre mais rápido?",
        "options": ["Leão", "Guepardo", "Tigre", "Cavalo"],
        "correct": 1,
    },
    {
        "q": "Qual é o maior oceano do mundo?",
        "options": ["Atlântico", "Índico", "Pacífico", "Ártico"],
        "correct": 2,
    },
    {
        "q": "Quantos bits tem um byte?",
        "options": ["4", "8", "16", "32"],
        "correct": 1,
    },
    {
        "q": "Qual é a fórmula química do ouro?",
        "options": ["Ag", "Fe", "Au", "Cu"],
        "correct": 2,
    },
    {
        "q": "Quem criou o Python?",
        "options": ["James Gosling", "Guido van Rossum", "Brendan Eich", "Dennis Ritchie"],
        "correct": 1,
    },
    {
        "q": "Qual é o menor país do mundo?",
        "options": ["Mônaco", "Vaticano", "San Marino", "Liechtenstein"],
        "correct": 1,
    },
]

QUIZ_SCORES: dict[int, int] = {}
QUIZ_ACTIVE: dict[int, bool] = {}


class QuizOptionButton(discord.ui.Button["QuizView"]):
    def __init__(self, idx: int, label: str) -> None:
        letter = ["A", "B", "C", "D"][idx]
        super().__init__(
            style=discord.ButtonStyle.secondary,
            label=f"{letter}) {label}",
            custom_id=f"quiz_option_{idx}",
        )
        self.idx = idx

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        q = self.view.question
        uid = interaction.user.id

        if uid in QUIZ_ACTIVE and QUIZ_ACTIVE[uid]:
            QUIZ_ACTIVE[uid] = False
        else:
            await interaction.response.send_message(
                embed=make_embed.error("Tempo Esgotado!", "Essa rodada já acabou."),
                ephemeral=True,
            )
            return

        correct = self.idx == q["correct"]
        if uid not in QUIZ_SCORES:
            QUIZ_SCORES[uid] = 0
        if correct:
            QUIZ_SCORES[uid] += 1

        letter = ["A", "B", "C", "D"][q["correct"]]
        color = 0x22C55E if correct else 0xEF4444
        result_text = "\u2705 **Correto!**" if correct else f"\u274c **Errou!** A resposta era **{letter}) {q['options'][q['correct']]}**."

        embed = (
            make_embed(color)
            .title("Quiz Klaus")
            .desc(
                f"**{q['q']}**\n\n"
                f"{result_text}\n\n"
                f"\U0001f3af **Sua pontuação:** {QUIZ_SCORES[uid]}"
            )
            .footer("Klaus Quiz")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)


class QuizView(discord.ui.View):
    def __init__(self, question: dict) -> None:
        super().__init__(timeout=15)
        self.question = question
        for i, opt in enumerate(question["options"]):
            self.add_item(QuizOptionButton(i, opt))


# =========================
# VIEW: Poll Vote
# =========================

class PollVoteSelect(discord.ui.Select["PollView"]):
    def __init__(self, options: list[str], votes: dict[int, set[int]]) -> None:
        select_options = [
            discord.SelectOption(label=opt, value=str(i), emoji=["1\ufe0f\u20e3", "2\ufe0f\u20e3", "3\ufe0f\u20e3", "4\ufe0f\u20e3"][i])
            for i, opt in enumerate(options)
        ]
        super().__init__(placeholder="Vote no sua opção...", options=select_options)
        self._votes = votes

    async def callback(self, interaction: discord.Interaction) -> None:
        uid = interaction.user.id
        choice = int(self.values[0])

        for voters in self._votes.values():
            voters.discard(uid)
        self._votes[choice].add(uid)

        total = sum(len(v) for v in self._votes.values())
        lines = []
        for i, voters in self._votes.items():
            count = len(voters)
            pct = (count / total * 100) if total else 0
            bar_len = int(pct // 10)
            bar = "\u2588" * bar_len + "\u2591" * (10 - bar_len)
            lines.append(f"**{self.options[i].label}** — {count} voto(s) (`{bar}` {pct:.0f}%)")

        view: PollView = self.view  # type: ignore
        embed = (
            make_embed("purple")
            .title(f"\U0001f4ca {view.question}")
            .desc("\n".join(lines) + f"\n\n\U0001f465 **Total:** {total} voto(s)")
            .footer(f"Enquete por {view.author_name}")
            .timestamp()
            .build()
        )
        await interaction.response.edit_message(embed=embed, view=self.view)


class PollView(discord.ui.View):
    def __init__(self, question: str, options: list[str], author_name: str) -> None:
        super().__init__(timeout=120)
        self.question = question
        self.author_name = author_name
        self._votes: dict[int, set[int]] = {i: set() for i in range(len(options))}
        self.add_item(PollVoteSelect(options, self._votes))


# =========================
# VIEW: Ship Rever
# =========================

class ShipReverButton(discord.ui.Button["ShipView"]):
    def __init__(self, user1_id: int, user2_id: int) -> None:
        super().__init__(
            style=discord.ButtonStyle.secondary,
            label="Rever Ship",
            emoji="\U0001f504",
            custom_id="ship_rever",
        )
        self.user1_id = user1_id
        self.user2_id = user2_id

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        if interaction.guild:
            u1 = interaction.guild.get_member(self.user1_id)
            u2 = interaction.guild.get_member(self.user2_id)
        else:
            u1 = u2 = None
        if not u1 or not u2:
            await interaction.response.send_message(
                embed=make_embed.error("Membros não encontrados", "Um ou ambos os membros não estão no servidor."),
                ephemeral=True,
            )
            return

        embed = _build_ship_embed(u1, u2)
        await interaction.response.send_message(embed=embed, view=ShipView(self.user1_id, self.user2_id))


class ShipView(discord.ui.View):
    def __init__(self, user1_id: int, user2_id: int) -> None:
        super().__init__(timeout=60)
        self.add_item(ShipReverButton(user1_id, user2_id))


def _build_ship_embed(user1: discord.Member, user2: discord.Member) -> discord.Embed:
    name1 = user1.display_name.lower()
    name2 = user2.display_name.lower()
    ship_name = (name1[:3] + name2[:3]).title()

    compat = random.randint(1, 100)

    name_factor = min(len(name1) + len(name2), 30) / 30
    id_factor = ((user1.id + user2.id) % 100) / 100
    random_factor = random.random()
    weighted = int(name_factor * 25 + id_factor * 25 + random_factor * 50)
    compat = max(1, min(100, weighted))

    if compat == 100:
        msg = "\U0001f31f **MATCH PERFEITO!** Vocês são almas gêmeas!"
        cor = 0xF59E0B
    elif compat >= 80:
        msg = "\U0001f496 Conexão muito forte! O destino sussurra seu nome!"
        cor = 0xD946EF
    elif compat >= 60:
        msg = "\U0001f525 Muita química! O universo está torcendo por vocês!"
        cor = 0xEC4899
    elif compat >= 40:
        msg = "\U0001f914 Pode rolar algo... deixe a mágica acontecer!"
        cor = 0x8B5CF6
    elif compat >= 20:
        msg = "\U0001f615 Quem sabe? Às vezes o improvável vira lindo!"
        cor = 0x6366F1
    else:
        msg = "\U0001f494 Melhor ser amigos... mas nunca diga nunca!"
        cor = 0x6B7280

    filled = compat // 5
    bar = "\u2588" * filled + "\u25a1" * (20 - filled)

    embed = (
        make_embed(cor)
        .title("\U0001f496 Klaus Ship Calculator")
        .desc(
            f"**{ship_name}**\n\n"
            f"**{user1.display_name}** \U00002764 \U00002764 \U00002764 **{user2.display_name}**\n\n"
            f"```\n{bar}\n```\n"
            f"**{compat}%** compatibilidade!\n\n"
            f"**Fatores:**\n"
            f"\u2022 Nomes: `{int(name_factor * 25)}/25`\n"
            f"\u2022 IDs: `{int(id_factor * 25)}/25`\n"
            f"\u2022 Destino: `{int(random_factor * 50)}/50`\n\n"
            f"_Destino:_ {msg}"
        )
        .thumb(user1.display_avatar.url)
        .image(user2.display_avatar.url)
        .footer("Klaus Ship Calculator")
        .timestamp()
        .build()
    )
    return embed


# =========================
# COG
# =========================

class Diversao(commands.Cog):
    def __init__(self, bot: KlausBot) -> None:
        self.bot = bot

    # =========================
    # /HUG
    # =========================

    @app_commands.command(name="hug", description="Abraces alguém com um GIF fofo.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(member="A pessoa que você quer abraçar")
    async def hug(self, interaction: discord.Interaction, member: discord.Member) -> None:
        if member == interaction.user:
            await interaction.response.send_message(
                embed=make_embed.error("Alvo Inválido", "Você não pode usar este comando em si mesmo!"),
                ephemeral=True,
            )
            return
        if interaction.guild:
            _track_social(interaction.guild.id, "hug")
        embed = (
            make_embed("purple")
            .title("Abraço!")
            .desc(f"{interaction.user.mention} abraçou {member.mention} com carinho!")
            .image(random.choice(HUG_GIFS))
            .timestamp()
            .footer("Klaus Social")
            .build()
        )
        view = SocialView(interaction.user.id, member.id, "hug")
        await interaction.response.send_message(embed=embed, view=view)

    # =========================
    # /KISS
    # =========================

    @app_commands.command(name="kiss", description="Mande um beijo com um GIF romântico.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(member="A pessoa que você quer beijar")
    async def kiss(self, interaction: discord.Interaction, member: discord.Member) -> None:
        if member == interaction.user:
            await interaction.response.send_message(
                embed=make_embed.error("Alvo Inválido", "Você não pode usar este comando em si mesmo!"),
                ephemeral=True,
            )
            return
        if interaction.guild:
            _track_social(interaction.guild.id, "kiss")
        embed = (
            make_embed("pink")
            .title("Beijo!")
            .desc(f"{interaction.user.mention} mandou um beijo para {member.mention}!")
            .image(random.choice(KISS_GIFS))
            .timestamp()
            .footer("Klaus Social")
            .build()
        )
        view = SocialView(interaction.user.id, member.id, "kiss")
        await interaction.response.send_message(embed=embed, view=view)

    # =========================
    # /SLAP
    # =========================

    @app_commands.command(name="slap", description="Dê um tapa divertido com GIFs engraçados.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(member="A pessoa que você quer dar um tapa")
    async def slap(self, interaction: discord.Interaction, member: discord.Member) -> None:
        if member == interaction.user:
            await interaction.response.send_message(
                embed=make_embed.error("Alvo Inválido", "Você não pode usar este comando em si mesmo!"),
                ephemeral=True,
            )
            return
        if interaction.guild:
            _track_social(interaction.guild.id, "slap")
        embed = (
            make_embed("orange")
            .title("Tapa!")
            .desc(f"{interaction.user.mention} deu um tapa em {member.mention}!")
            .image(random.choice(SLAP_GIFS))
            .timestamp()
            .footer("Klaus Social")
            .build()
        )
        view = SocialView(interaction.user.id, member.id, "slap")
        await interaction.response.send_message(embed=embed, view=view)

    # =========================
    # /PAT
    # =========================

    @app_commands.command(name="pat", description="Faça carinho em alguém.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(member="A pessoa que você quer acariciar")
    async def pat(self, interaction: discord.Interaction, member: discord.Member) -> None:
        if member == interaction.user:
            await interaction.response.send_message(
                embed=make_embed.error("Alvo Inválido", "Você não pode usar este comando em si mesmo!"),
                ephemeral=True,
            )
            return
        if interaction.guild:
            _track_social(interaction.guild.id, "pat")
        embed = (
            make_embed("pink")
            .title("Carinho!")
            .desc(f"{interaction.user.mention} fez carinho em {member.mention}!")
            .image(random.choice(PAT_GIFS))
            .timestamp()
            .footer("Klaus Social")
            .build()
        )
        view = SocialView(interaction.user.id, member.id, "pat")
        await interaction.response.send_message(embed=embed, view=view)

    # =========================
    # /SHIP (enhanced)
    # =========================

    @app_commands.command(name="ship", description="Calcule a compatibilidade entre duas pessoas.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(user1="Primeira pessoa", user2="Segunda pessoa")
    async def ship(self, interaction: discord.Interaction, user1: discord.Member, user2: discord.Member) -> None:
        embed = _build_ship_embed(user1, user2)
        await interaction.response.send_message(embed=embed, view=ShipView(user1.id, user2.id))

    # =========================
    # /CASAL
    # =========================

    @app_commands.command(name="casal", description="Klaus Casal Calculator - Calcule a compatibilidade amorosa!")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(member1="Primeira pessoa", member2="Segunda pessoa")
    async def casal(self, interaction: discord.Interaction, member1: discord.Member, member2: discord.Member) -> None:
        embed = _build_casal_embed(member1, member2)
        await interaction.response.send_message(embed=embed, view=CasalView(member1.id, member2.id))

    # =========================
    # /COIN
    # =========================

    @app_commands.command(name="coin", description="Jogue uma moeda e veja o resultado.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def coin(self, interaction: discord.Interaction) -> None:
        result = random.choice(["Cara", "Coroa"])
        cor = 0xF59E0B if result == "Cara" else 0x8B5CF6

        embed = (
            make_embed(cor)
            .title("Moeda!")
            .desc(f"Resultado: **{result}**")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .footer("Klaus Coin")
            .build()
        )
        await interaction.response.send_message(embed=embed, view=CoinView())

    # =========================
    # /RPS
    # =========================

    @app_commands.command(name="rps", description="Jogue pedra, papel ou tesoura com o bot.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(choice="Sua escolha: pedra, papel ou tesoura")
    async def rps(self, interaction: discord.Interaction, choice: str) -> None:
        option = choice.lower()
        valid = ["pedra", "papel", "tesoura"]
        if option not in valid:
            await interaction.response.send_message(
                embed=make_embed.error("Inválido", "Use `pedra`, `papel` ou `tesoura`."),
                ephemeral=True,
            )
            return

        bot_choice = random.choice(valid)
        emojis = {"pedra": "\u270a", "papel": "\u270b", "tesoura": "\u270c\ufe0f"}

        if option == bot_choice:
            result, color = "Empate!", 0xF59E0B
        elif (option == "pedra" and bot_choice == "tesoura") or (option == "papel" and bot_choice == "pedra") or (option == "tesoura" and bot_choice == "papel"):
            result, color = "Você ganhou!", 0x22C55E
        else:
            result, color = "O bot ganhou!", 0xEF4444

        embed = (
            make_embed(color)
            .title("Jokenp\u00f4")
            .desc(f"```\n  VOCÊ  vs  KLAUS\n```\nVocê: {emojis[option]} **{option.title()}**\nBot: {emojis[bot_choice]} **{bot_choice.title()}**\n\n**{result}**")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .footer("Klaus RPS")
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /BATALHA (enhanced)
    # =========================

    @app_commands.command(name="batalha", description="Desafie alguém para uma batalha de dados!")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.user.id)
    @app_commands.describe(member="Seu oponente")
    async def batalha(self, interaction: discord.Interaction, member: discord.Member) -> None:
        if member.bot or member.id == interaction.user.id:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Escolha um oponente válido!"),
                ephemeral=True,
            )
            return

        await interaction.response.defer()

        p1_hp, p2_hp = 100, 100
        p1_name = interaction.user.display_name
        p2_name = member.display_name
        p1_xp, p2_xp = 0, 0

        for turn in range(3):
            await asyncio.sleep(1.2)

            r1 = random.randint(1, 20)
            r2 = random.randint(1, 20)

            crit1 = ""
            crit2 = ""
            if r1 == 20:
                crit1 = " \U0001f31f **CRÍTICO!**"
                r1 += 10
            elif r1 == 1:
                crit1 = " \U0001f4a5 **FALHA!**"
                r1 = 0
            if r2 == 20:
                crit2 = " \U0001f31f **CRÍTICO!**"
                r2 += 10
            elif r2 == 1:
                crit2 = " \U0001f4a5 **FALHA!**"
                r2 = 0

            p1_hp -= r2
            p2_hp -= r1
            p1_hp = max(0, p1_hp)
            p2_hp = max(0, p2_hp)

            d1_emoji = DICE_FACES[min(r1 % 6, 5)]
            d2_emoji = DICE_FACES[min(r2 % 6, 5)]

            bar1 = "\u2588" * (p1_hp // 5) + "\u2591" * (20 - p1_hp // 5)
            bar2 = "\u2588" * (p2_hp // 5) + "\u2591" * (20 - p2_hp // 5)

            embed = (
                make_embed("purple")
                .title(f"Batalha de Dados! - Turno {turn + 1}/3")
                .desc(
                    f"```\n  {p1_name}  vs  {p2_name}\n```\n"
                    f"**{p1_name}**\n{d1_emoji} **{r1}**{crit1}\n`{bar1}` **{p1_hp}** HP\n\n"
                    f"**{p2_name}**\n{d2_emoji} **{r2}**{crit2}\n`{bar2}` **{p2_hp}** HP"
                )
                .footer("Klaus Battle Arena")
                .build()
            )
            await interaction.edit_original_response(embed=embed)

        if p1_hp > p2_hp:
            winner, w_name = interaction.user, p1_name
            p1_xp = 50
        elif p2_hp > p1_hp:
            winner, w_name = member, p2_name
            p2_xp = 50
        else:
            winner = None
            p1_xp = p2_xp = 25

        final_bar1 = "\u2588" * (p1_hp // 5) + "\u2591" * (20 - p1_hp // 5)
        final_bar2 = "\u2588" * (p2_hp // 5) + "\u2591" * (20 - p2_hp // 5)

        if winner:
            result_text = f"\U0001f3c6 **{w_name}** venceu a batalha! (+{50} XP)"
        else:
            result_text = f"\U0001f91d **Empate!** Ambos ganham **25 XP**!"

        embed = (
            make_embed("purple")
            .title("Batalha de Dados! - Resultado Final")
            .desc(
                f"```\n  {p1_name}  vs  {p2_name}\n```\n"
                f"**{p1_name}**\n`{final_bar1}` **{p1_hp}** HP  |  +{p1_xp} XP\n\n"
                f"**{p2_name}**\n`{final_bar2}` **{p2_hp}** HP  |  +{p2_xp} XP\n\n{result_text}"
            )
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Battle Arena")
            .build()
        )
        view = BatalhaView(interaction.user.id, member.id)
        await interaction.edit_original_response(embed=embed, view=view)

    # =========================
    # /PIADA
    # =========================

    @app_commands.command(name="piada", description="Conte uma piada aleatória.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def piada(self, interaction: discord.Interaction) -> None:
        piadas = [
            ("Por que o programador usa óculos?", "Porque ele não consegue C#!"),
            ("O que o JavaScript disse para o CSS?", "Você não me entende!"),
            ("Por que o foguete não usa WiFi?", "Porque ele prefere ir ao espaço!"),
            ("O que um bit disse ao outro?", "Você está mutado!"),
            ("Por que o relógio foi preso?", "Porque ele deu meia-noite!"),
            ("Qual a comida favorita do fantasma?", "Bolo de fantasminha!"),
            ("Por que o livro de matemática ficou triste?", "Porque ele tinha muitos problemas!"),
            ("O que o zero disse para o oito?", "Bonito cinto!"),
            ("Por que a calculadora foi ao bar?", "Para fazer contas!"),
            ("Qual o animal mais antigo?", "A zebra, porque ela é em preto e branco!"),
        ]

        pergunta, resposta = random.choice(piadas)

        embed = (
            make_embed("purple")
            .title("Piada do Klaus")
            .desc(f"**P:** {pergunta}\n\n**R:** {resposta}")
            .footer("Klaus Comedy Club")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed, view=PiadaView())

    # =========================
    # /MEME
    # =========================

    @app_commands.command(name="meme", description="Mande um meme aleatório para o chat.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def meme(self, interaction: discord.Interaction) -> None:
        memes = [
            "https://i.imgflip.com/anm8fd.jpg",
            "https://i.imgflip.com/aohzhe.jpg",
            "https://i.imgflip.com/3yhgyo.jpg",
            "https://i.imgflip.com/9lu40v.jpg",
            "https://i.imgflip.com/aqld2c.jpg",
        ]
        embed = (
            make_embed("purple")
            .title("Meme Aleatório")
            .image(random.choice(memes))
            .footer("Klaus Memes")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed, view=MemeView())

    # =========================
    # /8BALL (alias)
    # =========================

    @app_commands.command(name="8ball", description="Faça uma pergunta e receba uma resposta divertida.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(question="Pergunta que você quer fazer")
    async def eightball_alias(self, interaction: discord.Interaction, question: str) -> None:
        answers = [
            ("\u2705 Sim.", 0x22C55E),
            ("\u274c Não.", 0xEF4444),
            ("\U0001f914 Talvez.", 0xF59E0B),
            ("\U0001f525 Com certeza!", 0x8B5CF6),
            ("\U0001f6ab Não conte com isso.", 0xEF4444),
            ("\U0001f4ca Provavelmente.", 0x8B5CF6),
            ("\u23f0 Pergunte de novo mais tarde.", 0x8B5CF6),
            ("\U0001f48e Sem dúvida.", 0xD946EF),
        ]
        answer_text, answer_color = random.choice(answers)
        embed = (
            make_embed(answer_color)
            .title("Bola 8 M\u00e1gica")
            .desc(f"**Pergunta:** _{question}_\n\n**Resposta:** _{answer_text}_")
            .thumb(interaction.client.user.display_avatar.url)
            .timestamp()
            .footer("Klaus 8Ball")
            .build()
        )
        await interaction.response.send_message(embed=embed, view=EightballView())

    # =========================
    # /ROLL (D20 advantage/disadvantage)
    # =========================

    @app_commands.command(name="roll", description="Role um D20 com vantagem ou desvantagem!")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(advantage="True = vantagem (2 dados, maior), False = normal")
    async def roll(self, interaction: discord.Interaction, advantage: bool = False) -> None:
        if advantage:
            r1 = random.randint(1, 20)
            r2 = random.randint(1, 20)
            final = max(r1, r2)
            emoji = "\U0001f525"
            mode = "Vantagem"
            detail = f"Primeiro: **{r1}** | Segundo: **{r2}**"
        else:
            r1 = random.randint(1, 20)
            r2 = random.randint(1, 20)
            final = min(r1, r2)
            emoji = "\U0001f4a7"
            mode = "Desvantagem"
            detail = f"Primeiro: **{r1}** | Segundo: **{r2}**"

        if final == 20:
            result_text = "\U0001f31f **CRÍTICO!**"
            cor = 0xF59E0B
        elif final == 1:
            result_text = "\U0001f4a5 **FALHO CRÍTICO!**"
            cor = 0xEF4444
        else:
            result_text = f"Resultado: **{final}**"
            cor = 0x8B5CF6

        embed = (
            make_embed(cor)
            .title(f"{emoji} D20 - {mode}")
            .desc(f"{detail}\n\n**{result_text}**")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .footer(f"Jogado por {interaction.user.display_name}")
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /RANKING_SOCIAL
    # =========================

    @app_commands.command(name="ranking_social", description="Ranking social do servidor - quem recebeu mais carinho?")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def ranking_social(self, interaction: discord.Interaction) -> None:
        guild_id = interaction.guild.id if interaction.guild else 0
        stats = SOCIAL_STATS.get(guild_id, {})

        if not stats:
            stats = {
                "hug": random.randint(10, 200),
                "kiss": random.randint(5, 150),
                "slap": random.randint(3, 100),
                "pat": random.randint(8, 180),
            }

        medals = ["\U0001f947", "\U0001f948", "\U0001f949"]
        total = sum(stats.values())
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)

        lines = []
        emojis = {"hug": "\U0001f917", "kiss": "\U0001f48b", "slap": "\U0001f44b", "pat": "\U0001f970"}
        names = {"hug": "Abraços", "kiss": "Beijos", "slap": "Tapas", "pat": "Carinhos"}

        for i, (action, count) in enumerate(sorted_stats):
            medal = medals[i] if i < 3 else f"`#{i + 1}`"
            emoji = emojis.get(action, "\u2753")
            name = names.get(action, action.title())
            pct = (count / total * 100) if total else 0
            bar_len = int(pct // 10)
            bar = "\u2588" * bar_len + "\u2591" * (10 - bar_len)
            lines.append(f"{medal} {emoji} **{name}** — `{count}` ({pct:.0f}%)\n`{bar}`")

        embed = (
            make_embed("gold")
            .title("\U0001f3c6 Klaus Social Ranking")
            .desc("\n\n".join(lines) if lines else "Nenhuma interação social ainda!")
            .field("Total de Interações", f"**{total}**", inline=True)
            .field("Mais Popular", f"{emojis.get(sorted_stats[0][0], '')} {names.get(sorted_stats[0][0], sorted_stats[0][0]).title()}" if sorted_stats else "N/A", inline=True)
            .footer("Klaus Social Ranking")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /AVENTURA
    # =========================

    @app_commands.command(name="aventura", description="Embarque em uma aventura de texto com escolhas!")
    @app_commands.checks.cooldown(1, 15, key=lambda i: i.user.id)
    async def aventura(self, interaction: discord.Interaction) -> None:
        adventure = random.choice(ADVENTURES)

        embed = (
            make_embed(0x8B5CF6)
            .title(f"\U0001f30d {adventure['title']}")
            .desc(
                f"_{adventure['scene']}_\n\n"
                f"**Escolha seu destino:**"
            )
            .footer("Klaus Aventura")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed, view=AventuraView(adventure))

    # =========================
    # /QUIZ
    # =========================

    @app_commands.command(name="quiz", description="Teste seus conhecimentos com um quiz rápido!")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def quiz(self, interaction: discord.Interaction) -> None:
        uid = interaction.user.id
        QUIZ_ACTIVE[uid] = True

        question = random.choice(QUIZ_QUESTIONS)
        current_score = QUIZ_SCORES.get(uid, 0)

        options_text = "\n".join(
            f"**{['A', 'B', 'C', 'D'][i]})** {opt}" for i, opt in enumerate(question["options"])
        )

        embed = (
            make_embed(0x8B5CF6)
            .title("\U0001f9e0 Klaus Quiz")
            .desc(
                f"**{question['q']}**\n\n{options_text}\n\n"
                f"\U0001f3af **Sua pontuação:** {current_score}\n"
                f"\u23f0 **Tempo:** 15 segundos"
            )
            .footer("Klaus Quiz")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed, view=QuizView(question))

    # =========================
    # /POLL
    # =========================

    @app_commands.command(name="poll", description="Crie uma enquete rápida!")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    @app_commands.describe(
        question="Pergunta da enquete",
        option1="Opção 1",
        option2="Opção 2",
        option3="Opção 3 (opcional)",
        option4="Opção 4 (opcional)",
    )
    async def poll(
        self,
        interaction: discord.Interaction,
        question: str,
        option1: str,
        option2: str,
        option3: str = "",
        option4: str = "",
    ) -> None:
        options = [option1, option2]
        if option3:
            options.append(option3)
        if option4:
            options.append(option4)

        embed = (
            make_embed("purple")
            .title(f"\U0001f4ca {question}")
            .desc(
                "\n".join(
                    f"**{['1\ufe0f\u20e3', '2\ufe0f\u20e3', '3\ufe0f\u20e3', '4\ufe0f\u20e3'][i]})** {opt}"
                    for i, opt in enumerate(options)
                )
                + "\n\n\U0001f465 **Total:** 0 voto(s)"
            )
            .footer(f"Enquete por {interaction.user.display_name}")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(
            embed=embed,
            view=PollView(question, options, interaction.user.display_name),
        )


async def setup(bot: KlausBot) -> None:
    await bot.add_cog(Diversao(bot))

from __future__ import annotations

import asyncio
import random
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from embed_builder import KlausEmbed as make_embed

if TYPE_CHECKING:
    from klaus import KlausBot

# ── Truth or Dare Data ──────────────────────────────────────────────

TOD_CATEGORIES = {
    "leve": {"label": "\U0001f7e2 Leve", "desc": "Para quebrar o gelo", "color": 0x22C55E},
    "medio": {"label": "\U0001f7e1 Médio", "desc": "Começa a ficar interessante", "color": 0xF59E0B},
    "forte": {"label": "\U0001f534 Forte", "desc": "Só para os corajosos", "color": 0xEF4444},
    "louco": {"label": "\U0001f480 Louco", "desc": "Sem limites!", "color": 0x8B5CF6},
}

TRUTHS = {
    "leve": [
        "Qual é a sua cor favorita e por quê?",
        "Qual foi o último presente que deu para alguém?",
        "Qual é o seu maior medo?",
        "Qual é o seu jogo favorito de todos os tempos?",
        "Você já fingiu estar doente para faltar algo?",
        "Qual é o animal que você mais tem medo?",
        "Qual é a música que você mais ouve no momento?",
        "Qual foi a maior mentira que já contou?",
        "Se pudesse ter qualquer animal de estimação, qual seria?",
        "Qual é a sua comida favorita?",
        "Você já chorou assistindo um filme?",
        "Qual foi a nota mais baixa que já tirou?",
        "O que mais te irrita nas pessoas?",
        "Qual é a sua série favorita?",
        "Se fosse invisível por um dia, o que faria?",
        "Qual é o seu sinal zodíaco? Acredita nele?",
        "Qual é o apelido mais engraçado que já teve?",
        "Qual é a sua estação do ano favorita?",
        "Você prefere praia ou montanha?",
        "Qual foi o melhor aniversário que já teve?",
        "Qual é a sua memória mais feliz da infância?",
        "Você gosta de surpresas?",
        "Qual é o seu livro favorito?",
        "Se pudesse jantar com qualquer pessoa, quem seria?",
        "Qual é o seu maior arrependimento?",
        "O que mais te faz rir?",
        "Qual é a sua maior insegurança?",
        "Você prefere ligação ou mensagem?",
        "Qual é a coisa mais estranha que já comeu?",
        "Se pudesse ter um superpoder, qual seria?",
    ],
    "medio": [
        "Qual foi a coisa mais vergonhosa que já fez em público?",
        "Você já beijou alguém que não gostava? Quem?",
        "Qual é o segredo que nunca contou para ninguém?",
        "Qual foi a pior desculpa que já deu para sair de uma situação?",
        "Alguém aqui já te traiu? Como descobriu?",
        "Qual é a pessoa mais estranha que já cruzou seu caminho?",
        "Você já fingiu gostar de algo para impressionar alguém?",
        "Qual foi a maior loucura que já fez por amor?",
        "Qual é a sua maior fantasia secreta?",
        "Você já olhou o celular de alguém escondido?",
        "Qual foi a pior nota que já teve e como reagiu?",
        "Você já mentiu para um amigo para protegê-lo?",
        "Qual é a coisa mais selfish que já fez?",
        "Você já sentiu ciúmes de um amigo? Por quê?",
        "Qual foi a maior decepção amorosa?",
        "Se pudesse voltar no tempo, o que mudaria?",
        "Qual é a coisa mais boba que te faz chorar?",
        "Você já se arrependeu de algo que postou nas redes sociais?",
        "Qual foi a pior primeira impressão que já teve de alguém?",
        "Você já traiu a confiança de alguém?",
    ],
    "forte": [
        "Qual é a maior besteira que já fez bêbado(a)?",
        "Você já se apaixonou pelo melhor amigo(a) de alguém? Quem?",
        "Qual foi o momento mais tenso que já viveu?",
        "Você já ficou com mais de uma pessoa na mesma noite?",
        "Qual é a coisa mais selfish que já fez em um relacionamento?",
        "Alguém aqui já teve um caso? Se arrepende?",
        "Qual foi a pior traição que já sofreu ou cometeu?",
        "Você já mandou mensagem para a pessoa errada? O que aconteceu?",
        "Qual é a sua maior fantasia que nunca contou?",
        "Você já fez algo ilegal? O quê?",
        "Qual foi o maior sacrifício que já fez por amor?",
        "Você já se sentiu atraído(a) por alguém comprometido?",
        "Qual é a coisa mais ousada que já fez no trabalho/escola?",
        "Você já contou um segredo que não deveria? De quem era?",
        "Qual foi a noite mais louca da sua vida?",
        "Você já brigou fisicamente com alguém?",
        "Qual foi a maior humilhação pública que já passou?",
        "Você já se aproveitou de alguém? Como?",
        "Qual é a coisa mais selfish que faria se tivesse certeza que ninguém veria?",
        "Você já se sentiu inferior a alguém? Quem e por quê?",
    ],
    "louco": [
        "Neste exato momento, envie uma mensagem sincera para a pessoa que mais te marcou. Só diga o que sente.",
        "Ligue para a última pessoa do seu WhatsApp e diga que a ama. Agora.",
        "Poste no seu story que está solteiro(a) e disponível. Não apague em 24h.",
        "Mande áudio para 3 pessoas aleatórias da sua lista dizendo 'eu te amo'.",
        "Deixe a pessoa à sua direita escolher o próximo post que você vai curtir nas redes sociais.",
        "Troque de lugar com alguém por 10 minutos e responda todas as perguntas como se fosse essa pessoa.",
        "Escreva uma carta de amor para o próximo desconhecido que encontrar. Entregue pessoalmente.",
        "Faça uma declaração de amor para o ar. Grava e poste.",
        "Ligue para sua mãe/pai e diga que vai casar. Grava a reação.",
        "Deixe o grupo escolher o próximo stories que você posta. Não pode recusar.",
        "Dê o seu celular por 2 minutos para a pessoa à sua esquerda. Ela pode mandar 1 mensagem.",
        "Coma uma colher de pimenta ou beba algo azedo que o grupo escolher.",
        "Fale sobre a sua vida amorosa para um desconhecido. Grava sem ele saber.",
        "Faça uma coreografia de 30 segundos e poste. Sem desculpas.",
        "Escreva o nome da sua crush na bio por 1 hora.",
        "Compre algo para a pessoa que mais te irrita e entregue com um sorriso.",
        "Faça uma lista de 5 coisas que odeia em si mesmo e leia em voz alta.",
        "Dance por 1 minuto sem música. Grava e manda no grupo.",
        "Mande um áudio cantando a música mais brega que conseguir lembrar.",
        "Prometa algo impossível para o grupo e cumpra pelo menos uma parte.",
    ],
}

DARES = {
    "leve": [
        "Fale 'eu sou incrível' 5 vezes seguidas sem rir.",
        "Imite um animal por 30 segundos.",
        "Faça sua melhor pose de modelo e fique assim por 1 minuto.",
        "Cante o refrão da sua música favorita.",
        "Danse como se ninguém estivesse olhando por 30 segundos.",
        "Fale apenas em rimas pelos próximos 3 turnos.",
        "Deixe alguém escolher sua próxima busca no Google.",
        "Fale uma coisa engraçada sobre a pessoa à sua esquerda.",
        "Faça uma selfie fazendo a cara mais feia possível.",
        "Leia a última mensagem que enviou em voz alta.",
        "Conte uma piada. Se ninguém rir, beba água.",
        "Imite o som de 3 animais diferentes.",
        "Faça um juramento de lealdade para a pizza.",
        "Dance forró sozinho por 30 segundos.",
        "Faça uma declaração de amor para o celular.",
        "Grite 'EU SOU UM FRANGO' bem alto.",
        "Ande como um robô por 1 minuto.",
        "Fale 'bom dia' para 5 pessoas aleatórias aqui.",
        "Finga que está chovendo e dance sob a 'chuva'.",
        "Faça 10 flexões agora.",
    ],
    "medio": [
        "Ligue para a última pessoa ligada e diga 'nossa, que saudade'.",
        "Mande uma mensagem de voz cantando parabéns.",
        "Fale a verdade sobre a pessoa da sua esquerda: 3 coisas que observa nela.",
        "Poste uma foto vergonhosa no seu story por 5 minutos.",
        "Deixe a pessoa à direita escrever algo no seu WhatsApp. Só apague depois de 1 hora.",
        "Troque de camisa/blusa com alguém por 30 minutos.",
        "Fale sobre seu amor secreto para o grupo. (Pode inventar.)",
        "Coma algo que o grupo misturar sem reclamar.",
        "Faça uma massagem de 30 segundos na pessoa à sua direita.",
        "Escreva o nome de alguém no rosto com caneta. Fique assim até o final.",
        "Mande um áudio para sua ex/namorada falando que sente falta.",
        "Faça 20 agachamentos agora. O grupo conta.",
        "Deixe alguém escolher seu próximo status de WhatsApp.",
        "Imite alguém do grupo por 1 minuto. O grupo adivinha quem é.",
        "Fale a verdade sobre seu primeiro beijo. Todos os detalhes.",
        "Faça uma serenata para alguém aqui.",
        "Dê um abraço de 1 minuto na pessoa mais próxima.",
        "Escreva uma poesia romântica agora. Leia em voz alta.",
        "Faça sua melhor imitação de celebridade.",
        "Deixe o grupo postar algo no seu Instagram. Não pode apague em 1 hora.",
    ],
    "forte": [
        "Troque de lugar com a pessoa mais distante e fique como ela pelo resto do jogo.",
        "Mande uma mensagem para seu ex dizendo 'preciso falar algo sério' e depois desbloqueie.",
        "Deixe a pessoa que você mais gosta escolher sua foto de perfil. Não pode mudar em 24h.",
        "Fale 5 verdades constrangedoras sobre si mesmo em voz alta.",
        "Faça um pedido de desculpas sincero para alguém que já magoou. Grava e envia.",
        "Deixe alguém ver suas últimas 10 conversas no WhatsApp por 2 minutos.",
        "Poste 'estou solteiro(a) e disponível' nos stories. Fique 1h.",
        "Deixe alguém escolher sua bio do Instagram. Não pode mudar em 24h.",
        "Mande uma carta de amor escrita à mão para alguém. Foto e envia.",
        "Ligue para sua mãe e diga que está namorando. Grava.",
        "Faça uma declaração de amor ao vivo para alguém do grupo.",
        "Poste a pior foto sua que encontrar. Fique 1 hora.",
        "Deixe alguém escolher sua próxima compra online. Pague.",
        "Fale sobre a pessoa que mais te machucou. Tudo.",
        "Dance algo sensual por 1 minuto. Grava e manda no grupo.",
        "Escreva uma lista de 10 qualidades e 10 defeitos seus. Leia em voz alta.",
        "Mande um áudio dizendo 'eu te amo' para 5 pessoas. Grava as reações.",
        "Faça algo que tem medo de fazer. Conte depois.",
        "Troque de vida com alguém por 24h nas redes sociais.",
    ],
    "louco": [
        "Neste momento, mande uma mensagem para a crush confessando seus sentimentos.",
        "Ligue para sua ex e diga que ainda ama. Grava a reação.",
        "Deixe o grupo controlar suas redes sociais por 1 hora.",
        "Escreva um poema de amor e poste. Taggue a pessoa certa.",
        "Faça uma declaração de amor no estilo telenovela. Grave e poste.",
        "Mande áudio cantando uma música romântica para a pessoa que gosta.",
        "Troque sua foto de perfil para uma selfie ao vivo. Não mude em 24h.",
        "Deixe alguém escolher a pessoa que você vai beijar no próximo rolê.",
        "Faça uma lista de todas as pessoas que já se apaixonou. Leia em voz alta.",
        "Ligue para alguém e diga que precisa falar algo urgente. Conte a verdade.",
        "Poste que está solteiro(a) e disponível no Instagram. 24 horas.",
        "Escreva uma carta de despedida para o solteirato(a) e poste.",
        "Mande mensagem para 5 exs dizendo 'lembra de mim?'",
        "Faça uma serenata gravada e poste em 3 plataformas.",
        "Deixe o grupo escolher sua bio de todas as redes por 48h.",
        "Comprometa-se publicamente com algo que tem medo de fazer.",
        "Faça um pedido de desculpas público para alguém. Poste.",
        "Envie flores para alguém escolhido pelo grupo.",
        "Dance e grava algo trending do TikTok agora.",
        "Deixe o grupo escolher onde você vai no próximo fim de semana.",
    ],
}


# ── TOD Views ───────────────────────────────────────────────────────

class TODCategoryView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=60)
        self.author_id = author_id
        for key, cat in TOD_CATEGORIES.items():
            self.add_item(CategoryButton(key, cat, author_id))

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True


class CategoryButton(discord.ui.Button):
    def __init__(self, key: str, cat: dict, author_id: int):
        super().__init__(
            label=cat["label"],
            style=discord.ButtonStyle.secondary,
            custom_id=f"tod_cat_{key}_{author_id}",
        )
        self.key = key
        self.author_id = author_id

    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Não é sua vez de escolher!", ephemeral=True)
            return

        view = TODTypeView(self.key, self.author_id)
        cat = TOD_CATEGORIES[self.key]
        embed = (
            make_embed(cat["color"])
            .title(f"Truth or Dare — {cat['label']}")
            .desc(f"Categoria: **{cat['desc']}**\n\nAgora escolha: **Verdade** ou **Desafio**?")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.edit_message(embed=embed, view=view)


class TODTypeView(discord.ui.View):
    def __init__(self, category: str, author_id: int):
        super().__init__(timeout=60)
        self.category = category
        self.author_id = author_id
        self.add_item(TruthButton(category, author_id))
        self.add_item(DareButton(category, author_id))
        self.add_item(SpinButton(category, author_id))

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True


class TruthButton(discord.ui.Button):
    def __init__(self, category: str, author_id: int):
        super().__init__(
            label="\U0001f4ac Verdade",
            style=discord.ButtonStyle.primary,
            custom_id=f"tod_truth_{category}_{author_id}",
        )
        self.category = category

    async def callback(self, interaction: discord.Interaction) -> None:
        pool = TRUTHS.get(self.category, TRUTHS["leve"])
        question = random.choice(pool)

        cat = TOD_CATEGORIES[self.category]
        embed = (
            make_embed(cat["color"])
            .title("\U0001f4ac VERDADE!")
            .desc(f"**{interaction.user.display_name}**, responda com honestidade:\n\n>>> {question}")
            .field("Categoria", f"{cat['label']} — {cat['desc']}", inline=True)
            .field("Tipo", "\U0001f4ac Verdade", inline=True)
            .thumb(interaction.user.display_avatar.url)
            .footer("Se recusar, beba água! \U0001f4a7")
            .timestamp()
            .build()
        )
        view = AfterTODView(self.category, interaction.user.id)
        await interaction.response.edit_message(embed=embed, view=view)


class DareButton(discord.ui.Button):
    def __init__(self, category: str, author_id: int):
        super().__init__(
            label="\U0001f3af Desafio",
            style=discord.ButtonStyle.danger,
            custom_id=f"tod_dare_{category}_{author_id}",
        )
        self.category = category

    async def callback(self, interaction: discord.Interaction) -> None:
        pool = DARES.get(self.category, DARES["leve"])
        dare = random.choice(pool)

        cat = TOD_CATEGORIES[self.category]
        embed = (
            make_embed(cat["color"])
            .title("\U0001f3af DESAFIO!")
            .desc(f"**{interaction.user.display_name}**, sua missão:\n\n>>> {dare}")
            .field("Categoria", f"{cat['label']} — {cat['desc']}", inline=True)
            .field("Tipo", "\U0001f3af Desafio", inline=True)
            .thumb(interaction.user.display_avatar.url)
            .footer("Se recusar, beba água! \U0001f4a7")
            .timestamp()
            .build()
        )
        view = AfterTODView(self.category, interaction.user.id)
        await interaction.response.edit_message(embed=embed, view=view)


class SpinButton(discord.ui.Button):
    def __init__(self, category: str, author_id: int):
        super().__init__(
            label="\U0001f3b2 Sortear",
            style=discord.ButtonStyle.success,
            custom_id=f"tod_spin_{category}_{author_id}",
        )
        self.category = category

    async def callback(self, interaction: discord.Interaction) -> None:
        is_truth = random.random() < 0.5
        pool = TRUTHS if is_truth else DARES
        item = random.choice(pool.get(self.category, pool["leve"]))
        tipo = "VERDADE" if is_truth else "DESAFIO"
        icon = "\U0001f4ac" if is_truth else "\U0001f3af"

        cat = TOD_CATEGORIES[self.category]
        embed = (
            make_embed(cat["color"])
            .title(f"{icon} {tipo} ALEATÓRIO!")
            .desc(f"**{interaction.user.display_name}**, o destino escolheu:\n\n>>> {item}")
            .field("Categoria", f"{cat['label']} — {cat['desc']}", inline=True)
            .field("Tipo", f"{icon} {tipo} (Sorteado)", inline=True)
            .thumb(interaction.user.display_avatar.url)
            .footer("Se recusar, beba água! \U0001f4a7")
            .timestamp()
            .build()
        )
        view = AfterTODView(self.category, interaction.user.id)
        await interaction.response.edit_message(embed=embed, view=view)


class AfterTODView(discord.ui.View):
    def __init__(self, category: str, author_id: int):
        super().__init__(timeout=120)
        self.add_item(NextRoundButton(category, author_id))
        self.add_item(ChangeCategoryButton(author_id))
        self.add_item(StopButton())

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True


class NextRoundButton(discord.ui.Button):
    def __init__(self, category: str, author_id: int):
        super().__init__(
            label="\u27a1\ufe0f Próximo",
            style=discord.ButtonStyle.primary,
            custom_id=f"tod_next_{category}_{author_id}",
        )
        self.category = category

    async def callback(self, interaction: discord.Interaction) -> None:
        view = TODTypeView(self.category, interaction.user.id)
        cat = TOD_CATEGORIES[self.category]
        embed = (
            make_embed(cat["color"])
            .title(f"Truth or Dare — {cat['label']}")
            .desc(f"**{interaction.user.display_name}**, escolha:\n\n**Verdade** ou **Desafio**?")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.edit_message(embed=embed, view=view)


class ChangeCategoryButton(discord.ui.Button):
    def __init__(self, author_id: int):
        super().__init__(
            label="\U0001f504 Mudar Categoria",
            style=discord.ButtonStyle.secondary,
            custom_id=f"tod_change_{author_id}",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        view = TODCategoryView(interaction.user.id)
        embed = (
            make_embed("purple")
            .title("\U0001f3b2 Truth or Dare")
            .desc(
                f"**{interaction.user.display_name}**, escolha a categoria:\n\n"
                "\U0001f7e2 **Leve** — Para quebrar o gelo\n"
                "\U0001f7e1 **Médio** — Começa a ficar interessante\n"
                "\U0001f534 **Forte** — Só para os corajosos\n"
                "\U0001f480 **Louco** — Sem limites!"
            )
            .thumb(interaction.user.display_avatar.url)
            .footer("Se recusar, beba água! \U0001f4a7")
            .timestamp()
            .build()
        )
        await interaction.response.edit_message(embed=embed, view=view)


class StopButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="\u23f9\ufe0f Parar",
            style=discord.ButtonStyle.danger,
            custom_id="tod_stop",
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        embed = (
            make_embed("info")
            .title("\U0001f44b Truth or Dare — Encerrado!")
            .desc(f"**{interaction.user.display_name}** encerrou a rodada!\n\nObrigado por jogar!")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.edit_message(embed=embed, view=None)


# ── Versus Mode ─────────────────────────────────────────────────────

class TODVersusView(discord.ui.View):
    def __init__(self, challenger: discord.Member, target: discord.Member):
        super().__init__(timeout=120)
        self.challenger = challenger
        self.target = target
        self.current = challenger
        self.scores = {challenger.id: 0, target.id: 0}
        self.round = 0
        self.streak = {challenger.id: 0, target.id: 0}

    def next_turn(self) -> discord.Member:
        self.current = self.target if self.current == self.challenger else self.challenger
        self.round += 1
        return self.current

    def add_score(self, user_id: int) -> int:
        self.scores[user_id] = self.scores.get(user_id, 0) + 1
        self.streak[user_id] = self.streak.get(user_id, 0) + 1
        self.streak[self.target.id if user_id == self.challenger.id else self.challenger.id] = 0
        return self.streak[user_id]

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True


class VersusTruthButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="\U0001f4ac Verdade", style=discord.ButtonStyle.primary, custom_id="tod_vs_truth")

    async def callback(self, interaction: discord.Interaction) -> None:
        view: TODVersusView = self.view
        question = random.choice(TRUTHS["medio"])
        user = interaction.user

        streak = view.add_score(user.id)
        streak_text = f"\n\U0001f525 Streak: **{streak}**" if streak >= 2 else ""

        embed = (
            make_embed("purple")
            .title(f"\U0001f4ac VERDADE — Rodada {view.round}")
            .desc(f"**{user.display_name}**, responda:\n\n>>> {question}")
            .field("Placar", f"**{view.challenger.display_name}**: {view.scores[view.challenger.id]}\n**{view.target.display_name}**: {view.scores[view.target.id]}")
            .field("Streak", f"**{user.display_name}**: {streak}{streak_text}")
            .thumb(user.display_avatar.url)
            .timestamp()
            .build()
        )

        next_user = view.next_turn()
        next_view = TODVersusView.__new__(TODVersusView)
        next_view.__dict__.update(view.__dict__)
        next_view.add_item(VersusTruthButton())
        next_view.add_item(VersusDareButton())
        next_view.add_item(VersusSpinButton())

        await interaction.response.edit_message(embed=embed, view=next_view)


class VersusDareButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="\U0001f3af Desafio", style=discord.ButtonStyle.danger, custom_id="tod_vs_dare")

    async def callback(self, interaction: discord.Interaction) -> None:
        view: TODVersusView = self.view
        dare = random.choice(DARES["medio"])
        user = interaction.user

        streak = view.add_score(user.id)
        streak_text = f"\n\U0001f525 Streak: **{streak}**" if streak >= 2 else ""

        embed = (
            make_embed("warning")
            .title(f"\U0001f3af DESAFIO — Rodada {view.round}")
            .desc(f"**{user.display_name}**, sua missão:\n\n>>> {dare}")
            .field("Placar", f"**{view.challenger.display_name}**: {view.scores[view.challenger.id]}\n**{view.target.display_name}**: {view.scores[view.target.id]}")
            .field("Streak", f"**{user.display_name}**: {streak}{streak_text}")
            .thumb(user.display_avatar.url)
            .timestamp()
            .build()
        )

        next_user = view.next_turn()
        next_view = TODVersusView.__new__(TODVersusView)
        next_view.__dict__.update(view.__dict__)
        next_view.add_item(VersusTruthButton())
        next_view.add_item(VersusDareButton())
        next_view.add_item(VersusSpinButton())

        await interaction.response.edit_message(embed=embed, view=next_view)


class VersusSpinButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="\U0001f3b2 Sortear", style=discord.ButtonStyle.success, custom_id="tod_vs_spin")

    async def callback(self, interaction: discord.Interaction) -> None:
        view: TODVersusView = self.view
        is_truth = random.random() < 0.5
        pool = TRUTHS["medio"] if is_truth else DARES["medio"]
        item = random.choice(pool)
        user = interaction.user

        streak = view.add_score(user.id)
        streak_text = f"\n\U0001f525 Streak: **{streak}**" if streak >= 2 else ""
        tipo = "VERDADE" if is_truth else "DESAFIO"
        icon = "\U0001f4ac" if is_truth else "\U0001f3af"
        color = "purple" if is_truth else "warning"

        embed = (
            make_embed(color)
            .title(f"{icon} {tipo} ALEATÓRIO — Rodada {view.round}")
            .desc(f"**{user.display_name}**, o destino escolheu:\n\n>>> {item}")
            .field("Placar", f"**{view.challenger.display_name}**: {view.scores[view.challenger.id]}\n**{view.target.display_name}**: {view.scores[view.target.id]}")
            .field("Streak", f"**{user.display_name}**: {streak}{streak_text}")
            .thumb(user.display_avatar.url)
            .timestamp()
            .build()
        )

        next_user = view.next_turn()
        next_view = TODVersusView.__new__(TODVersusView)
        next_view.__dict__.update(view.__dict__)
        next_view.add_item(VersusTruthButton())
        next_view.add_item(VersusDareButton())
        next_view.add_item(VersusSpinButton())

        await interaction.response.edit_message(embed=embed, view=next_view)


# ── Cog ─────────────────────────────────────────────────────────────

class DiversaoExtra(commands.Cog):
    def __init__(self, bot: KlausBot) -> None:
        self.bot = bot


class RussianRouletteView(discord.ui.View):
    def __init__(self, author_id: int):
        super().__init__(timeout=120)
        self.author_id = author_id
        self.chamber = random.randint(1, 6)
        self.pull_count = 0

    @discord.ui.button(label="\U0001f52b Puxar o Gatilho", style=discord.ButtonStyle.danger, custom_id="russian_pull")
    async def pull(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message("Não é sua vez!", ephemeral=True)
            return

        self.pull_count += 1

        if self.pull_count == self.chamber:
            self.clear_items()
            embed = (
                make_embed("error")
                .title("\U0001f4a5 BOOM!")
                .desc(
                    f"**{interaction.user.display_name}**...\n\n"
                    f"**LEVOU UM TIRO NA 6ª CÂMARA!**\n\n"
                    f"\U0001f480 *Encerre seus assuntos.*\n\n"
                    f"Total de puxadas: **{self.pull_count}**"
                )
                .thumb(interaction.user.display_avatar.url)
                .footer("RIP \U0001f480")
                .timestamp()
                .build()
            )
            await interaction.response.edit_message(embed=embed, view=self)
        else:
            remaining = 6 - self.pull_count
            embed = (
                make_embed("warning")
                .title(f"\U0001f50c Click... ({self.pull_count} puxadas)")
                .desc(
                    f"**{interaction.user.display_name}** sobreviveu!\n\n"
                    f"Câmaras restantes: **{remaining}**\n"
                    f"Chance de morrer na próxima: **{1}/{remaining}**"
                )
                .thumb(interaction.user.display_avatar.url)
                .footer("Sobreviveu... por enquanto...")
                .timestamp()
                .build()
            )
            await interaction.response.edit_message(embed=embed)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True


async def setup(bot: KlausBot) -> None:
    await bot.add_cog(DiversaoExtra(bot))

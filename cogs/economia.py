from __future__ import annotations

import asyncio
import logging
import random
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from config import settings
from database import db
from embed_builder import KlausEmbed as make_embed
from helpers import format_koins, calculate_streak_bonus
from profile_generator import generate_profile

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from klaus import KlausBot


# =========================
# VIEW: Coinflip
# =========================

class CoinflipView(discord.ui.View):
    def __init__(self, author: discord.Member, amount: int) -> None:
        super().__init__(timeout=30)
        self.author = author
        self.amount = amount

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                embed=make_embed.error("Acesso Negado", "Essa aposta não é sua!"),
                ephemeral=True,
            )
            return False
        return True

    async def _resolve(self, interaction: discord.Interaction, chosen: str) -> None:
        balance = await db.get_balance(self.author.id)
        if balance < self.amount:
            await interaction.response.edit_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                view=None,
            )
            return

        result = random.choice(["cara", "coroa"])
        emoji = "\U0001fa99" if result == "cara" else "\U0001f538"
        won = chosen == result

        if won:
            await db.add_koins(self.author.id, self.amount)
            if self.amount >= 10000:
                await db.add_achievement(self.author.id, "big_win")
            bal = await db.get_balance(self.author.id)
            embed = (
                make_embed("success")
                .title(f"\U0001fa99 {result.title()}!")
                .desc(f"O coin caiu em **{result.upper()}**!\nVocê ganhou **{format_koins(self.amount)}** koins!")
                .field("Escolha", f"```{chosen.upper()}```")
                .field("Resultado", f"{emoji} **{result.upper()}**")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(self.author.display_avatar.url)
                .footer("Klaus Coinflip")
                .timestamp()
                .build()
            )
        else:
            await db.remove_koins(self.author.id, self.amount)
            bal = await db.get_balance(self.author.id)
            embed = (
                make_embed("error")
                .title(f"\U0001f538 {result.title()}!")
                .desc(f"O coin caiu em **{result.upper()}**!\nVocê perdeu **{format_koins(self.amount)}** koins!")
                .field("Escolha", f"```{chosen.upper()}```")
                .field("Resultado", f"{emoji} **{result.upper()}**")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(self.author.display_avatar.url)
                .footer("Klaus Coinflip")
                .timestamp()
                .build()
            )

        view = CoinflipView(self.author, self.amount)
        await interaction.response.edit_message(embed=embed, view=view)

    @discord.ui.button(label="Cara \U0001fa99", style=discord.ButtonStyle.primary)
    async def caras(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._resolve(interaction, "cara")

    @discord.ui.button(label="Coroa \U0001f538", style=discord.ButtonStyle.secondary)
    async def coroas(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._resolve(interaction, "coroa")


# =========================
# VIEW: Dice
# =========================

class DiceView(discord.ui.View):
    def __init__(self, author: discord.Member, amount: int) -> None:
        super().__init__(timeout=30)
        self.author = author
        self.amount = amount

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                embed=make_embed.error("Acesso Negado", "Essa aposta não é sua!"),
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Menor (2-6)", style=discord.ButtonStyle.red)
    async def menor(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._resolve(interaction, "menor", 2, 6)

    @discord.ui.button(label="Meio (7-10)", style=discord.ButtonStyle.blurple)
    async def meio(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._resolve(interaction, "meio", 7, 10)

    @discord.ui.button(label="Maior (11-12)", style=discord.ButtonStyle.green)
    async def maior(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        await self._resolve(interaction, "maior", 11, 12)

    async def _resolve(self, interaction: discord.Interaction, choice: str, low: int, high: int) -> None:
        balance = await db.get_balance(self.author.id)
        if balance < self.amount:
            await interaction.response.edit_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                view=None,
            )
            return

        d1 = random.randint(1, 6)
        d2 = random.randint(1, 6)
        total = d1 + d2
        dice_faces = {1: "\u2680", 2: "\u2681", 3: "\u2682", 4: "\u2683", 5: "\u2684", 6: "\u2685"}
        dice_str = f"{dice_faces[d1]} + {dice_faces[d2]}"

        won = low <= total <= high
        multiplier = 3 if choice == "meio" else 2

        if won:
            gain = self.amount * (multiplier - 1)
            await db.add_koins(self.author.id, gain)
            bal = await db.get_balance(self.author.id)
            embed = (
                make_embed("success")
                .title(f"\U0001f3b2 Resultado: {total}")
                .desc(f"{dice_str} = **{total}**\nVocê ganhou **{format_koins(gain)}** koins!")
                .field("Escolha", f"```{choice.upper()}```")
                .field("Multiplicador", f"```x{multiplier}```")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(self.author.display_avatar.url)
                .footer("Klaus Dice")
                .timestamp()
                .build()
            )
        else:
            await db.remove_koins(self.author.id, self.amount)
            bal = await db.get_balance(self.author.id)
            embed = (
                make_embed("error")
                .title(f"\U0001f3b2 Resultado: {total}")
                .desc(f"{dice_str} = **{total}**\nVocê perdeu **{format_koins(self.amount)}** koins!")
                .field("Escolha", f"```{choice.upper()}```")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(self.author.display_avatar.url)
                .footer("Klaus Dice")
                .timestamp()
                .build()
            )

        view = DiceView(self.author, self.amount)
        await interaction.response.edit_message(embed=embed, view=view)


# =========================
# VIEW: Blackjack
# =========================

class BlackjackView(discord.ui.View):
    def __init__(self, author: discord.Member, amount: int, player: list[str], dealer: list[str]) -> None:
        super().__init__(timeout=30)
        self.author = author
        self.amount = amount
        self.player = player
        self.dealer = dealer

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                embed=make_embed.error("Acesso Negado", "Essa mão não é sua!"),
                ephemeral=True,
            )
            return False
        return True

    @staticmethod
    def _hand_str(hand: list[str]) -> str:
        return " ".join(hand)

    @staticmethod
    def _hand_value(hand: list[str]) -> int:
        val = 0
        aces = 0
        for c in hand:
            r = c[0]
            if r in ("J", "Q", "K"):
                val += 10
            elif r == "A":
                val += 11
                aces += 1
            else:
                try:
                    val += int(r)
                except ValueError:
                    val += 10
        while val > 21 and aces:
            val -= 10
            aces -= 1
        return val

    def _build_embed(self, hide_dealer: bool = True, result: str = "") -> discord.Embed:
        pv = self._hand_value(self.player)
        dv = self._hand_value(self.dealer)
        dealer_str = self._hand_str(self.dealer) if not hide_dealer else f"{self.dealer[0]} \U0001f0cf"
        color = "success" if result == "win" else "error" if result == "lose" else "purple"

        embed = (
            make_embed(color)
            .title("\U0001f0cf Blackjack")
            .field(f"Dealer ({dv if not hide_dealer else '?'} points)", f"```{dealer_str}```")
            .field(f"Você ({pv} points)", f"```{self._hand_str(self.player)}```")
            .field("Aposta", f"```{format_koins(self.amount)} koins```")
            .thumb(self.author.display_avatar.url)
        )
        if result:
            embed.desc(result)
        embed.timestamp()
        embed.footer("Klaus Blackjack")
        return embed.build()

    @discord.ui.button(label="Pedir Carta \U0001f0cf", style=discord.ButtonStyle.green)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        suits = ["\u2660", "\u2665", "\u2666", "\u2663"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.player.append(f"{random.choice(ranks)}{random.choice(suits)}")

        pv = self._hand_value(self.player)
        if pv > 21:
            await db.remove_koins(self.author.id, self.amount)
            bal = await db.get_balance(self.author.id)
            embed = (
                make_embed("error")
                .title("\U0001f0cf Blackjack \u2014 Estourou!")
                .desc(f"Você pegou **{pv}** pontos e estourou!\nPerdeu **{format_koins(self.amount)}** koins.")
                .field("Sua Mão", f"```{self._hand_str(self.player)}```")
                .field("Dealer", f"```{self._hand_str(self.dealer)}```")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(self.author.display_avatar.url)
                .footer("Klaus Blackjack")
                .timestamp()
                .build()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return

        await interaction.response.edit_message(embed=self._build_embed(), view=self)

    @discord.ui.button(label="Parar \u2705", style=discord.ButtonStyle.red)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        while self._hand_value(self.dealer) < 17:
            suits = ["\u2660", "\u2665", "\u2666", "\u2663"]
            ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
            self.dealer.append(f"{random.choice(ranks)}{random.choice(suits)}")

        pv = self._hand_value(self.player)
        dv = self._hand_value(self.dealer)

        if dv > 21 or pv > dv:
            await db.add_koins(self.author.id, self.amount)
            bal = await db.get_balance(self.author.id)
            embed = (
                make_embed("success")
                .title("\U0001f0cf Blackjack \u2014 Você Venceu!")
                .desc(f"Dealer: **{dv}** pts | Você: **{pv}** pts\nGanhou **{format_koins(self.amount)}** koins!")
                .field("Dealer", f"```{self._hand_str(self.dealer)}```")
                .field("Você", f"```{self._hand_str(self.player)}```")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(self.author.display_avatar.url)
                .footer("Klaus Blackjack")
                .timestamp()
                .build()
            )
        elif pv == dv:
            embed = (
                make_embed("warning")
                .title("\U0001f0cf Blackjack \u2014 Empate!")
                .desc(f"Ambos com **{pv}** pontos. Aposta devolvida!")
                .field("Dealer", f"```{self._hand_str(self.dealer)}```")
                .field("Você", f"```{self._hand_str(self.player)}```")
                .thumb(self.author.display_avatar.url)
                .footer("Klaus Blackjack")
                .timestamp()
                .build()
            )
        else:
            await db.remove_koins(self.author.id, self.amount)
            bal = await db.get_balance(self.author.id)
            embed = (
                make_embed("error")
                .title("\U0001f0cf Blackjack \u2014 Dealer Venceu!")
                .desc(f"Dealer: **{dv}** pts | Você: **{pv}** pts\nPerdeu **{format_koins(self.amount)}** koins.")
                .field("Dealer", f"```{self._hand_str(self.dealer)}```")
                .field("Você", f"```{self._hand_str(self.player)}```")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(self.author.display_avatar.url)
                .footer("Klaus Blackjack")
                .timestamp()
                .build()
            )

        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Dobrar \U0001f504", style=discord.ButtonStyle.blurple)
    async def double(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        balance = await db.get_balance(self.author.id)
        if balance < self.amount:
            await interaction.response.edit_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                view=None,
            )
            return

        await db.remove_koins(self.author.id, self.amount)
        self.amount *= 2

        suits = ["\u2660", "\u2665", "\u2666", "\u2663"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
        self.player.append(f"{random.choice(ranks)}{random.choice(suits)}")

        pv = self._hand_value(self.player)
        if pv > 21:
            bal = await db.get_balance(self.author.id)
            embed = (
                make_embed("error")
                .title("\U0001f0cf Blackjack \u2014 Estourou ao Dobrar!")
                .desc(f"Você pegou **{pv}** pontos e estourou!\nPerdeu **{format_koins(self.amount)}** koins.")
                .field("Sua Mão", f"```{self._hand_str(self.player)}```")
                .field("Dealer", f"```{self._hand_str(self.dealer)}```")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(self.author.display_avatar.url)
                .footer("Klaus Blackjack")
                .timestamp()
                .build()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return

        while self._hand_value(self.dealer) < 17:
            self.dealer.append(f"{random.choice(ranks)}{random.choice(suits)}")

        dv = self._hand_value(self.dealer)
        if dv > 21 or pv > dv:
            await db.add_koins(self.author.id, self.amount)
            bal = await db.get_balance(self.author.id)
            embed = (
                make_embed("success")
                .title("\U0001f0cf Blackjack \u2014 Dobrou e Venceu!")
                .desc(f"Dealer: **{dv}** pts | Você: **{pv}** pts\nGanhou **{format_koins(self.amount)}** koins!")
                .field("Dealer", f"```{self._hand_str(self.dealer)}```")
                .field("Você", f"```{self._hand_str(self.player)}```")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(self.author.display_avatar.url)
                .footer("Klaus Blackjack")
                .timestamp()
                .build()
            )
        else:
            bal = await db.get_balance(self.author.id)
            embed = (
                make_embed("error")
                .title("\U0001f0cf Blackjack \u2014 Dobrou e Perdeu!")
                .desc(f"Dealer: **{dv}** pts | Você: **{pv}** pts\nPerdeu **{format_koins(self.amount)}** koins.")
                .field("Dealer", f"```{self._hand_str(self.dealer)}```")
                .field("Você", f"```{self._hand_str(self.player)}```")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(self.author.display_avatar.url)
                .footer("Klaus Blackjack")
                .timestamp()
                .build()
            )

        await interaction.response.edit_message(embed=embed, view=None)


# =========================
# VIEW: Duel Request
# =========================

class DuelRequestView(discord.ui.View):
    def __init__(self, challenger: discord.Member, target: discord.Member, amount: int) -> None:
        super().__init__(timeout=30)
        self.challenger = challenger
        self.target = target
        self.amount = amount

    @discord.ui.button(label="Aceitar \u2694\ufe0f", style=discord.ButtonStyle.green)
    async def aceitar(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                embed=make_embed.error("Acesso Negado", "Esse desafio não é para você!"),
                ephemeral=True,
            )
            return

        chal_bal = await db.get_balance(self.challenger.id)
        tgt_bal = await db.get_balance(self.target.id)
        if chal_bal < self.amount or tgt_bal < self.amount:
            await interaction.response.edit_message(
                embed=make_embed.error("Saldo Insuficiente", "Um dos jogadores não tem koins suficientes."),
                view=None,
            )
            return

        await db.remove_koins(self.challenger.id, self.amount)
        await db.remove_koins(self.target.id, self.amount)

        if random.random() < 0.5:
            winner, loser = self.challenger, self.target
        else:
            winner, loser = self.target, self.challenger

        prize = self.amount * 2
        await db.add_koins(winner.id, prize)
        w_bal = await db.get_balance(winner.id)

        embed = (
            make_embed("success")
            .title("\u2694\ufe0f Duelo Finalizado!")
            .desc(f"**{winner.mention}** venceu o duelo contra **{loser.mention}**!")
            .field("Prêmio", f"```{format_koins(prize)} koins```")
            .field("Ganhador", f"```{winner.display_name} ({format_koins(w_bal)} koins)```")
            .thumb(winner.display_avatar.url)
            .footer("Klaus Duel")
            .timestamp()
            .build()
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Recusar \u274c", style=discord.ButtonStyle.red)
    async def recusar(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if interaction.user.id != self.target.id:
            await interaction.response.send_message(
                embed=make_embed.error("Acesso Negado", "Esse desafio não é para você!"),
                ephemeral=True,
            )
            return

        embed = make_embed("warning").title("Duelo Recusado").desc(f"{self.target.display_name} recusou o duelo.").timestamp().footer("Klaus Duel").build()
        await interaction.response.edit_message(embed=embed, view=None)


# =========================
# VIEW: Apostar Again
# =========================

class ApostarAgainView(discord.ui.View):
    def __init__(self, author: discord.Member, amount: int) -> None:
        super().__init__(timeout=30)
        self.author = author
        self.amount = amount

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                embed=make_embed.error("Acesso Negado", "Essa aposta não é sua!"),
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Apostar Novamente \U0001f3b0", style=discord.ButtonStyle.blurple)
    async def repeat(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        balance = await db.get_balance(self.author.id)
        if balance < self.amount:
            await interaction.response.edit_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                view=None,
            )
            return

        stats = await db.get_stats(self.author.id)
        jackpot_chance = settings.jackpot_base_chance
        big_bet = self.amount >= settings.big_bet_threshold

        if stats["easy_wins"] >= 3 and big_bet:
            jackpot_chance = 1
        elif stats["easy_wins"] >= 2 and big_bet:
            jackpot_chance = 3
        elif stats["easy_wins"] >= 1 and big_bet:
            jackpot_chance = 7
        if stats["profit"] >= 100000:
            jackpot_chance = max(1, jackpot_chance - 5)
        if stats["big_losses"] >= 1:
            jackpot_chance += 4

        slots = ["\U0001f352", "\U0001f34b", "\U0001f48e", "\U0001f340", "\u0037\u20e3", "\u2b50", "\U0001f525", "\U0001f451", "\U0001f4b0", "\U0001f3b2", "\U0001fa99", "\u26a1", "\U0001f347", "\U0001f976", "\U0001f3af"]

        is_jackpot = random.randint(1, 100) <= jackpot_chance
        if is_jackpot:
            symbol = random.choice(slots)
            final = [symbol, symbol, symbol]
        else:
            final = [random.choice(slots) for _ in range(3)]
            while final[0] == final[1] == final[2]:
                final = [random.choice(slots) for _ in range(3)]

        formatted_bet = format_koins(self.amount)

        embed = (
            make_embed("purple")
            .title("\U0001f3b0 Roleta Klaus")
            .desc(f"```\n\u2503 \u2753 \u2502 \u2753 \u2502 \u2753 \u2503\n```\nApostado: **{formatted_bet}** koins")
            .thumb(self.author.display_avatar.url)
            .footer("Roleta Klaus \u2022 Girando...")
            .timestamp()
            .build()
        )
        await interaction.response.edit_message(embed=embed, view=None)
        message = await interaction.original_response()
        current = ["\u2753", "\u2753", "\u2753"]

        slot_names = ["Primeiro", "Segundo", "\u00daltimo"]
        colors = [0xE74C3C, 0xE67E22, 0xF1C40F]

        for i in range(3):
            for _ in range(6):
                for j in range(i, 3):
                    current[j] = random.choice(slots)
                spinning = (
                    make_embed(colors[i])
                    .title("\U0001f3b0 Roleta Klaus")
                    .desc(f"```\n\u2503 {' \u2502 '.join(current)} \u2503\n```\nGirando: **{slot_names[i]}** slot...")
                    .thumb(self.author.display_avatar.url)
                    .footer("Roleta Klaus \u2022 Girando...")
                    .timestamp()
                    .build()
                )
                await message.edit(embed=spinning)
                await asyncio.sleep(0.5)
            current[i] = final[i]

        if current[0] == current[1] == current[2]:
            bonus = random.randint(settings.jackpot_bonus_min, settings.jackpot_bonus_max)
            total_won = self.amount + bonus
            await db.add_koins(self.author.id, total_won)
            await db.add_win(self.author.id, total_won)
            await db.add_achievement(self.author.id, "jackpot")
            result = (
                make_embed("gold")
                .title("\U0001f48e JACKPOT!")
                .desc(f"```\n\u2503 {' \u2502 '.join(current)} \u2503\n```\n\U0001f389 **3 símbolos iguais!**")
                .field("\U0001f4b0 Apostado", f"```{formatted_bet} koins```", True)
                .field("\u2728 Bônus", f"```+ {format_koins(bonus)} koins```", True)
                .field("\U0001f3c6 Total", f"```{format_koins(total_won)} koins```", True)
                .thumb(self.author.display_avatar.url)
                .footer("Klaus Roleta")
                .timestamp()
                .build()
            )
        else:
            loss_extra = random.randint(settings.loss_extra_min, settings.loss_extra_max)
            total_loss = self.amount + loss_extra
            current_balance = await db.get_balance(self.author.id)
            if total_loss > current_balance:
                total_loss = current_balance
            await db.remove_koins(self.author.id, total_loss)
            await db.add_loss(self.author.id, total_loss)
            result = (
                make_embed("error")
                .title("\U0001f4b8 Você Perdeu!")
                .desc(f"```\n\u2503 {' \u2502 '.join(current)} \u2503\n```\n\U0001f3b2 Tente novamente!")
                .field("\U0001f4b0 Apostado", f"```{formatted_bet} koins```", True)
                .field("\u26a0\ufe0f Perda Extra", f"```- {format_koins(loss_extra)} koins```", True)
                .field("\U0001f480 Total Perdido", f"```{format_koins(total_loss)} koins```", True)
                .thumb(self.author.display_avatar.url)
                .footer("Klaus Roleta")
                .timestamp()
                .build()
            )

        view = ApostarAgainView(self.author, self.amount)
        await message.edit(embed=result, view=view)


# =========================
# VIEW: Confirmar Pagamento
# =========================

class ConfirmacaoPagar(discord.ui.View):
    def __init__(self, author: discord.Member, target: discord.User, amount: int) -> None:
        super().__init__(timeout=60)
        self.author = author
        self.target = target
        self.amount = amount

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(
                embed=make_embed.error("Acesso Negado", "Essa confirmação não é para você!"),
                ephemeral=True,
            )
            return False
        return True

    @discord.ui.button(label="Confirmar", style=discord.ButtonStyle.green)
    async def confirmar(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        balance = await db.get_balance(self.author.id)
        if balance < self.amount:
            await interaction.response.edit_message(
                embed=make_embed.error("Transação Cancelada", "Saldo insuficiente."),
                view=None,
            )
            return

        await db.remove_koins(self.author.id, self.amount)
        await db.add_koins(self.target.id, self.amount)
        formatted = format_koins(self.amount)

        embed = (
            make_embed("success")
            .title("\u2705 Transferência Concluída")
            .desc(f"{self.author.mention} enviou **{formatted}** koins para {self.target.mention}")
            .field("\U0001f4b5 Valor", f"```{formatted} koins```")
            .thumb(self.author.display_avatar.url)
            .footer("Klaus Payment")
            .timestamp()
            .build()
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Cancelar", style=discord.ButtonStyle.red)
    async def cancelar(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed = make_embed.error("Transferência Cancelada", "A transação foi cancelada.")
        await interaction.response.edit_message(embed=embed, view=None)


# =========================
# VIEW: Loja Interativa
# =========================

class LojaView(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=120)

    loja_itens = {
        "escudo": ("\U0001f6e1\ufe0f Escudo", "Protege de 1 roubo", 5000, "\U0001f6e1\ufe0f"),
        "mirage": ("\U0001f3af Mirage", "+5% chance de jackpot", 15000, "\U0001f3af"),
        "diamante": ("\U0001f48e Diamante", "Vale 10.000 koins", 8000, "\U0001f48e"),
        "pacote de sorte": ("\U0001f340 Pacote de Sorte", "+10% chance de vitória", 20000, "\U0001f340"),
        "trofeu de ouro": ("\U0001f3c6 Troféu", "Item decorativo raro", 50000, "\U0001f3c6"),
        "vassoura": ("\U0001f9f9 Vassoura", "Limpa histórico de perdas", 10000, "\U0001f9f9"),
    }

    @discord.ui.select(
        placeholder="Selecione um item para comprar...",
        options=[
            discord.SelectOption(label=info[0].split(" ", 1)[1], value=key, description=f"{format_koins(info[2])} koins", emoji=info[3])
            for key, info in {
                "escudo": ("\U0001f6e1\ufe0f Escudo", "Protege de 1 roubo", 5000, "\U0001f6e1\ufe0f"),
                "mirage": ("\U0001f3af Mirage", "+5% chance de jackpot", 15000, "\U0001f3af"),
                "diamante": ("\U0001f48e Diamante", "Vale 10.000 koins", 8000, "\U0001f48e"),
                "pacote": ("\U0001f340 Pacote de Sorte", "+10% chance", 20000, "\U0001f340"),
                "trofeu": ("\U0001f3c6 Troféu", "Item raro", 50000, "\U0001f3c6"),
                "vassoura": ("\U0001f9f9 Vassoura", "Limpa perdas", 10000, "\U0001f9f9"),
            }.items()
        ],
    )
    async def select_callback(self, interaction: discord.Interaction, select: discord.ui.Select) -> None:
        item_key = select.values[0]
        item_map = {
            "escudo": ("\U0001f6e1\ufe0f Escudo", 5000),
            "mirage": ("\U0001f3af Mirage", 15000),
            "diamante": ("\U0001f48e Diamante", 8000),
            "pacote": ("\U0001f340 Pacote de Sorte", 20000),
            "trofeu": ("\U0001f3c6 Troféu de Ouro", 50000),
            "vassoura": ("\U0001f9f9 Vassoura", 10000),
        }

        if item_key not in item_map:
            return

        nome, preco = item_map[item_key]
        balance = await db.get_balance(interaction.user.id)

        if balance < preco:
            embed = make_embed.error(
                "Saldo Insuficiente",
                f"Você precisa de **{format_koins(preco)}** koins.\nSeu saldo: **{format_koins(balance)}** koins",
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        await db.remove_koins(interaction.user.id, preco)
        new_balance = await db.get_balance(interaction.user.id)

        embed = (
            make_embed("success")
            .title(f"{nome} Comprado!")
            .desc(f"Você adquiriu **{nome}** com sucesso!")
            .field("Custo", f"```{format_koins(preco)} koins```")
            .field("Saldo", f"```{format_koins(new_balance)} koins```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Shop")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)


# =========================
# ECONOMIA COG
# =========================

CHALLENGE_BUTTON_MAP = {
    "bet": ("\U0001f3b2 Apostar", "bet"),
    "mine": ("\u26cf\ufe0f Minerar", "mine"),
    "work": ("\U0001f4bc Trabalhar", "work"),
    "crime": ("\U0001f575\ufe0f Crime", "crime"),
    "feed_pet": ("\U0001f43e Alimentar Pet", "feed_pet"),
}


class ChallengeButton(discord.ui.Button):
    def __init__(self, label: str, challenge_type: str, index: int, user_id: int):
        super().__init__(label=label, style=discord.ButtonStyle.primary, custom_id=f"ch_{challenge_type}_{index}_{user_id}")
        self.challenge_type = challenge_type
        self.user_id = user_id

    async def callback(self, interaction: discord.Interaction) -> None:
        if interaction.user.id != self.user_id:
            await interaction.response.send_message(embed=make_embed.error("Acesso Negado", "Esses desafios não são seus!"), ephemeral=True)
            return
        await interaction.response.defer()

        if self.challenge_type == "bet":
            import random as _rand
            bet_amount = 500
            balance = await db.get_balance(self.user_id)
            if balance < bet_amount:
                await interaction.followup.send(
                    embed=make_embed.error("Saldo Insuficiente", "Precisa de **500 koins** para apostar!"),
                    ephemeral=True,
                )
                return
            await db.remove_koins(self.user_id, bet_amount)
            if _rand.random() < 0.45:
                won = bet_amount * 2
                await db.add_koins(self.user_id, won)
                result = f"Cara! Você ganhou **{format_koins(won)}** koins!"
            else:
                result = f"Coroa! Você perdeu **{format_koins(bet_amount)}** koins."
            await db.update_challenge_progress(self.user_id, "bet")
        elif self.challenge_type == "mine":
            import random as _rand
            reward = _rand.randint(200, 2000)
            await db.add_koins(self.user_id, reward)
            result = f"Minerou e encontrou **{format_koins(reward)}** koins!"
            await db.update_challenge_progress(self.user_id, "mine")
        elif self.challenge_type == "work":
            import random as _rand
            reward = _rand.randint(100, 1000)
            await db.add_koins(self.user_id, reward)
            result = f"Trabalhou e ganhou **{format_koins(reward)}** koins!"
            await db.update_challenge_progress(self.user_id, "work")
        elif self.challenge_type == "crime":
            import random as _rand
            if _rand.random() < 0.5:
                reward = _rand.randint(500, 3000)
                await db.add_koins(self.user_id, reward)
                result = f"Crime cometido! Ganhou **{format_koins(reward)}** koins!"
            else:
                loss = _rand.randint(200, 1500)
                await db.remove_koins(self.user_id, loss)
                result = f"Preso! Perdeu **{format_koins(loss)}** koins."
            await db.update_challenge_progress(self.user_id, "crime")
        elif self.challenge_type == "feed_pet":
            result = "Alimentou o pet! \U0001f43e"
            await db.update_challenge_progress(self.user_id, "feed_pet")
        else:
            result = "Comando não suportado ainda."

        newly = await db.update_challenge_progress(self.user_id, self.challenge_type)
        reward_text = ""
        if newly:
            for ch in newly:
                await db.add_koins(self.user_id, ch["reward"])
                reward_text += f"\n\U0001f3c6 **{ch['name']}** completo! +{format_koins(ch['reward'])} koins"

        embed = (
            make_embed("success")
            .title(f"\u2705 {self.label}")
            .desc(result)
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Challenges")
            .timestamp()
            .build()
        )
        if reward_text:
            embed.add_field(name="Desafios Completos", value=reward_text)
        await interaction.followup.send(embed=embed)


class ChallengeView(discord.ui.View):
    def __init__(self, challenges: list, completed: list, user_id: int):
        super().__init__(timeout=300)
        for i, ch in enumerate(challenges):
            if str(i) in completed:
                continue
            info = CHALLENGE_BUTTON_MAP.get(ch.get("type"))
            if info:
                self.add_item(ChallengeButton(info[0], info[1], i, user_id))

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True


class Economia(commands.Cog):
    def __init__(self, bot: KlausBot) -> None:
        self.bot = bot

    # =========================
    # /DAILY
    # =========================

    @app_commands.command(name="daily", description="Receba sua recompensa diária")
    @app_commands.checks.cooldown(1, settings.daily_cooldown_hours * 3600, key=lambda i: (i.guild_id, i.user.id))
    async def daily(self, interaction: discord.Interaction) -> None:
        amount = random.randint(settings.daily_min, settings.daily_max)
        is_premium = await db.is_premium(interaction.user.id)
        streak_data = await db.update_streak(interaction.user.id, premium=is_premium)
        streak = streak_data["streak"]

        streak_bonus = calculate_streak_bonus(streak, settings.daily_streak_bonus)

        total = amount + streak_bonus
        if is_premium:
            total *= 3
        await db.add_koins(interaction.user.id, total)
        balance = await db.get_balance(interaction.user.id)

        # Achievements
        if streak == 1:
            await db.add_achievement(interaction.user.id, "first_daily")
        if streak >= 7:
            await db.add_achievement(interaction.user.id, "streak_7")
        if streak >= 30:
            await db.add_achievement(interaction.user.id, "streak_30")
        if streak >= 100:
            await db.add_achievement(interaction.user.id, "streak_100")
        if streak >= 365:
            await db.add_achievement(interaction.user.id, "streak_365")
        if balance >= 100000:
            await db.add_achievement(interaction.user.id, "rich_100k")
        if balance >= 500000:
            await db.add_achievement(interaction.user.id, "rich_500k")
        if balance >= 1000000:
            await db.add_achievement(interaction.user.id, "rich_1m")
        if balance >= 10000000:
            await db.add_achievement(interaction.user.id, "rich_10m")
        if balance >= 100000000:
            await db.add_achievement(interaction.user.id, "rich_100m")
        if total >= 10000:
            await db.add_achievement(interaction.user.id, "big_daily")

        streak_text = f"\n\U0001f525 Sequência: **{streak} dias** (+{format_koins(streak_bonus)} bônus)" if streak > 1 else ""
        premium_text = " \U0001f451 **3x PREMIUM**" if is_premium else ""

        embed = (
            make_embed("purple")
            .title("Recompensa Diária Coletada!")
            .field("\U0001f4b5 Recebido", f"```+ {format_koins(total)} koins```")
            .field("\U0001f3e6 Saldo Atual", f"```{format_koins(balance)} koins```")
            .desc((streak_text + premium_text) if streak_text or premium_text else None)
            .thumb(interaction.user.display_avatar.url)
            .footer(f"Volte amanhã! \u2022 {interaction.user.display_name}", interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    @daily.error
    async def daily_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            retry = error.cooldown.get_retry_after()
            h, m, s = int(retry // 3600), int((retry % 3600) // 60), int(retry % 60)
            embed = make_embed.error("Cooldown Diário", f"Tente novamente em: **{h}h {m}m {s}s**")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            raise error

    # =========================
    # /STREAK
    # =========================

    @app_commands.command(name="streak", description="Veja sua sequência de daily.")
    async def streak(self, interaction: discord.Interaction) -> None:
        stats = await db.get_stats(interaction.user.id)
        streak = stats.get("daily_streak", 0)

        bar_filled = min(streak, 30)
        bar = "\U0001f525" * min(bar_filled, 10) + "\u2b55" * max(0, 10 - bar_filled)

        embed = (
            make_embed("purple")
            .title("Sua Sequência de Daily")
            .field("Sequência Atual", f"```{streak} dias```")
            .field("Próximo Bônus", f"```+{format_koins(calculate_streak_bonus(streak + 1, settings.daily_streak_bonus))} koins```")
            .desc(f"```\n{bar}\n```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Streak")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /WEEKLY
    # =========================

    @app_commands.command(name="weekly", description="Receba sua recompensa semanal")
    @app_commands.checks.cooldown(1, 7 * 24 * 3600, key=lambda i: (i.guild_id, i.user.id))
    async def weekly(self, interaction: discord.Interaction) -> None:
        is_premium = await db.is_premium(interaction.user.id)

        base = random.randint(15000, 45000)
        streak_data = await db.update_streak(interaction.user.id, premium=is_premium)
        streak = streak_data.get("streak", 0)
        streak_mult = 1.0 + min(streak * 0.02, 2.0)

        total = int(base * streak_mult)
        if is_premium:
            total = int(total * 2.5)

        await db.add_koins(interaction.user.id, total)
        balance = await db.get_balance(interaction.user.id)

        await db.add_achievement(interaction.user.id, "weekly_1")

        streak_text = f"\n🔥 Sequência: **{streak} dias** (x{streak_mult:.1f})" if streak > 1 else ""
        premium_text = " 👑 **2.5x PREMIUM**" if is_premium else ""

        embed = (
            make_embed("purple")
            .title("Recompensa Semanal Coletada!")
            .field("💵 Recebido", f"```+ {format_koins(total)} koins```")
            .field("🏦 Saldo Atual", f"```{format_koins(balance)} koins```")
            .desc(f"Próxima recompensa em **7 dias**!{streak_text}{premium_text}")
            .thumb(interaction.user.display_avatar.url)
            .footer(f"Volte na próxima semana! • {interaction.user.display_name}", interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    @weekly.error
    async def weekly_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            retry = error.cooldown.get_retry_after()
            d = int(retry // 86400)
            h = int((retry % 86400) // 3600)
            m = int((retry % 3600) // 60)
            embed = make_embed.error("Cooldown Semanal", f"Tente novamente em: **{d}d {h}h {m}m**")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            raise error

    # =========================
    # /PERFIL
    # =========================

    @app_commands.command(name="perfil", description="Veja seu perfil completo do Klaus.")
    @app_commands.checks.cooldown(1, 10, key=lambda i: i.user.id)
    async def perfil(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        user_data = await db.get_user(interaction.user.id)
        stats = await db.get_stats(interaction.user.id)
        rank = await db.get_user_rank(interaction.user.id)
        achievements = await db.get_achievements(interaction.user.id)
        balance = user_data.get("koins", 0)
        profile_data = await db.get_profile(interaction.user.id)

        rank_name = "INICIANTE"
        for threshold in sorted(settings.rank_thresholds.keys(), reverse=True):
            if balance >= threshold:
                rank_name = settings.rank_thresholds[threshold][0].split(" ", 1)[1] if " " in settings.rank_thresholds[threshold][0] else settings.rank_thresholds[threshold][0]
                break

        bg_key = profile_data.get("background", "padrao")
        border_key = profile_data.get("border", "default")
        bg_cfg = settings.profile_backgrounds.get(bg_key, settings.profile_backgrounds["padrao"])
        border_cfg = settings.profile_borders.get(border_key, settings.profile_borders["default"])

        # Level calculation from XP
        level = stats.get("level", 1)
        xp_current = stats.get("xp", 0)
        xp_next = 100 + (level - 1) * 50

        try:
            avatar_url = interaction.user.display_avatar.with_format("png").with_size(256).url
            effects = bg_cfg.get("effects", {"particles": 60, "sparkles": 10, "stripes": False, "grid": False, "glow": 1})
            profile_buf = generate_profile(
                avatar_url=avatar_url,
                username=interaction.user.display_name,
                koins=balance,
                rank_name=rank_name,
                rank_position=rank,
                wins=stats.get("wins", 0),
                losses=stats.get("losses", 0),
                streak=stats.get("daily_streak", 0),
                commands_used=stats.get("commands_used", 0),
                achievements_count=len(achievements),
                level=level,
                xp_current=xp_current,
                xp_next=xp_next,
                bg_color=bg_cfg["colors"]["bg"],
                accent_color=bg_cfg["colors"]["accent"],
                border_color=border_cfg["color"],
                effects=effects,
                theme=bg_key,
            )
            profile_buf.seek(0)
            import base64 as _b64
            img_b64 = _b64.b64encode(profile_buf.read()).decode()
            await db.save_profile_image(interaction.user.id, img_b64)
            profile_buf.seek(0)
            file = discord.File(profile_buf, filename="perfil.png")
            embed = (
                make_embed("purple")
                .title(f"Perfil de {interaction.user.display_name}")
                .image("attachment://perfil.png")
                .footer("Klaus Profile")
                .timestamp()
                .build()
            )
            view = discord.ui.View()
            view.add_item(discord.ui.Button(
                label="Customizar",
                style=discord.ButtonStyle.link,
                url="https://klaus-dashboard-delta.vercel.app/profile",
                emoji="🎨",
            ))
            message = await interaction.followup.send(embed=embed, file=file, view=view, wait=True)
        except Exception as e:
            logger.exception("Profile generation failed for user %s", interaction.user.id)
            # Fallback to text embed if image generation fails
            progress = min(int((balance / 1000000) * 20), 20)
            bar = "█" * progress + "░" * (20 - progress)
            wins = stats.get("wins", 0)
            losses = stats.get("losses", 0)
            winrate = round((wins / (wins + losses)) * 100) if (wins + losses) > 0 else 0
            embed = (
                make_embed("purple")
                .title(f"👤 Perfil de {interaction.user.display_name}")
                .thumb(interaction.user.display_avatar.url)
                .field("💰 Economia", f"Saldo: **{format_koins(balance)}**\nRank: **{rank_name}**\nPosição: **#{rank}**")
                .field("🎰 Cassino", f"Wins: **{wins}**\nLosses: **{losses}**\nWin Rate: **{winrate}%**")
                .field("📊 Atividade", f"Comandos: **{stats.get('commands_used', 0)}**\nMinerações: **{stats.get('mines', 0)}**\nSequência: **{stats.get('daily_streak', 0)} dias**")
                .field("⭐ Evolução", f"```\n{bar}\n```", False)
                .footer("Klaus Profile")
                .timestamp()
                .build()
            )
            view = discord.ui.View()
            view.add_item(discord.ui.Button(
                label="Customizar",
                style=discord.ButtonStyle.link,
                url="https://klaus-dashboard-delta.vercel.app/profile",
                emoji="🎨",
            ))
            message = await interaction.followup.send(embed=embed, view=view, wait=True)

        async def _delete_later() -> None:
            await asyncio.sleep(120)
            try:
                await message.delete()
            except discord.HTTPException:
                pass

        asyncio.create_task(_delete_later())

    # =========================
    # /CONQUISTAS
    # =========================

    @app_commands.command(name="conquistas", description="Veja todas as conquistas disponíveis.")
    async def conquistas(self, interaction: discord.Interaction) -> None:
        user_achievements = await db.get_achievements(interaction.user.id)

        lines = []
        for key, name in settings.achievements.items():
            unlocked = "\u2705" if key in user_achievements else "\u2b55"
            lines.append(f"{unlocked} {name}")

        embed = (
            make_embed("purple")
            .title(f"Conquistas \u2014 {len(user_achievements)}/{len(settings.achievements)}")
            .desc("\n".join(lines))
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Achievements")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /PAGAR
    # =========================

    @app_commands.command(name="pagar", description="Transfira koins para outro usuário")
    @app_commands.checks.cooldown(1, 3, key=lambda i: i.user.id)
    async def pagar(self, interaction: discord.Interaction, usuario: discord.User, valor: int) -> None:
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Não pode enviar koins para si mesmo!"),
                ephemeral=True,
            )
            return
        if valor <= 0:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "O valor deve ser maior que zero."),
                ephemeral=True,
            )
            return
        if usuario.bot:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Não pode enviar koins para bots!"),
                ephemeral=True,
            )
            return

        balance = await db.get_balance(interaction.user.id)
        if balance < valor:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Seu saldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )
            return

        formatted = format_koins(valor)
        embed = (
            make_embed("warning")
            .title("\u26a0\ufe0f Confirmação de Transferência")
            .desc(f"**{interaction.user.display_name}** deseja enviar **{formatted}** koins para **{usuario.display_name}**")
            .field("\U0001f4b5 Valor", f"```{formatted} koins```")
            .field("\U0001f464 Destinatário", usuario.mention)
            .thumb(usuario.display_avatar.url)
            .timestamp()
            .footer("Klaus Payment")
            .build()
        )
        view = ConfirmacaoPagar(interaction.user, usuario, valor)
        await interaction.response.send_message(embed=embed, view=view)

    # =========================
    # /TRABALHAR
    # =========================

    @app_commands.command(name="trabalhar", description="Trabalhe para ganhar koins.")
    @app_commands.checks.cooldown(1, settings.work_cooldown_hours * 3600, key=lambda i: (i.guild_id, i.user.id))
    async def trabalhar(self, interaction: discord.Interaction) -> None:
        trabalhos = [
            ("Programador", "\U0001f4bb", 1200, 15000, 0x8B5CF6),
            ("Streamer", "\U0001f3a5", 800, 4000, 0xD946EF),
            ("Designer", "\U0001f3a8", 1000, 3800, 0xEC4899),
            ("Hacker", "\U0001f5a5\ufe0f", 10000, 50000, 0x14B8A6),
            ("Entregador", "\U0001f6f5", 500, 2500, 0xF97316),
            ("Empresário", "\U0001f4bc", 2000, 6000, 0x3B82F6),
            ("Trader", "\U0001f4c8", 1000, 5500, 0x22C55E),
            ("Mecânico", "\U0001f527", 700, 3000, 0x8B5CF6),
            ("Chef", "\U0001f35c", 800, 3200, 0xEF4444),
            ("Segurança", "\U0001f6e1\ufe0f", 900, 3500, 0x2C1A4E),
        ]

        nome, emoji, minimo, maximo, cor = random.choice(trabalhos)
        salary = random.randint(minimo, maximo)
        is_premium = await db.is_premium(interaction.user.id)
        if is_premium:
            salary *= 2

        frases = [
            "Seu trabalho foi um sucesso!",
            "Expediente produtivo e recompensador.",
            "Você completou todas as tarefas!",
            "Desempenho impressionante hoje.",
            "Um dia duro, mas lucrativo.",
        ]

        frames = [
            ("\u2588\u2581\u2581\u2581\u2581\u2581\u2581\u2581\u2581\u2581", 10),
            ("\u2588\u2588\u2581\u2581\u2581\u2581\u2581\u2581\u2581\u2581", 20),
            ("\u2588\u2588\u2588\u2581\u2581\u2581\u2581\u2581\u2581\u2581", 30),
            ("\u2588\u2588\u2588\u2588\u2581\u2581\u2581\u2581\u2581\u2581", 40),
            ("\u2588\u2588\u2588\u2588\u2588\u2581\u2581\u2581\u2581\u2581", 50),
            ("\u2588\u2588\u2588\u2588\u2588\u2588\u2581\u2581\u2581\u2581", 60),
            ("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2581\u2581\u2581", 70),
            ("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2581\u2581", 80),
            ("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2581", 90),
            ("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", 100),
        ]

        embed = (
            make_embed(cor)
            .title(f"{emoji} Trabalhando como {nome}...")
            .field("\U0001f464 Funcionário", interaction.user.mention)
            .field("\U0001f4bc Profissão", f"```{nome}```")
            .field("\U0001f4b5 Salário", f"```{format_koins(salary)} koins```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Work System \u2022 Aguarde...")
            .timestamp()
            .build()
        )

        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        for barra, pct in frames:
            loading = (
                make_embed(cor)
                .title(f"{emoji} Trabalhando como {nome}...")
                .field("\U0001f4ca Progresso", f"```{barra} {pct}%```")
                .field("\U0001f4bc Profissão", f"```{nome}```")
                .field("\U0001f4b5 Salário", f"```{format_koins(salary)} koins```")
                .thumb(interaction.user.display_avatar.url)
                .footer("Klaus Work System \u2022 Trabalhando...")
                .timestamp()
                .build()
            )
            try:
                await message.edit(embed=loading)
            except discord.HTTPException:
                return
            await asyncio.sleep(1)

        await db.add_koins(interaction.user.id, salary)
        if is_premium:
            await db.add_achievement(interaction.user.id, "premium_worker")

        # Track work count for achievements
        user_data = await db.get_user(interaction.user.id)
        work_count = user_data.get("stats", {}).get("work_count", 0) + 1
        await db.update_user(interaction.user.id, {"$set": {"stats.work_count": work_count}})
        if work_count >= 100:
            await db.add_achievement(interaction.user.id, "work_100")
        if work_count >= 500:
            await db.add_achievement(interaction.user.id, "work_500")

        balance = await db.get_balance(interaction.user.id)

        final = (
            make_embed("success")
            .title(f"{emoji} Expediente Finalizado!" + (" \U0001f451 2x PREMIUM" if is_premium else ""))
            .field("\U0001f4bc Profissão", f"```{nome}```")
            .field("\U0001f4b5 Salário", f"```+ {format_koins(salary)} koins```")
            .field("\U0001f3e6 Saldo", f"```{format_koins(balance)} koins```")
            .field("\U0001f4cb Relatório", random.choice(frases))
            .field("\U0001f4ca Status", "```[\u2588\u2588\u2588\u2588\u2588] 100%```")
            .thumb(interaction.user.display_avatar.url)
            .footer(f"Funcionário: {interaction.user.display_name}", interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )

        try:
            await message.edit(embed=final)
        except discord.HTTPException:
            return

        await asyncio.sleep(60)
        try:
            await message.delete()
        except discord.HTTPException:
            pass

    @trabalhar.error
    async def trabalhar_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            retry = error.retry_after
            h, m, s = int(retry // 3600), int((retry % 3600) // 60), int(retry % 60)
            embed = make_embed.error("Cooldown", f"Volte em: **{h}h {m}m {s}s**")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            raise error

    # =========================
    # /APOSTAR
    # =========================

    @app_commands.command(name="apostar", description="Aposte seus koins em uma roleta.")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def apostar(self, interaction: discord.Interaction, valor: int) -> None:
        user_id = interaction.user.id
        balance = await db.get_balance(user_id)

        if valor <= 0:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Valor deve ser maior que zero."), ephemeral=True
            )
            return
        if balance < valor:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )
            return

        stats = await db.get_stats(user_id)
        jackpot_chance = settings.jackpot_base_chance
        big_bet = valor >= settings.big_bet_threshold

        if stats["easy_wins"] >= 3 and big_bet:
            jackpot_chance = 1
        elif stats["easy_wins"] >= 2 and big_bet:
            jackpot_chance = 3
        elif stats["easy_wins"] >= 1 and big_bet:
            jackpot_chance = 7
        if stats["profit"] >= 100000:
            jackpot_chance = max(1, jackpot_chance - 5)
        if stats["big_losses"] >= 1:
            jackpot_chance += 4

        slots = ["\U0001f352", "\U0001f34b", "\U0001f48e", "\U0001f340", "\u0037\u20e3", "\u2b50", "\U0001f525", "\U0001f451", "\U0001f4b0", "\U0001f3b2", "\U0001fa99", "\u26a1", "\U0001f347", "\U0001f976", "\U0001f3af"]

        is_jackpot = random.randint(1, 100) <= jackpot_chance
        if is_jackpot:
            symbol = random.choice(slots)
            final = [symbol, symbol, symbol]
        else:
            final = [random.choice(slots) for _ in range(3)]
            while final[0] == final[1] == final[2]:
                final = [random.choice(slots) for _ in range(3)]

        formatted_bet = format_koins(valor)

        embed = (
            make_embed("purple")
            .title("\U0001f3b0 Roleta Klaus")
            .desc(f"```\n\u2503 \u2753 \u2502 \u2753 \u2502 \u2753 \u2503\n```\nApostado: **{formatted_bet}** koins")
            .thumb(interaction.user.display_avatar.url)
            .footer("Roleta Klaus \u2022 Girando...")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()
        current = ["\u2753", "\u2753", "\u2753"]

        slot_names = ["Primeiro", "Segundo", "Último"]
        colors = [0xE74C3C, 0xE67E22, 0xF1C40F]

        for i in range(3):
            for _ in range(6):
                for j in range(i, 3):
                    current[j] = random.choice(slots)
                spinning = (
                    make_embed(colors[i])
                    .title("\U0001f3b0 Roleta Klaus")
                    .desc(f"```\n\u2503 {' \u2502 '.join(current)} \u2503\n```\nGirando: **{slot_names[i]}** slot...")
                    .thumb(interaction.user.display_avatar.url)
                    .footer("Roleta Klaus \u2022 Girando...")
                    .timestamp()
                    .build()
                )
                await message.edit(embed=spinning)
                await asyncio.sleep(0.5)
            current[i] = final[i]

        if current[0] == current[1] == current[2]:
            bonus = random.randint(settings.jackpot_bonus_min, settings.jackpot_bonus_max)
            total_won = valor + bonus
            await db.add_koins(user_id, total_won)
            await db.add_win(user_id, total_won)
            await db.add_achievement(user_id, "jackpot")

            extra = "\n\n\U0001f575\ufe0f O cassino monitora sua sorte..." if big_bet and stats["easy_wins"] >= 2 else ""

            result = (
                make_embed("gold")
                .title("\U0001f48e JACKPOT!")
                .desc(f"```\n\u2503 {' \u2502 '.join(current)} \u2503\n```\n\U0001f389 **3 símbolos iguais!**{extra}")
                .field("\U0001f4b0 Apostado", f"```{formatted_bet} koins```", True)
                .field("\u2728 Bônus", f"```+ {format_koins(bonus)} koins```", True)
                .field("\U0001f3c6 Total", f"```{format_koins(total_won)} koins```", True)
                .thumb(interaction.user.display_avatar.url)
                .footer(f"Apostador: {interaction.user.display_name}", interaction.user.display_avatar.url)
                .timestamp()
                .build()
            )
        else:
            loss_extra = random.randint(settings.loss_extra_min, settings.loss_extra_max)
            total_loss = valor + loss_extra
            current_balance = await db.get_balance(user_id)
            if total_loss > current_balance:
                total_loss = current_balance
            await db.remove_koins(user_id, total_loss)
            await db.add_loss(user_id, total_loss)

            extra = "\n\n\U0001f480 A ganância cobrou!" if big_bet else ""

            result = (
                make_embed("error")
                .title("\U0001f4b8 Você Perdeu!")
                .desc(f"```\n\u2503 {' \u2502 '.join(current)} \u2503\n```\n\U0001f3b2 Tente novamente!{extra}")
                .field("\U0001f4b0 Apostado", f"```{formatted_bet} koins```", True)
                .field("\u26a0\ufe0f Perda Extra", f"```- {format_koins(loss_extra)} koins```", True)
                .field("\U0001f480 Total Perdido", f"```{format_koins(total_loss)} koins```", True)
                .thumb(interaction.user.display_avatar.url)
                .footer(f"Apostador: {interaction.user.display_name}", interaction.user.display_avatar.url)
                .timestamp()
                .build()
            )

        await message.edit(embed=result)
        view = ApostarAgainView(interaction.user, valor)
        await message.edit(view=view)

    # =========================
    # /ROUBAR
    # =========================

    @app_commands.command(name="roubar", description="Roube koins de alguém.")
    @app_commands.checks.cooldown(1, settings.rob_cooldown_hours * 3600, key=lambda i: (i.guild_id, i.user.id))
    async def roubar(self, interaction: discord.Interaction, member: discord.Member) -> None:
        if member.bot:
            await interaction.response.send_message(embed=make_embed.error("Erro", "Não pode roubar bots!"), ephemeral=True)
            return
        if member.id == interaction.user.id:
            await interaction.response.send_message(embed=make_embed.error("Erro", "Não pode roubar a si mesmo!"), ephemeral=True)
            return

        target_balance = await db.get_balance(member.id)
        if target_balance <= 0:
            await interaction.response.send_message(
                embed=make_embed.error("Alvo Sem Koins", f"{member.mention} não possui koins."),
                ephemeral=True,
            )
            return

        amount = random.randint(settings.rob_min_amount, settings.rob_max_amount)
        is_premium = await db.is_premium(interaction.user.id)
        if is_premium:
            amount *= 2
        success_chance = settings.rob_success_chance + (15 if is_premium else 0)
        success = random.randint(1, 100) <= success_chance
        fail_pct = random.randint(5, 95)

        embed = (
            make_embed("error")
            .title("\U0001f9b9 Invasão em Andamento")
            .desc(f"**Alvo:** {member.mention}\n**Saldo:** {format_koins(target_balance)} koins\n\n```\n[\u25a1\u25a1\u25a1\u25a1\u25a1\u25a1\u25a1\u25a1\u25a1\u25a1] 0%\n```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Rob System \u2022 Infiltrando...")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        for pct in range(0, 101, 10):
            if not success and pct >= fail_pct:
                barra = "\u2588" * (pct // 10) + "\u25a1" * (10 - (pct // 10))
                fail = (
                    make_embed("error")
                    .title("\U0001f6a8 Roubo Interrompido!")
                    .desc(f"**Alvo:** {member.mention}\n\n```\n[{barra}] {pct}%\n```\n\U0001f6d1 Você foi detectado!")
                    .thumb(interaction.user.display_avatar.url)
                    .footer("Klaus Rob System \u2022 Falhou!")
                    .timestamp()
                    .build()
                )
                await message.edit(embed=fail)
                return

            barra = "\u2588" * (pct // 10) + "\u25a1" * (10 - (pct // 10))
            loading = (
                make_embed("warning")
                .title("\U0001f9b9 Invasão em Andamento")
                .desc(f"**Alvo:** {member.mention}\n\n```\n[{barra}] {pct}%\n```")
                .thumb(interaction.user.display_avatar.url)
                .footer("Klaus Rob System \u2022 Infiltrando...")
                .timestamp()
                .build()
            )
            await message.edit(embed=loading)
            await asyncio.sleep(0.5)

        if amount > target_balance:
            amount = target_balance

        await db.remove_koins(member.id, amount)
        await db.add_koins(interaction.user.id, amount)
        await db.add_achievement(interaction.user.id, "first_rob")

        barra_final = "\u2588" * 10
        success_embed = (
            make_embed("success")
            .title("\U0001f4b0 Roubo Concluído!")
            .desc(f"**Alvo:** {member.mention}\n\n```\n[{barra_final}] 100%\n```\n\U0001f3ad {interaction.user.mention} roubou **{format_koins(amount)}** koins!")
            .thumb(interaction.user.display_avatar.url)
            .footer("Roubo realizado!", interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )
        await message.edit(embed=success_embed)

    @roubar.error
    async def roubar_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            retry = error.retry_after
            h, m, s = int(retry // 3600), int((retry % 3600) // 60), int(retry % 60)
            embed = make_embed.error("Cooldown", f"Tente em: **{h}h {m}m {s}s**")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            raise error

    # =========================
    # /SALDO
    # =========================

    @app_commands.command(name="saldo", description="Veja sua quantidade de koins.")
    async def saldo(self, interaction: discord.Interaction) -> None:
        balance = await db.get_balance(interaction.user.id)
        formatted = format_koins(balance)
        rank = await db.get_user_rank(interaction.user.id)

        rank_name = "\U0001fa99 INICIANTE"
        for threshold in sorted(settings.rank_thresholds.keys(), reverse=True):
            if balance >= threshold:
                rank_name = settings.rank_thresholds[threshold][0]
                break

        embed = (
            make_embed("gold")
            .title("Saldo")
            .field("\U0001f3e6 Koins", f"```{formatted} koins```")
            .field("\U0001f3c6 Rank", f"```{rank_name}```")
            .field("\U0001f4ca Posicao", f"```#{rank}```")
            .thumb(interaction.user.display_avatar.url)
            .footer(f"Saldo de {interaction.user.display_name}")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /CARTEIRA
    # =========================

    @app_commands.command(name="carteira", description="Veja sua carteira completa.")
    async def carteira(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        balance = await db.get_balance(interaction.user.id)
        stats = await db.get_stats(interaction.user.id)
        rank = await db.get_user_rank(interaction.user.id)

        wins = stats.get("wins", 0)
        losses = stats.get("losses", 0)
        profit = stats.get("profit", 0)
        total_games = wins + losses
        taxa = round((wins / total_games) * 100) if total_games > 0 else 0

        rank_name = "\U0001fa99 INICIANTE"
        rank_cor = 0x95A5A6
        for threshold in sorted(settings.rank_thresholds.keys(), reverse=True):
            if balance >= threshold:
                rank_name, rank_cor = settings.rank_thresholds[threshold]
                break

        progress = min(int((balance / 1000000) * 15), 15)
        barra = "\u2588" * progress + "\u25a1" * (15 - progress)

        embed = (
            make_embed(rank_cor)
            .title("\U0001f3e6 Carteira Klaus")
            .field("\U0001f464 Usuário", interaction.user.mention)
            .field(
                "\U0001f4b0 Economia",
                f"\U0001f4b5 Saldo: **{format_koins(balance)}**\n"
                f"\U0001f4c8 Lucro: **{format_koins(profit)}**\n"
                f"\U0001f3c6 Rank: **{rank_name}**\n"
                f"\U0001f4ca Posição: **#{rank}**",
            )
            .field(
                "\U0001f3b0 Cassino",
                f"\u2705 Wins: **{wins}**\n\u274c Losses: **{losses}**\n\U0001f4ca Win Rate: **{taxa}%**",
            )
            .field("\U0001f4ca Evolução", f"```\n[{barra}]\n```", False)
            .thumb(interaction.user.display_avatar.url)
            .footer(f"Klaus Carteira \u2022 {interaction.user.display_name}", interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )

        message = await interaction.followup.send(embed=embed, wait=True)

        async def _delete_later() -> None:
            await asyncio.sleep(60)
            try:
                await message.delete()
            except discord.HTTPException:
                pass

        asyncio.create_task(_delete_later())

    # =========================
    # /RANKING
    # =========================

    @app_commands.command(name="ranking", description="Veja o ranking dos mais ricos.")
    async def ranking(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()

        data = await db.get_leaderboard_page(1, 10)
        entries = data["entries"]
        user_rank = await db.get_user_rank(interaction.user.id)

        medals = ["\U0001f947", "\U0001f948", "\U0001f949"]
        lines = []
        for entry in entries:
            try:
                user = await self.bot.fetch_user(entry["discord_id"])
                name = user.display_name
            except discord.NotFound:
                name = f"ID: {entry['discord_id']}"
            medal = medals[entry["rank"] - 1] if entry["rank"] <= 3 else f"`#{entry['rank']}`"
            lines.append(f"{medal} **{name}** \u2014 {format_koins(entry['koins'])} koins")

        embed = (
            make_embed("purple")
            .title("Ranking \u2014 Top 10 Mais Ricos")
            .desc("\n".join(lines))
            .field("Sua Posição", f"```#{user_rank}```")
            .thumb(interaction.guild.icon.url if interaction.guild and interaction.guild.icon else self.bot.user.display_avatar.url)
            .footer(f"Solicitado por {interaction.user.display_name}")
            .timestamp()
            .build()
        )
        await interaction.followup.send(embed=embed)

    # =========================
    # /LOJA
    # =========================

    @app_commands.command(name="loja", description="Veja os itens disponíveis na loja.")
    async def loja(self, interaction: discord.Interaction) -> None:
        embed = (
            make_embed("purple")
            .title("Loja Klaus")
            .desc("Selecione um item no menu abaixo para comprar!")
            .field("\U0001f6e1\ufe0f Escudo", "```5.000 koins``` Protege de 1 roubo")
            .field("\U0001f3af Mirage", "```15.000 koins``` +5% jackpot")
            .field("\U0001f48e Diamante", "```8.000 koins``` Vale 10K koins")
            .field("\U0001f340 Pacote de Sorte", "```20.000 koins``` +10% vitória")
            .field("\U0001f3c6 Troféu", "```50.000 koins``` Item raro")
            .field("\U0001f9f9 Vassoura", "```10.000 koins``` Limpa perdas")
            .thumb(self.bot.user.display_avatar.url)
            .footer("Loja Klaus \u2022 Itens limitados!")
            .timestamp()
            .build()
        )
        view = LojaView()
        await interaction.response.send_message(embed=embed, view=view)

    # =========================
    # /MINERAR
    # =========================

    @app_commands.command(name="minerar", description="Minere koins e minérios raros.")
    @app_commands.checks.cooldown(1, 1800, key=lambda i: (i.guild_id, i.user.id))
    async def minerar(self, interaction: discord.Interaction) -> None:
        minerais = [
            ("\u26cf\ufe0f Carvão", 50, 300, 0x555555),
            ("\U0001f48e Diamante", 500, 3000, 0x00BCD4),
            ("\U0001f9f2 Ferro", 100, 800, 0x9E9E9E),
            ("\u2b50 Ouro", 300, 2000, 0xFFD700),
            ("\U0001f48e Esmeralda", 800, 5000, 0x2ECC71),
        ]

        nome, minimo, maximo, cor = random.choice(minerais)
        amount = random.randint(minimo, maximo)

        embed = (
            make_embed("dark")
            .title("\u26cf\ufe0f Minerando...")
            .desc("```\nProcurando minérios...\n```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Mining")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        frames = ["\u2588\u2581\u2581\u2581\u2581\u2581\u2581\u2581\u2581\u2581", "\u2588\u2588\u2588\u2581\u2581\u2581\u2581\u2581\u2581\u2581", "\u2588\u2588\u2588\u2588\u2588\u2581\u2581\u2581\u2581\u2581", "\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2581\u2581\u2581", "\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588"]

        for i, frame in enumerate(frames):
            pct = (i + 1) * 20
            loading = (
                make_embed("dark")
                .title("\u26cf\ufe0f Minerando...")
                .desc(f"```\n{frame} {pct}%\n```")
                .thumb(interaction.user.display_avatar.url)
                .footer("Klaus Mining")
                .timestamp()
                .build()
            )
            try:
                await message.edit(embed=loading)
            except discord.HTTPException:
                return
            await asyncio.sleep(0.8)

        await db.add_koins(interaction.user.id, amount)
        await db.add_mine(interaction.user.id)
        balance = await db.get_balance(interaction.user.id)

        final = (
            make_embed(cor)
            .title(f"{nome} Encontrado!")
            .desc(f"```\nMineração completa!\n```\nVocê encontrou **{nome}** e ganhou **{format_koins(amount)}** koins!")
            .field("\U0001f4b0 Ganho", f"```+ {format_koins(amount)} koins```")
            .field("\U0001f3e6 Saldo", f"```{format_koins(balance)} koins```")
            .thumb(interaction.user.display_avatar.url)
            .footer(f"Minerador: {interaction.user.display_name}")
            .timestamp()
            .build()
        )

        try:
            await message.edit(embed=final)
        except discord.HTTPException:
            pass

    @minerar.error
    async def minerar_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            retry = error.retry_after
            m, s = int((retry % 3600) // 60), int(retry % 60)
            embed = make_embed.error("Cooldown", f"Volte em: **{m}m {s}s**")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            raise error

    # =========================
    # /COINFLIP
    # =========================

    @app_commands.command(name="coinflip", description="Aposte em cara ou coroa!")
    @app_commands.describe(valor="Quantidade de koins para apostar")
    async def coinflip(self, interaction: discord.Interaction, valor: int) -> None:
        if valor <= 0:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Valor deve ser maior que zero."), ephemeral=True
            )
            return
        balance = await db.get_balance(interaction.user.id)
        if balance < valor:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )
            return

        embed = (
            make_embed("purple")
            .title("\U0001fa99 Coinflip")
            .desc(f"Aposte **{format_koins(valor)}** koins em **Cara** ou **Coroa**!")
            .field("Escolha", "Clique em um botão abaixo")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .footer("Klaus Coinflip")
            .build()
        )
        view = CoinflipView(interaction.user, valor)
        await interaction.response.send_message(embed=embed, view=view)

    # =========================
    # /DADOS
    # =========================

    @app_commands.command(name="aposta_dados", description="Aposte nos dados! Menor, meio ou maior.")
    @app_commands.describe(valor="Quantidade de koins para apostar")
    async def dados(self, interaction: discord.Interaction, valor: int) -> None:
        if valor <= 0:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Valor deve ser maior que zero."), ephemeral=True
            )
            return
        balance = await db.get_balance(interaction.user.id)
        if balance < valor:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )
            return

        embed = (
            make_embed("purple")
            .title("\U0001f3b2 Dados Klaus")
            .desc(f"Aposte **{format_koins(valor)}** koins!")
            .field("Menor (2-6)", "```x2```")
            .field("Meio (7-10)", "```x3```")
            .field("Maior (11-12)", "```x2```")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .footer("Klaus Dice")
            .build()
        )
        view = DiceView(interaction.user, valor)
        await interaction.response.send_message(embed=embed, view=view)

    # =========================
    # /BLACKJACK
    # =========================

    @app_commands.command(name="blackjack", description="Jogue blackjack contra o dealer!")
    @app_commands.describe(valor="Quantidade de koins para apostar")
    async def blackjack(self, interaction: discord.Interaction, valor: int) -> None:
        if valor <= 0:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Valor deve ser maior que zero."), ephemeral=True
            )
            return
        balance = await db.get_balance(interaction.user.id)
        if balance < valor:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )
            return

        suits = ["\u2660", "\u2665", "\u2666", "\u2663"]
        ranks = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]

        def deal():
            return f"{random.choice(ranks)}{random.choice(suits)}"

        player = [deal(), deal()]
        dealer = [deal(), deal()]

        pv = BlackjackView._hand_value(player)

        if pv == 21:
            bonus = valor // 2
            total = valor + bonus
            await db.add_koins(interaction.user.id, total)
            bal = await db.get_balance(interaction.user.id)
            embed = (
                make_embed("gold")
                .title("\U0001f0cf Blackjack \u2014 BLACKJACK!")
                .desc(f"**21 pontos!** Você ganhou **{format_koins(total)}** koins!")
                .field("Sua Mão", f"```{' '.join(player)}```")
                .field("Dealer", f"```{' '.join(dealer)}```")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(interaction.user.display_avatar.url)
                .footer("Klaus Blackjack")
                .timestamp()
                .build()
            )
            await interaction.response.send_message(embed=embed)
            return

        embed = (
            make_embed("purple")
            .title("\U0001f0cf Blackjack")
            .field("Dealer", f"```{dealer[0]} \U0001f0cf```")
            .field(f"Você ({pv} points)", f"```{' '.join(player)}```")
            .field("Aposta", f"```{format_koins(valor)} koins```")
            .field("Ações", "Pedir, Parar ou Dobrar a aposta!")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .footer("Klaus Blackjack")
            .build()
        )
        view = BlackjackView(interaction.user, valor, player, dealer)
        await interaction.response.send_message(embed=embed, view=view)

    # =========================
    # /DUEL
    # =========================

    @app_commands.command(name="duel", description="Desafie alguém para um duelo de koins!")
    @app_commands.describe(adversario="O jogador que você quer desafiar", valor="Quantidade de koins para apostar")
    async def duel(self, interaction: discord.Interaction, adversario: discord.Member, valor: int) -> None:
        if adversario.id == interaction.user.id:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Não pode desafiar a si mesmo!"), ephemeral=True
            )
            return
        if adversario.bot:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Não pode desafiar bots!"), ephemeral=True
            )
            return
        if valor <= 0:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Valor deve ser maior que zero."), ephemeral=True
            )
            return

        balance = await db.get_balance(interaction.user.id)
        if balance < valor:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )
            return

        embed = (
            make_embed("warning")
            .title("\u2694\ufe0f Desafio de Duelo!")
            .desc(f"**{interaction.user.display_name}** desafiou **{adversario.display_name}**!")
            .field("Aposta", f"```{format_koins(valor)} koins```")
            .field("Regras", "50/50 chance. O ganhador leva tudo!")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .footer("Klaus Duel")
            .build()
        )
        view = DuelRequestView(interaction.user, adversario, valor)
        await interaction.response.send_message(content=adversario.mention, embed=embed, view=view)

    @duel.error
    async def duel_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        await interaction.response.send_message(
            embed=make_embed.error("Erro", str(error)), ephemeral=True
        )

    # =========================
    # /MINERAR
    # =========================
    # /FORJAR
    # =========================

    @app_commands.command(name="forjar", description="Forje itens raros combinando minérios.")
    @app_commands.describe(item="Nome do item que deseja forjar")
    async def forjar(self, interaction: discord.Interaction, item: str) -> None:
        receitas = {
            "escudo": {"preco": 2000, "emoji": "\U0001f6e1\ufe0f", "desc": "3 Carvão + 2 Ferro"},
            "espada": {"preco": 5000, "emoji": "\u2694\ufe0f", "desc": "5 Ferro + 1 Ouro"},
            "coroa": {"preco": 15000, "emoji": "\U0001f451", "desc": "3 Ouro + 2 Diamante"},
        }

        key = item.lower()
        if key not in receitas:
            desc = "\n".join(f"- `/forjar {k}` \u2014 {v['emoji']} {v['desc']}" for k, v in receitas.items())
            await interaction.response.send_message(
                embed=make_embed.error("Receita Não Encontrada", f"**Receitas:**\n{desc}"),
                ephemeral=True,
            )
            return

        receita = receitas[key]
        balance = await db.get_balance(interaction.user.id)
        if balance < receita["preco"]:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Custo: **{format_koins(receita['preco'])}** koins\nSaldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )
            return

        await db.remove_koins(interaction.user.id, receita["preco"])
        new_balance = await db.get_balance(interaction.user.id)

        embed = (
            make_embed("orange")
            .title(f"{receita['emoji']} Item Forjado!")
            .desc(f"Você forjou um **{item.title()}**!")
            .field("Custo", f"```{format_koins(receita['preco'])} koins```")
            .field("Saldo", f"```{format_koins(new_balance)} koins```")
            .thumb(interaction.user.display_avatar.url)
            .footer(f"Forjado por {interaction.user.display_name}")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    @forjar.error
    async def forjar_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            retry = error.retry_after
            m, s = int((retry % 3600) // 60), int(retry % 60)
            embed = make_embed.error("Forja Esfriando", f"Forje em: **{m}m {s}s**")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            raise error

    # =========================
    # /COFRE
    # =========================

    @app_commands.command(name="cofre", description="Sua poupança segura com juros!")
    async def cofre(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()
        cofre = await db.get_cofre(interaction.user.id)
        balance = await db.get_balance(interaction.user.id)

        interest = int(cofre["balance"] * 0.02)

        embed = (
            make_embed("purple")
            .title(f"\U0001f3e6 Cofre de {interaction.user.display_name}")
            .field("\U0001f4b5 Saldo no Cofre", f"```{format_koins(cofre['balance'])} koins```")
            .field("\U0001f4b0 Saldo Carteira", f"```{format_koins(balance)} koins```")
            .field("\U0001f4c8 Juros (2%)", f"```+ {format_koins(interest)} koins/hora```")
            .field("\U0001f4ca Total Depositado", f"```{format_koins(cofre['total_deposited'])} koins```")
            .field("\U0001f4b5 Juros Ganhos", f"```{format_koins(cofre['interest_earned'])} koins```")
            .desc("Use `/cofre_deposit` e `/cofre_withdraw` para gerenciar.")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Cofre \u2022 Seu dinheiro rende 2% por hora!")
            .timestamp()
            .build()
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="cofre_deposit", description="Deposite koins no cofre (rende juros!)")
    @app_commands.describe(valor="Quantidade para depositar (ou 'tudo' para tudo)")
    async def cofre_deposit(self, interaction: discord.Interaction, valor: str) -> None:
        balance = await db.get_balance(interaction.user.id)
        if valor.lower() == "tudo":
            amount = balance
        else:
            try:
                amount = int(valor)
            except ValueError:
                await interaction.response.send_message(
                    embed=make_embed.error("Erro", "Use um número ou `tudo`."), ephemeral=True
                )
                return

        if amount <= 0:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Valor deve ser maior que zero."), ephemeral=True
            )
            return
        if balance < amount:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )
            return

        result = await db.deposit_cofre(interaction.user.id, amount)
        if not result["ok"]:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", result["error"]), ephemeral=True
            )
            return

        await db.add_achievement(interaction.user.id, "cofre_100k")
        if result["cofre"]["balance"] >= 500000:
            await db.add_achievement(interaction.user.id, "cofre_500k")
        if result["cofre"]["balance"] >= 1000000:
            await db.add_achievement(interaction.user.id, "cofre_1m")

        embed = (
            make_embed("success")
            .title("\U0001f4b0 Depositado no Cofre!")
            .field("Depositado", f"```+ {format_koins(amount)} koins```")
            .field("Cofre", f"```{format_koins(result['cofre']['balance'])} koins```")
            .field("Rendimento", f"```2% por hora```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Cofre")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="cofre_withdraw", description="Retire koins do cofre")
    @app_commands.describe(valor="Quantidade para retirar (ou 'tudo' para tudo)")
    async def cofre_withdraw(self, interaction: discord.Interaction, valor: str) -> None:
        cofre = await db.get_cofre(interaction.user.id)
        if valor.lower() == "tudo":
            amount = cofre["balance"]
        else:
            try:
                amount = int(valor)
            except ValueError:
                await interaction.response.send_message(
                    embed=make_embed.error("Erro", "Use um número ou `tudo`."), ephemeral=True
                )
                return

        if amount <= 0:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Valor deve ser maior que zero."), ephemeral=True
            )
            return
        if cofre["balance"] < amount:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Cofre: **{format_koins(cofre['balance'])}** koins"),
                ephemeral=True,
            )
            return

        result = await db.withdraw_cofre(interaction.user.id, amount)
        if not result["ok"]:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", result["error"]), ephemeral=True
            )
            return

        embed = (
            make_embed("success")
            .title("\U0001f4b5 Retirado do Cofre!")
            .field("Retirado", f"```- {format_koins(amount)} koins```")
            .field("Cofre", f"```{format_koins(result['cofre']['balance'])} koins```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Cofre")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /CRIME
    # =========================

    @app_commands.command(name="crime", description="Cometa um crime e arrisque ser preso!")
    @app_commands.checks.cooldown(1, 1800, key=lambda i: (i.guild_id, i.user.id))
    async def crime(self, interaction: discord.Interaction) -> None:
        jail = await db.is_in_jail(interaction.user.id)
        if jail["jailed"]:
            mins = jail["remaining_seconds"] // 60
            await interaction.response.send_message(
                embed=make_embed.error("Preso!", f"Você está preso por mais **{mins} minutos**!"),
                ephemeral=True,
            )
            return

        balance = await db.get_balance(interaction.user.id)
        if balance < 100:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", "Precisa de pelo menos 100 koins."),
                ephemeral=True,
            )
            return

        crimes = [
            ("Roubar um Banco", "\U0001f3e6", 5000, 50000),
            ("Hackear o Discord", "\U0001f5a5\ufe0f", 3000, 30000),
            ("Vender Informações", "\U0001f4dd", 1000, 15000),
            ("Sequestrar o Presidente", "\U0001f469\u200d\U0001f454", 8000, 80000),
            ("Tráfico de Koins", "\U0001f4b5", 2000, 20000),
            ("Invasão Cibernética", "\U0001f4bb", 1500, 18000),
            ("Assalto à Mão Armada", "\U0001f52b", 3000, 25000),
        ]

        nome, emoji, minimo, maximo = random.choice(crimes)
        success = random.randint(1, 100) <= 40

        embed = (
            make_embed("warning")
            .title(f"{emoji} Crime em Andamento...")
            .desc(f"**{interaction.user.display_name}** está tentando: **{nome}**")
            .field("Status", "```Investigando...```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Crime System \u2022 Não faça isso em casa!")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        frames = ["\u2581", "\u2582", "\u2583", "\u2584", "\u2585", "\u2586", "\u2587", "\u2588"]
        for i, f in enumerate(frames):
            barra = "\u2588" * (i + 1) + "\u25a1" * (7 - i)
            pct = (i + 1) * 12
            loading = (
                make_embed("warning")
                .title(f"{emoji} Crime em Andamento...")
                .desc(f"**{interaction.user.display_name}** está tentando: **{nome}**")
                .field("Progresso", f"```[{barra}] {pct}%```")
                .thumb(interaction.user.display_avatar.url)
                .footer("Klaus Crime System \u2022 Investigando...")
                .timestamp()
                .build()
            )
            try:
                await message.edit(embed=loading)
            except discord.HTTPException:
                return
            await asyncio.sleep(0.8)

        if success:
            amount = random.randint(minimo, maximo)
            await db.add_koins(interaction.user.id, amount)
            await db.add_crime(interaction.user.id)
            bal = await db.get_balance(interaction.user.id)

            crimes_count = await db.get_crimes(interaction.user.id)
            if crimes_count == 1:
                await db.add_achievement(interaction.user.id, "first_crime")
            if crimes_count >= 10:
                await db.add_achievement(interaction.user.id, "crime_10")
            if crimes_count >= 50:
                await db.add_achievement(interaction.user.id, "crime_50")
            if crimes_count >= 100:
                await db.add_achievement(interaction.user.id, "crime_100")

            result = (
                make_embed("success")
                .title(f"{emoji} Crime Bem-Sucedido!")
                .desc(f"**{interaction.user.display_name}** completou: **{nome}**!")
                .field("Recompensa", f"```+ {format_koins(amount)} koins```")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(interaction.user.display_avatar.url)
                .footer("Klaus Crime")
                .timestamp()
                .build()
            )
        else:
            fine = random.randint(500, 5000)
            current = await db.get_balance(interaction.user.id)
            if fine > current:
                fine = current
            await db.remove_koins(interaction.user.id, fine)
            jail_time = random.randint(10, 30)
            await db.add_jail(interaction.user.id, jail_time)
            bal = await db.get_balance(interaction.user.id)

            result = (
                make_embed("error")
                .title(f"\U0001f6a8 Crime Falhou!")
                .desc(f"**{interaction.user.display_name}** foi pego tentando: **{nome}**!")
                .field("Multa", f"```- {format_koins(fine)} koins```")
                .field("Prisão", f"```{jail_time} minutos```")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(interaction.user.display_avatar.url)
                .footer("Klaus Crime")
                .timestamp()
                .build()
            )

        try:
            await message.edit(embed=result)
        except discord.HTTPException:
            pass

    @crime.error
    async def crime_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            retry = error.retry_after
            m, s = int((retry % 3600) // 60), int(retry % 60)
            embed = make_embed.error("Cooldown", f"Volte em: **{m}m {s}s**")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            raise error

    # =========================
    # /LOTTERY
    # =========================

    @app_commands.command(name="lottery", description="Compre um ticket da loteria! Número aleatório 1-100.")
    async def lottery(self, interaction: discord.Interaction) -> None:
        pool = await db.get_lottery_pool()
        result = await db.buy_lottery_ticket(interaction.user.id, 500)

        if not result["ok"]:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", result["error"]), ephemeral=True
            )
            return

        await db.add_achievement(interaction.user.id, "lottery_win")

        embed = (
            make_embed("purple")
            .title("\U0001f3b0 Loteria Klaus")
            .desc(f"Seu número: **{result['number']}**")
            .field("Premio Acumulado", f"```{format_koins(pool + 500)} koins```")
            .field("Custo", "```500 koins```")
            .field("Como Ganhar", "O bot sorteia um número de 1-100.\nSe o seu número for sorteado, você ganha o prêmio acumulado!")
            .thumb(interaction.user.display_avatar.url)
            .footer("Loteria Klaus \u2022 Boa sorte!")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /PET
    # =========================

    @app_commands.command(name="pet", description="Adote um pet virtual!")
    @app_commands.describe(nome="Nome do seu pet", tipo="Tipo: gato, cao, dragao, fantasma, robô")
    async def pet(self, interaction: discord.Interaction, nome: str, tipo: str = "gato") -> None:
        existing = await db.get_pet(interaction.user.id)
        if existing:
            embed = (
                make_embed("purple")
                .title(f"\U0001f43e {existing['name']} - Seu Pet")
                .field("Tipo", f"```{existing['type'].title()}```")
                .field("Level", f"```{existing['level']}```")
                .field("XP", f"```{existing['xp']}/{existing['level'] * 50}```")
                .field("\U0001f356 Fome", f"```{existing['hunger']}/100```")
                .field("\U0001f60a Felicidade", f"```{existing['happiness']}/100```")
                .field("Alimentado", f"```{existing.get('total_fed', 0)} vezes```")
                .desc("Use `/pet_feed` e `/pet_play` para cuidar!")
                .thumb(interaction.user.display_avatar.url)
                .footer("Klaus Pet")
                .timestamp()
                .build()
            )
            await interaction.response.send_message(embed=embed)
            return

        valid = ["gato", "cao", "cachorro", "dragao", "fantasma", "robo", "robô", "panda", "unicornio"]
        if tipo.lower() not in valid:
            await interaction.response.send_message(
                embed=make_embed.error("Tipo Inválido", f"Tipos: {', '.join(valid)}"), ephemeral=True
            )
            return

        pet = await db.create_pet(interaction.user.id, nome, tipo.lower())
        embed = (
            make_embed("success")
            .title(f"\U0001f43e {nome} Adotado!")
            .desc(f"Você adotou um **{tipo.title()}** chamado **{nome}**!")
            .field("Level", f"```{pet['level']}```")
            .field("Fome", f"```{pet['hunger']}/100```")
            .field("Felicidade", f"```{pet['happiness']}/100```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Pet")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pet_feed", description="Alimente seu pet!")
    async def pet_feed(self, interaction: discord.Interaction) -> None:
        result = await db.feed_pet(interaction.user.id)
        if not result["ok"]:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", result["error"]), ephemeral=True
            )
            return

        pet = await db.get_pet(interaction.user.id)
        emoji = "\U0001f389" if result["leveled_up"] else "\U0001f356"
        desc = f"Level up! Agora é level **{pet['level']}**!" if result["leveled_up"] else f"{pet['name']} está satisfeito!"

        embed = (
            make_embed("success")
            .title(f"{emoji} {pet['name']} Alimentado!")
            .desc(desc)
            .field("Fome", f"```{result['hunger']}/100```")
            .field("Felicidade", f"```{result['happiness']}/100```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Pet")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pet_play", description="Brinque com seu pet!")
    async def pet_play(self, interaction: discord.Interaction) -> None:
        result = await db.play_pet(interaction.user.id)
        if not result["ok"]:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", result["error"]), ephemeral=True
            )
            return

        pet = await db.get_pet(interaction.user.id)
        emoji = "\U0001f389" if result["leveled_up"] else "\U0001f3ae"
        desc = f"Level up! Agora é level **{pet['level']}**!" if result["leveled_up"] else f"{pet['name']} adorou brincar!"

        embed = (
            make_embed("success")
            .title(f"{emoji} {pet['name']} Brincou!")
            .desc(desc)
            .field("Felicidade", f"```{result['happiness']}/100```")
            .field("Fome", f"```{result['hunger']}/100```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Pet")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /CASE (GACHA)
    # =========================

    @app_commands.command(name="case", description="Abra uma case e ganhe prêmios raros!")
    async def case(self, interaction: discord.Interaction) -> None:
        balance = await db.get_balance(interaction.user.id)
        price = 2000
        if balance < price:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Custo: **{format_koins(price)}** koins\nSaldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )
            return

        embed = (
            make_embed("purple")
            .title("\U0001f4e6 Abrindo Case...")
            .desc("```\n\U0001f4e6 ???\n```\nAbrindo sua case...")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Cases \u2022 Boa sorte!")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        frames = ["\U0001f4e6", "\U0001f4e5", "\U0001f4e4", "\U0001f381"]
        for f in frames:
            loading = (
                make_embed("purple")
                .title("\U0001f4e6 Abrindo Case...")
                .desc(f"```\n{f}\n```")
                .thumb(interaction.user.display_avatar.url)
                .timestamp()
                .footer("Klaus Cases \u2022 Boa sorte!")
                .build()
            )
            try:
                await message.edit(embed=loading)
            except discord.HTTPException:
                return
            await asyncio.sleep(0.6)

        result = await db.open_case(interaction.user.id, price)
        if not result["ok"]:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", result["error"]), ephemeral=True
            )
            return

        rarity_colors = {
            "common": 0x95A5A6,
            "uncommon": 0x2ECC71,
            "rare": 0x3498DB,
            "epic": 0x9B59B6,
            "legendary": 0xF1C40F,
        }

        bal = await db.get_balance(interaction.user.id)
        final = (
            make_embed(rarity_colors.get(result["rarity"], 0x8B5CF6))
            .title(f"\U0001f4e6 {result['name']}!")
            .desc(f"Você abriu uma case e ganhou: **{result['name']}**!")
            .field("Multiplicador", f"```x{result['multiplier']}```")
            .field("Premio", f"```+ {format_koins(result['prize'])} koins```")
            .field("Saldo", f"```{format_koins(bal)} koins```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Cases")
            .timestamp()
            .build()
        )
        await message.edit(embed=final)

    # =========================
    # /HEIST
    # =========================

    @app_commands.command(name="heist", description="Assalte um banco com sua equipe!")
    @app_commands.describe(valor="Quantidade de koins para investir no heist")
    @app_commands.checks.cooldown(1, 3600, key=lambda i: (i.guild_id, i.user.id))
    async def heist(self, interaction: discord.Interaction, valor: int) -> None:
        if valor < 5000:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Mínimo de **5.000** koins para um heist!"), ephemeral=True
            )
            return

        balance = await db.get_balance(interaction.user.id)
        if balance < valor:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )
            return

        await db.remove_koins(interaction.user.id, valor)

        embed = (
            make_embed("warning")
            .title("\U0001f4b0 ASSALTO BANCÁRIO!")
            .desc(f"**{interaction.user.display_name}** está planejando um assalto!")
            .field("Investimento", f"```{format_koins(valor)} koins```")
            .field("Status", "```\u2581\u2581\u2581\u2581\u2581\u2581\u2581\u2581\u2581\u2581 0%\n```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Heist \u2022 Planejando...")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)
        message = await interaction.original_response()

        frames = [
            ("\u2588\u2581\u2581\u2581\u2581\u2581\u2581\u2581\u2581\u2581", "Infiltrando..."),
            ("\u2588\u2588\u2581\u2581\u2581\u2581\u2581\u2581\u2581\u2581", "Hackeando alarmes..."),
            ("\u2588\u2588\u2588\u2581\u2581\u2581\u2581\u2581\u2581\u2581", "Abrindo cofres..."),
            ("\u2588\u2588\u2588\u2588\u2581\u2581\u2581\u2581\u2581\u2581", "Coletando koins..."),
            ("\u2588\u2588\u2588\u2588\u2588\u2581\u2581\u2581\u2581\u2581", "Escapando..."),
            ("\u2588\u2588\u2588\u2588\u2588\u2588\u2581\u2581\u2581\u2581", "Saindo da cena..."),
            ("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2581\u2581\u2581", "Finalizando..."),
            ("\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588\u2588", "Concluído!"),
        ]

        for barra, status in frames:
            pct = int((len([c for c in barra if c == '\u2588']) / 10) * 100)
            loading = (
                make_embed("warning")
                .title("\U0001f4b0 ASSALTO BANCÁRIO!")
                .desc(f"**{interaction.user.display_name}** está assaltando!")
                .field("Progresso", f"```[{barra}] {pct}%\n{status}```")
                .field("Investimento", f"```{format_koins(valor)} koins```")
                .thumb(interaction.user.display_avatar.url)
                .footer("Klaus Heist \u2022 Assaltando...")
                .timestamp()
                .build()
            )
            try:
                await message.edit(embed=loading)
            except discord.HTTPException:
                return
            await asyncio.sleep(1.5)

        success = random.randint(1, 100) <= 35
        if success:
            multiplier = random.uniform(1.5, 3.0)
            prize = int(valor * multiplier)
            await db.add_koins(interaction.user.id, prize)
            await db.add_heist(interaction.user.id)
            bal = await db.get_balance(interaction.user.id)

            result = (
                make_embed("success")
                .title("\U0001f4b0 ASSALTO BEM-SUCEDIDO!")
                .desc(f"**{interaction.user.display_name}** assaltou o banco com sucesso!")
                .field("Investimento", f"```{format_koins(valor)} koins```")
                .field("Retorno", f"```+ {format_koins(prize)} koins```")
                .field("Multiplicador", f"```x{multiplier:.1f}```")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(interaction.user.display_avatar.url)
                .footer("Klaus Heist")
                .timestamp()
                .build()
            )
        else:
            fine = int(valor * 0.5)
            current = await db.get_balance(interaction.user.id)
            if fine > current:
                fine = current
            await db.remove_koins(interaction.user.id, fine)
            bal = await db.get_balance(interaction.user.id)

            result = (
                make_embed("error")
                .title("\U0001f6a8 ASSALTO FRACASSADO!")
                .desc(f"**{interaction.user.display_name}** foi pego pela polícia!")
                .field("Multa", f"```- {format_koins(fine)} koins```")
                .field("Perda", f"```- {format_koins(valor)} koins (investimento)```")
                .field("Saldo", f"```{format_koins(bal)} koins```")
                .thumb(interaction.user.display_avatar.url)
                .footer("Klaus Heist")
                .timestamp()
                .build()
            )

        try:
            await message.edit(embed=result)
        except discord.HTTPException:
            pass

    @heist.error
    async def heist_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            retry = error.retry_after
            m, s = int((retry % 3600) // 60), int(retry % 60)
            embed = make_embed.error("Cooldown", f"Volte em: **{m}m {s}s**")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            raise error

    # =========================
    # /BOUNTY
    # =========================

    @app_commands.command(name="bounty", description="Coloque um bounty em alguém!")
    @app_commands.describe(alvo="Quem vai ser o alvo", valor="Valor do bounty")
    async def bounty(self, interaction: discord.Interaction, alvo: discord.Member, valor: int) -> None:
        if alvo.id == interaction.user.id:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Não pode colocar bounty em si mesmo!"), ephemeral=True
            )
            return
        if alvo.bot:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Não pode colocar bounty em bots!"), ephemeral=True
            )
            return
        if valor < 1000:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Mínimo de **1.000** koins!"), ephemeral=True
            )
            return

        balance = await db.get_balance(interaction.user.id)
        if balance < valor:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )
            return

        result = await db.place_bounty(alvo.id, interaction.user.id, valor)
        if not result["ok"]:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", result["error"]), ephemeral=True
            )
            return

        bounties = await db.get_bounties(alvo.id)
        total = sum(b["amount"] for b in bounties)

        embed = (
            make_embed("warning")
            .title("\U0001f3af Bounty Colocado!")
            .desc(f"**{interaction.user.display_name}** colocou um bounty em **{alvo.display_name}**!")
            .field("Valor", f"```{format_koins(valor)} koins```")
            .field("Total no Alvo", f"```{format_koins(total)} koins```")
            .field("Bounties Ativos", f"```{len(bounties)}```")
            .thumb(alvo.display_avatar.url)
            .footer("Klaus Bounty")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /INVEST
    # =========================

    @app_commands.command(name="invest", description="Invista seus koins!")
    @app_commands.describe(tipo="Tipo: cripto, acoes, imoveis, nft", valor="Valor para investir")
    async def invest(self, interaction: discord.Interaction, tipo: str, valor: int) -> None:
        from config import settings as cfg
        valid = list(cfg.investment_types.keys())
        if tipo.lower() not in valid:
            await interaction.response.send_message(
                embed=make_embed.error("Tipo Inválido", f"Tipos: {', '.join(valid)}"), ephemeral=True
            )
            return

        inv_data = cfg.investment_types[tipo.lower()]
        if valor < inv_data["min"]:
            await interaction.response.send_message(
                embed=make_embed.error("Mínimo", f"Mínimo de **{format_koins(inv_data['min'])}** koins para {tipo}"),
                ephemeral=True,
            )
            return

        is_premium = await db.is_premium(interaction.user.id)
        investments = await db.get_investments(interaction.user.id)
        active = [i for i in investments if i.get("status") == "active"]
        max_slots = 10 if is_premium else 3
        if len(active) >= max_slots:
            await interaction.response.send_message(
                embed=make_embed.error("Limite", f"Você atingiu o limite de **{max_slots}** investimentos ativos!" + (" Com premium você pode ter mais!" if not is_premium else "")),
                ephemeral=True,
            )
            return

        result = await db.invest(interaction.user.id, tipo.lower(), valor)
        if not result["ok"]:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", result["error"]), ephemeral=True
            )
            return

        embed = (
            make_embed("success")
            .title(f"\U0001f4c8 Investimento em {tipo.title()}")
            .desc(f"**{interaction.user.display_name}** investiu em **{tipo.title()}**!")
            .field("Valor", f"```{format_koins(valor)} koins```")
            .field("Risco", f"```{int(inv_data['risk'] * 100)}%```")
            .field("Retorno Máx", f"```{int(inv_data['max_return'] * 100)}%```")
            .field("Dica", "Use `/collect` para coletar seus investimentos!")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Invest")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    # =========================
    # /DAILY_CHALLENGES
    # =========================

    @app_commands.command(name="challenges", description="Veja seus desafios diários!")
    async def challenges(self, interaction: discord.Interaction) -> None:
        data = await db.get_daily_challenges(interaction.user.id)
        progress = data["progress"]
        completed = data["completed"]

        lines = []
        for i, ch in enumerate(data["challenges"]):
            status = "\u2705" if str(i) in completed else "\u2b55"
            prog = progress.get(str(i), 0)
            bar_len = 10
            filled = min(int((prog / ch["target"]) * bar_len), bar_len)
            bar = "\u2588" * filled + "\u25a1" * (bar_len - filled)
            lines.append(f"{status} **{ch['name']}**\n`[{bar}]` {prog}/{ch['target']} — Recompensa: {format_koins(ch['reward'])} koins")

        embed = (
            make_embed("purple")
            .title("\U0001f3af Desafios Diários")
            .desc("\n\n".join(lines) if lines else "Nenhum desafio disponível.")
            .field("Completados", f"```{len(completed)}/{len(data['challenges'])}```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Clique nos botões abaixo para executar cada desafio!")
            .timestamp()
            .build()
        )
        view = ChallengeView(data["challenges"], completed, interaction.user.id)
        if not view.children:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(embed=embed, view=view)

    # =========================
    # /LUCKY_WHEEL
    # =========================

    @app_commands.command(name="lucky_wheel", description="Gire a roda da sorte!")
    @app_commands.checks.cooldown(1, 7200, key=lambda i: (i.guild_id, i.user.id))
    async def lucky_wheel(self, interaction: discord.Interaction) -> None:
        result = await db.spin_lucky_wheel(interaction.user.id)
        bal = await db.get_balance(interaction.user.id)

        embed = (
            make_embed("gold")
            .title("\U0001f3b0 Roda da Sorte!")
            .desc(f"**{interaction.user.display_name}** girou a roda e ganhou!")
            .field("Prêmio", f"```+ {format_koins(result['reward'])} koins```")
            .field("Saldo", f"```{format_koins(bal)} koins```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Klaus Lucky Wheel")
            .timestamp()
            .build()
        )
        await interaction.response.send_message(embed=embed)

    @lucky_wheel.error
    async def lucky_wheel_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            retry = error.retry_after
            m, s = int((retry % 3600) // 60), int(retry % 60)
            embed = make_embed.error("Cooldown", f"Volte em: **{m}m {s}s**")
            embed.set_thumbnail(url=interaction.user.display_avatar.url)
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            raise error

    # =========================
    # /BATALHAR
    # =========================

    @app_commands.command(name="batalhar", description="Desafie alguém para uma batalha de koins!")
    @app_commands.describe(adversario="O jogador que você quer desafiar", valor="Quantidade de koins para apostar")
    async def batalhar(self, interaction: discord.Interaction, adversario: discord.Member, valor: int) -> None:
        if adversario.id == interaction.user.id:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Não pode batalhar contra si mesmo!"), ephemeral=True
            )
            return
        if adversario.bot:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Não pode batalhar contra bots!"), ephemeral=True
            )
            return
        if valor <= 0:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Valor deve ser maior que zero."), ephemeral=True
            )
            return
        balance = await db.get_balance(interaction.user.id)
        if balance < valor:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )
            return
        adv_balance = await db.get_balance(adversario.id)
        if adv_balance < valor:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"{adversario.display_name} precisa de **{format_koins(valor)}** koins."),
                ephemeral=True,
            )
            return

        embed = (
            make_embed("warning")
            .title("\u2694\ufe0f Batalha de Koins!")
            .desc(f"**{interaction.user.display_name}** desafiou **{adversario.display_name}**!\n\nUse seus poderes para vencer!")
            .field("Aposta", f"```{format_koins(valor)} koins```")
            .field("Mecânica", "Cada jogador escolhe Ataque, Defesa ou Especial.\n\n⚔️ **Ataque** vence 🛡️ **Defesa**\n🛡️ **Defesa** vence ✨ **Especial**\n✨ **Especial** vence ⚔️ **Ataque**\n\nEmpate = repetição!")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .footer("Klaus Battle")
            .build()
        )
        view = BattleView(interaction.user, adversario, valor)
        await interaction.response.send_message(content=adversario.mention, embed=embed, view=view)

    @batalhar.error
    async def batalhar_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        await interaction.response.send_message(
            embed=make_embed.error("Erro", str(error)), ephemeral=True
        )

    # =========================
    # /CAIXA_FORTUNA
    # =========================

    @app_commands.command(name="caixa_fortuna", description="Abra uma caixa da sorte e ganhe prêmios!")
    @app_commands.checks.cooldown(1, 3600, key=lambda i: i.user.id)
    async def caixa_fortuna(self, interaction: discord.Interaction) -> None:
        prizes = [
            {"emoji": "\U0001f4b5", "name": "Koins", "min": 100, "max": 5000, "weight": 50},
            {"emoji": "\U0001f48e", "name": "Diamante Raro", "min": 5000, "max": 20000, "weight": 20},
            {"emoji": "\U0001f451", "name": "Coroa Lendária", "min": 10000, "max": 50000, "weight": 10},
            {"emoji": "\u2b50", "name": "Estrela da Sorte", "min": 20000, "max": 100000, "weight": 5},
            {"emoji": "\U0001f525", "name": "Fênix Premium", "min": 50000, "max": 200000, "weight": 3},
            {"emoji": "\U0001f3af", "name": "Jackpot Total", "min": 100000, "max": 500000, "weight": 2},
        ]
        is_premium = await db.is_premium(interaction.user.id)
        if is_premium:
            for p in prizes:
                p["weight"] = int(p["weight"] * 1.5)

        total_weight = sum(p["weight"] for p in prizes)
        roll = random.randint(1, total_weight)
        cumulative = 0
        chosen = prizes[0]
        for p in prizes:
            cumulative += p["weight"]
            if roll <= cumulative:
                chosen = p
                break

        amount = random.randint(chosen["min"], chosen["max"])
        if is_premium:
            amount = int(amount * 1.5)

        embed_loading = (
            make_embed("warning")
            .title("\U0001f4e6 Caixa da Fortuna!")
            .desc(f"**{interaction.user.display_name}**, abrindo sua caixa...\n\n```\n[\u2588\u2588\u2588\u25a1\u25a1\u25a1\u25a1\u25a1\u25a1\u25a1] 30%\n```\nPreparando seu prêmio...")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .footer("Klaus Caixa da Fortuna")
            .build()
        )
        await interaction.response.send_message(embed=embed_loading)
        message = await interaction.original_response()

        for pct in [60, 90, 100]:
            barra = "\u2588" * (pct // 10) + "\u25a1" * (10 - (pct // 10))
            embed_step = (
                make_embed("warning")
                .title("\U0001f4e6 Caixa da Fortuna!")
                .desc(f"**{interaction.user.display_name}**, abrindo sua caixa...\n\n```\n[{barra}] {pct}%\n```\nPreparando seu prêmio...")
                .thumb(interaction.user.display_avatar.url)
                .timestamp()
                .footer("Klaus Caixa da Fortuna")
                .build()
            )
            await message.edit(embed=embed_step)
            await asyncio.sleep(0.7)

        await db.add_koins(interaction.user.id, amount)
        balance = await db.get_balance(interaction.user.id)

        embed_final = (
            make_embed("success")
            .title(f"\U0001f381 {chosen['emoji']} {chosen['name']}!")
            .desc(f"**{interaction.user.display_name}** abriu a caixa e ganhou!\n\n{chosen['emoji']} **{format_koins(amount)}** koins!")
            .field("\U0001f4b0 Novo Saldo", f"```{format_koins(balance)} koins```")
            .thumb(interaction.user.display_avatar.url)
            .footer("Caixa da Fortuna • Klaus", interaction.user.display_avatar.url)
            .timestamp()
            .build()
        )
        await message.edit(embed=embed_final)

    @caixa_fortuna.error
    async def caixa_fortuna_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            m, s = int((error.retry_after % 3600) // 60), int(error.retry_after % 60)
            await interaction.response.send_message(
                embed=make_embed.error("Cooldown", f"Volte em: **{m}m {s}s**"), ephemeral=True
            )
        else:
            raise error

    # =========================
    # /SORTEIO
    # =========================

    @app_commands.command(name="sorteio", description="Gire a roda da sorte e ganhe prêmios!")
    @app_commands.describe(valor="Quantidade de koins para apostar (mínimo 100)")
    @app_commands.checks.cooldown(1, 30, key=lambda i: i.user.id)
    async def sorteio(self, interaction: discord.Interaction, valor: int = 100) -> None:
        if valor < 100:
            await interaction.response.send_message(
                embed=make_embed.error("Erro", "Mínimo de **100** koins para jogar!"), ephemeral=True
            )
            return
        balance = await db.get_balance(interaction.user.id)
        if balance < valor:
            await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )
            return

        prizes = [
            {"name": "💀 Sem prêmio", "multiplier": 0, "weight": 30},
            {"name": "🪙 1.5x", "multiplier": 1.5, "weight": 25},
            {"name": "💰 2x", "multiplier": 2, "weight": 20},
            {"name": "💎 3x", "multiplier": 3, "weight": 15},
            {"name": "👑 5x", "multiplier": 5, "weight": 8},
            {"name": "🌟 10x JACKPOT!", "multiplier": 10, "weight": 2},
        ]
        total_weight = sum(p["weight"] for p in prizes)
        roll = random.randint(1, total_weight)
        cumulative = 0
        chosen = prizes[0]
        for p in prizes:
            cumulative += p["weight"]
            if roll <= cumulative:
                chosen = p
                break

        winnings = int(valor * chosen["multiplier"])
        won = winnings > 0

        frames = ["\U0001f3b0", "\U0001f3b2", "\u26cf\ufe0f", "\U0001f3b1", "\U0001f3ad", "\U0001f0cf"]
        embed_loading = (
            make_embed("warning")
            .title("\U0001f3b0 Roda da Sorte!")
            .desc(f"**{interaction.user.display_name}** apostou **{format_koins(valor)}** koins...\n\n```\n{random.choice(frames)} Girando...\n```")
            .thumb(interaction.user.display_avatar.url)
            .timestamp()
            .footer("Klaus Sorteio")
            .build()
        )
        await interaction.response.send_message(embed=embed_loading)
        message = await interaction.original_response()

        for _ in range(5):
            frame = random.choice(frames)
            embed_spin = (
                make_embed("warning")
                .title("\U0001f3b0 Roda da Sorte!")
                .desc(f"**{interaction.user.display_name}** apostou **{format_koins(valor)}** koins...\n\n```\n{frame} Girando...\n```")
                .thumb(interaction.user.display_avatar.url)
                .timestamp()
                .footer("Klaus Sorteio")
                .build()
            )
            await message.edit(embed=embed_spin)
            await asyncio.sleep(0.4)

        if won:
            await db.add_koins(interaction.user.id, winnings)
            embed_final = (
                make_embed("success")
                .title(f"\U0001f389 {chosen['name']}")
                .desc(f"**{interaction.user.display_name}** ganhou **{format_koins(winnings)}** koins!")
                .field("Aposta", f"```{format_koins(valor)} koins```")
                .field("Prêmio", f"```{chosen['name']}```")
                .field("Lucro", f"```+{format_koins(winnings - valor)} koins```")
                .thumb(interaction.user.display_avatar.url)
                .footer("Roda da Sorte • Klaus", interaction.user.display_avatar.url)
                .timestamp()
                .build()
            )
        else:
            await db.remove_koins(interaction.user.id, valor)
            embed_final = (
                make_embed("error")
                .title(f"\U0001f4a5 {chosen['name']}")
                .desc(f"**{interaction.user.display_name}** perdeu **{format_koins(valor)}** koins...")
                .field("Aposta", f"```{format_koins(valor)} koins```")
                .field("Resultado", "```Sem prêmio```")
                .thumb(interaction.user.display_avatar.url)
                .footer("Roda da Sorte • Klaus", interaction.user.display_avatar.url)
                .timestamp()
                .build()
            )
        await message.edit(embed=embed_final)

    @sorteio.error
    async def sorteio_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            m, s = int((error.retry_after % 60)), int(error.retry_after % 60)
            await interaction.response.send_message(
                embed=make_embed.error("Cooldown", f"Volte em: **{m}m {s}s**"), ephemeral=True
            )
        else:
            raise error

    # ── SLOT ───────────────────────────────────────────────

    @app_commands.command(name="slot", description="Gire a roda caça-niquel e tente ganhar koins!")
    @app_commands.describe(aposta="Valor da aposta em koins")
    @app_commands.checks.cooldown(1, 5, key=lambda i: i.user.id)
    async def slot(self, interaction: discord.Interaction, aposta: int) -> None:
        if aposta <= 0:
            return await interaction.response.send_message(embed=make_embed.error("Erro", "Aposta deve ser maior que 0!"), ephemeral=True)
        if aposta > 100000:
            return await interaction.response.send_message(embed=make_embed.error("Erro", "Aposta maxima: 100.000 koins!"), ephemeral=True)

        balance = await db.get_balance(interaction.user.id)
        if balance < aposta:
            return await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                ephemeral=True,
            )

        view = SlotView(interaction.user, aposta)
        embed = make_embed.info(
            "🎰 Slot Machine",
            f"Aposta: **{format_koins(aposta)}** koins\n\nClique para girar!"
        )
        await interaction.response.send_message(embed=embed, view=view)

    @slot.error
    async def slot_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(
                embed=make_embed.error("Cooldown", f"Aguarde **{int(error.retry_after)}s** para girar novamente!"),
                ephemeral=True,
            )
        else:
            raise error


# =========================
# VIEW: Batalha PvP
# =========================


class BattleView(discord.ui.View):
    def __init__(self, author: discord.Member, adversary: discord.Member, amount: int) -> None:
        super().__init__(timeout=45)
        self.author = author
        self.adversary = adversary
        self.amount = amount
        self.choices: dict[int, str | None] = {author.id: None, adversary.id: None}
        self.choices_made = 0

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id not in self.choices:
            await interaction.response.send_message(
                embed=make_embed.error("Acesso Negado", "Essa batalha não é sua!"), ephemeral=True
            )
            return False
        if self.choices[interaction.user.id] is not None:
            await interaction.response.send_message(
                embed=make_embed.error("Já Escolheu", "Você já fez sua escolha!"), ephemeral=True
            )
            return False
        return True

    def resolve(self) -> str:
        c1 = self.choices[self.author.id]
        c2 = self.choices[self.adversary.id]
        wins = {
            ("ataque", "defesa"): self.author.id,
            ("defesa", "especial"): self.author.id,
            ("especial", "ataque"): self.author.id,
            ("defesa", "ataque"): self.adversary.id,
            ("especial", "defesa"): self.adversary.id,
            ("ataque", "especial"): self.adversary.id,
        }
        if c1 == c2:
            return "empate"
        return wins.get((c1, c2), "empate")

    async def _resolve_battle(self, interaction: discord.Interaction) -> None:
        result = self.resolve()
        if result == "empate":
            embed = (
                make_embed("warning")
                .title("\u2694\ufe0f Batalha — Empate!")
                .desc("Ambos escolheram a mesma coisa! Sem vencedor.")
                .timestamp()
                .footer("Klaus Battle")
                .build()
            )
            await interaction.response.edit_message(embed=embed, view=None)
            return

        winner_id = result
        loser_id = self.adversary.id if winner_id == self.author.id else self.author.id
        winner = self.author if winner_id == self.author.id else self.adversary
        loser = self.adversary if winner_id == self.author.id else self.author

        await db.remove_koins(loser.id, self.amount)
        await db.add_koins(winner.id, self.amount)

        c1_emoji = {"ataque": "⚔️", "defesa": "🛡️", "especial": "✨"}[self.choices[self.author.id]]
        c2_emoji = {"ataque": "⚔️", "defesa": "🛡️", "especial": "✨"}[self.choices[self.adversary.id]]

        embed = (
            make_embed("success")
            .title(f"\U0001f3c6 {winner.display_name} Venceu!")
            .desc(
                f"**{self.author.display_name}** escolheu {c1_emoji} `{self.choices[self.author.id]}`\n"
                f"**{self.adversary.display_name}** escolheu {c2_emoji} `{self.choices[self.adversary.id]}`\n\n"
                f"\U0001f4b0 **{winner.display_name}** ganhou **{format_koins(self.amount)}** koins!"
            )
            .field("Resultado", f"```{self.author.display_name}: {c1_emoji} {self.choices[self.author.id].upper()}\n{self.adversary.display_name}: {c2_emoji} {self.choices[self.adversary.id].upper()}```")
            .thumb(winner.display_avatar.url)
            .footer("Batalha de Koins • Klaus")
            .timestamp()
            .build()
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="⚔️ Ataque", style=discord.ButtonStyle.danger, row=0)
    async def btn_ataque(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.choices[interaction.user.id] = "ataque"
        self.choices_made += 1
        if self.choices_made >= 2:
            await self._resolve_battle(interaction)
        else:
            embed = (
                make_embed("warning")
                .title("\u2694\ufe0f Batalha em Andamento...")
                .desc(f"**{interaction.user.display_name}** escolheu ⚔️ **Ataque**!\n\nAguardando o adversário...")
                .timestamp()
                .footer("Klaus Battle")
                .build()
            )
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="🛡️ Defesa", style=discord.ButtonStyle.primary, row=0)
    async def btn_defesa(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.choices[interaction.user.id] = "defesa"
        self.choices_made += 1
        if self.choices_made >= 2:
            await self._resolve_battle(interaction)
        else:
            embed = (
                make_embed("warning")
                .title("\u2694\ufe0f Batalha em Andamento...")
                .desc(f"**{interaction.user.display_name}** escolheu 🛡️ **Defesa**!\n\nAguardando o adversário...")
                .timestamp()
                .footer("Klaus Battle")
                .build()
            )
            await interaction.response.edit_message(embed=embed)

    @discord.ui.button(label="✨ Especial", style=discord.ButtonStyle.success, row=0)
    async def btn_especial(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        self.choices[interaction.user.id] = "especial"
        self.choices_made += 1
        if self.choices_made >= 2:
            await self._resolve_battle(interaction)
        else:
            embed = (
                make_embed("warning")
                .title("\u2694\ufe0f Batalha em Andamento...")
                .desc(f"**{interaction.user.display_name}** escolheu ✨ **Especial**!\n\nAguardando o adversário...")
                .timestamp()
                .footer("Klaus Battle")
                .build()
            )
            await interaction.response.edit_message(embed=embed)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True


# =========================
# COMMAND: Slot Machine
# =========================

SLOT_EMOJIS = ["🍒", "🍋", "🍊", "🍇", "💎", "7️⃣"]
SLOT_WEIGHTS = [30, 25, 20, 15, 7, 3]

class SlotView(discord.ui.View):
    def __init__(self, author: discord.Member, bet: int) -> None:
        super().__init__(timeout=30)
        self.author = author
        self.bet = bet

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.author.id:
            await interaction.response.send_message(embed=make_embed.error("Acesso Negado", "Essa aposta nao e sua!"), ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Girar! 🎰", style=discord.ButtonStyle.primary)
    async def spin(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        balance = await db.get_balance(self.author.id)
        if balance < self.bet:
            return await interaction.response.edit_message(
                embed=make_embed.error("Saldo Insuficiente", f"Saldo: **{format_koins(balance)}** koins"),
                view=None,
            )

        await db.add_koins(self.author.id, -self.bet)

        results = random.choices(SLOT_EMOJIS, weights=SLOT_WEIGHTS, k=3)
        slots_display = f"[ {results[0]} | {results[1]} | {results[2]} ]"

        if results[0] == results[1] == results[2]:
            if results[0] == "7️⃣":
                multiplier = 20
                result_text = "JACKPOT! 🎉"
            elif results[0] == "💎":
                multiplier = 10
                result_text = "DIAMANTES! 💎"
            else:
                multiplier = 5
                result_text = "TRINCA! 🔥"
            winnings = self.bet * multiplier
        elif results[0] == results[1] or results[1] == results[2] or results[0] == results[2]:
            multiplier = 2
            result_text = "PAR! ✨"
            winnings = self.bet * multiplier
        else:
            multiplier = 0
            result_text = "Nada... 😢"
            winnings = 0

        if winnings > 0:
            await db.add_koins(self.author.id, winnings)
            if winnings >= 10000:
                await db.add_achievement(self.author.id, "big_win")

        bal = await db.get_balance(self.author.id)

        embed = make_embed.info(
            "🎰 Slot Machine",
            f"```\n{slots_display}\n```\n"
            f"{result_text}\n"
            + (f"Ganhou: **{format_koins(winnings)}** koins\n" if winnings > 0 else f"Perdeu: **{format_koins(self.bet)}** koins\n")
            + f"Saldo: **{format_koins(bal)}** koins"
        )
        await interaction.response.edit_message(embed=embed, view=self)

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True


async def setup(bot: KlausBot) -> None:
    await bot.add_cog(Economia(bot))
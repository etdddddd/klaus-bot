from __future__ import annotations

import logging
import random
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from config import settings
from database import db
from embed_builder import KlausEmbed as make_embed
from helpers import format_koins

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from klaus import KlausBot


class Social(commands.Cog):
    def __init__(self, bot: "KlausBot") -> None:
        self.bot = bot

    # ── MARRY ──────────────────────────────────────────────

    @app_commands.command(name="marry", description="Case-se com outro membro do servidor!")
    @app_commands.describe(membro="Membro para se casar", valor="Valor do presente (koins, opcional)")
    async def marry(self, interaction: discord.Interaction, membro: discord.Member, valor: int = 0) -> None:
        if membro.bot:
            return await interaction.response.send_message(embed=make_embed.error("Erro", "Voce nao pode casar com um bot!"), ephemeral=True)
        if membro.id == interaction.user.id:
            return await interaction.response.send_message(embed=make_embed.error("Erro", "Voce nao pode casar consigo mesmo!"), ephemeral=True)

        user_data = await db.get_user(interaction.user.id)
        married_to = user_data.get("married_to")
        if married_to:
            return await interaction.response.send_message(embed=make_embed.error("Erro", "Voce ja e casado(a)! Use `/divorce` primeiro."), ephemeral=True)

        target_data = await db.get_user(membro.id)
        if target_data.get("married_to"):
            return await interaction.response.send_message(embed=make_embed.error("Erro", f"**{membro.display_name}** ja e casado(a)!"), ephemeral=True)

        if valor > 0:
            balance = await db.get_balance(interaction.user.id)
            if balance < valor:
                return await interaction.response.send_message(embed=make_embed.error("Saldo Insuficiente", f"Voce precisa de **{format_koins(valor)}** koins para o presente."), ephemeral=True)

        view = MarryView(interaction.user, membro, valor)
        embed = make_embed.info(
            "Proposta de Casamento",
            f"**{interaction.user.display_name}** esta pedindo **{membro.display_name}** em casamento!"
            + (f"\n\nPresente: **{format_koins(valor)}** koins" if valor > 0 else "")
            + f"\n\n{membro.mention}, voce aceita?"
        )
        await interaction.response.send_message(embed=embed, view=view)

    # ── DIVORCE ────────────────────────────────────────────

    @app_commands.command(name="divorce", description="Divorcie-se do seu conjuge")
    async def divorce(self, interaction: discord.Interaction) -> None:
        user_data = await db.get_user(interaction.user.id)
        married_to = user_data.get("married_to")
        if not married_to:
            return await interaction.response.send_message(embed=make_embed.error("Erro", "Voce nao e casado(a)!"), ephemeral=True)

        partner = self.bot.get_user(married_to)
        partner_name = partner.display_name if partner else "Desconhecido"

        view = discord.ui.View(timeout=30)

        async def confirm_callback(i: discord.Interaction) -> None:
            if i.user.id != interaction.user.id:
                return await i.response.send_message("Essa nao e sua decisao!", ephemeral=True)
            await db.update_user(interaction.user.id, {"$unset": {"married_to": ""}})
            if partner:
                await db.update_user(married_to, {"$unset": {"married_to": ""}})
            await i.response.edit_message(
                embed=make_embed.success("Divorcio", f"Voce se divorciou de **{partner_name}**. 😔"),
                view=None,
            )

        async def cancel_callback(i: discord.Interaction) -> None:
            if i.user.id != interaction.user.id:
                return await i.response.send_message("Essa nao e sua decisao!", ephemeral=True)
            await i.response.edit_message(
                embed=make_embed.info("Divorcio", "Divorcio cancelado! Ufa!"),
                view=None,
            )

        confirm = discord.ui.Button(label="Sim, divorciar", style=discord.ButtonStyle.danger)
        cancel = discord.ui.Button(label="Nao, manter", style=discord.ButtonStyle.secondary)
        confirm.callback = confirm_callback
        cancel.callback = cancel_callback
        view.add_item(confirm)
        view.add_item(cancel)

        embed = make_embed.warning(
            "Divorcio",
            f"Voce esta se divorciando de **{partner_name}**.\nTem certeza?"
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)

    # ── COMPRAR ────────────────────────────────────────────

    @app_commands.command(name="comprar", description="Compre um item da loja")
    @app_commands.describe(item="Nome do item")
    async def buy(self, interaction: discord.Interaction, item: str) -> None:
        from cogs.economia import Economia
        econ = self.bot.get_cog("Economia")
        if not econ:
            return await interaction.response.send_message(embed=make_embed.error("Erro", "Sistema de economia indisponivel."), ephemeral=True)

        shop_items = getattr(econ, "SHOP_ITEMS", {})
        item_lower = item.lower().strip()

        found = None
        for key, data in shop_items.items():
            if item_lower in key.lower() or item_lower in data.get("name", "").lower():
                found = (key, data)
                break

        if not found:
            return await interaction.response.send_message(
                embed=make_embed.error("Item Nao Encontrado", f"Use `/loja` para ver os itens disponiveis."),
                ephemeral=True,
            )

        key, data = found
        price = data.get("price", 0)
        balance = await db.get_balance(interaction.user.id)
        if balance < price:
            return await interaction.response.send_message(
                embed=make_embed.error("Saldo Insuficiente", f"Voce precisa de **{format_koins(price)}** koins.\nSeu saldo: **{format_koins(balance)}** koins."),
                ephemeral=True,
            )

        await db.add_koins(interaction.user.id, -price)
        await db.add_item(interaction.user.id, key)
        await interaction.response.send_message(
            embed=make_embed.success("Compra Realizada", f"Voce comprou **{data.get('name', key)}** por **{format_koins(price)}** koins!")
        )


class MarryView(discord.ui.View):
    def __init__(self, author: discord.Member, target: discord.Member, gift: int = 0) -> None:
        super().__init__(timeout=60)
        self.author = author
        self.target = target
        self.gift = gift

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user.id != self.target.id:
            await interaction.response.send_message("Essa proposta nao e para voce!", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Aceitar 💍", style=discord.ButtonStyle.success)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        if self.gift > 0:
            bal = await db.get_balance(self.author.id)
            if bal < self.gift:
                return await interaction.response.edit_message(
                    embed=make_embed.error("Erro", "O noivo(a) nao tem mais saldo para o presente!"),
                    view=None,
                )
            await db.add_koins(self.author.id, -self.gift)

        await db.update_user(self.author.id, {"married_to": self.target.id})
        await db.update_user(self.target.id, {"married_to": self.author.id})

        embed = make_embed.success(
            "Casamento!",
            f"**{self.author.display_name}** e **{self.target.display_name}** estao oficialmente casados! 💍🎉"
            + (f"\nPresente: **{format_koins(self.gift)}** koins" if self.gift > 0 else "")
        )
        await interaction.response.edit_message(embed=embed, view=None)

    @discord.ui.button(label="Recusar 😔", style=discord.ButtonStyle.danger)
    async def reject(self, interaction: discord.Interaction, button: discord.ui.Button) -> None:
        embed = make_embed.warning(
            "Proposta Recusada",
            f"**{self.target.display_name}** recusou a proposta de **{self.author.display_name}**. 😔"
        )
        await interaction.response.edit_message(embed=embed, view=None)


async def setup(bot: "KlausBot") -> None:
    await bot.add_cog(Social(bot))

import discord
import json

from discord.ext import commands
from discord import app_commands
from aiohttp import ClientSession
from typing import List, Any, Dict, Union

from Bot import Bot


class WarframeMarket(commands.Cog):


    def __init__(self, bot: Bot):
        self.bot = bot
        self.base_url: str = "https://api.warframe.market/v1"
        self.items_list: List[Dict[str, str]] = []
        self.is_synced: bool = False
        self.image_url: str = "https://warframe.market/static/assets"
        
        
    async def sync(self):
        """Syncs the items information from WarframeMarket.
        """
        session: ClientSession = self.bot.session  
        async with session.get(self.base_url+"/items") as r:
            if r.status == 200:
                response = await r.read()
                self.items_list = json.loads(response)['payload']['items']
                self.is_synced = True
            else:
                print("WarframeMarket down!")


    async def cog_load(self) -> None:
        try:
            await self.sync()
        except Exception as e:
            print(e)
    
    
    async def item_autocomplete(self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        """An autocomplete function

        Args:
            interaction (discord.Interaction): the interaction that invokes this coroutine
            current (str): whatever the user has typed as the input

        Returns:
            List[app_commands.Choice[str]]: The list of choices matching the input
        """
        if not self.is_synced:
            await self.sync()
        return [
            app_commands.Choice(name=item['item_name'], value=item['item_name'])
            for item in self.items_list if current.lower() in item['item_name'].lower()
        ][:25]
    
    
    @app_commands.command(name="item")
    @app_commands.choices(choices=[
        app_commands.Choice(name="I want to buy", value="sell"),
        app_commands.Choice(name="I want to sell", value="buy"),
        ])
    @app_commands.autocomplete(item_name=item_autocomplete)
    @app_commands.describe(choices="Do you want to buy or sell, in fact?!", item_name="Which item, in fact?!")
    async def get_item(self, interaction: discord.Interaction, choices: app_commands.Choice[str], item_name: str):
        """Get item information and buy/sell orders.

        Args:
            interaction (discord.Interaction): the interaction that invokes this coroutine
            choices (app_commands.Choice[str]): buying or selling?
            item_name (str): item name to search for
        """
        order_type: str = choices.value  
        if not self.is_synced:
            await self.sync()
        item_info = None
        for item in self.items_list:
            if item['item_name'] == item_name:
                item_info = item
        if item_info is not None:
            url_name = item_info['url_name']
            session: ClientSession = self.bot.session  
            item_detail: Dict[str, Any] = {}
            async with session.get(self.base_url+"/items/"+url_name) as r:
                if r.status == 200:
                    response = await r.read()
                    item_detail = json.loads(response)['payload']['item']['items_in_set'][0]
                else:
                    print("WarframeMarket down!")
            trading_tax: str = item_detail['trading_tax'] if 'trading_tax' in item_detail.keys() else "No trading tax value"
            ducats: str = item_detail['ducats'] if 'ducats' in item_detail.keys() else "No ducats value"
            mastery_level: str = item_detail['mastery_level'] if 'mastery_level' in item_detail.keys() else "No mastery level"
            item_description: str = item_detail['en']['description']
            wikilink: str = item_detail['en']['wiki_link']
            drop_list: List[Dict[str, str]] = item_detail['en']['drop']
            desc: str = f"Requires mastery rank {mastery_level}\n"
            desc += f"Trading tax: {trading_tax}, Ducats value: {ducats}\n"
            desc += f"```{item_description}```\n"
            desc += f"Drops from " if len(drop_list)>0 else ""
            for i in range(len(drop_list)):
                desc += drop_list[i]['name']+', ' if i < len(drop_list)-1 else drop_list[i]['name']
            session = self.bot.session  
            orders_sorted: List[Dict[Union[Dict[str, Any], str], Any]] = []
            async with session.get(self.base_url+"/items/"+url_name+"/orders") as r:
                if r.status == 200:
                    response = await r.read()
                    orders = json.loads(response)['payload']['orders']
                    online_orders = [o for o in orders if o['user']['status'] != 'offline']
                    filtered_types = [o for o in online_orders if o['order_type'] == order_type]
                    orders_sorted = sorted(filtered_types, key = lambda ele: ele['platinum']) if order_type != 'buy' else sorted(filtered_types, key = lambda ele: ele['platinum'], reverse=True)
                else:
                    print("WarframeMarket down!")
            for i in range(len(orders_sorted)):
                if i>4:
                    break
                desc += f"\n\nPrice: {orders_sorted[i]['platinum']} plat, Quantity: {orders_sorted[i]['quantity']}, Order type: {orders_sorted[i]['order_type']}\n"
                desc += f"by {orders_sorted[i]['user']['ingame_name']}\n"
                desc += f"```/w {orders_sorted[i]['user']['ingame_name']} Hi! I want to {orders_sorted[i]['order_type']}: {item_name} for {orders_sorted[i]['platinum']} platinum. (warframe.market)```\n"
            embed = discord.Embed(
                color=discord.Colour.random(),
                title=item_info['item_name'],
                url=wikilink,
                description=desc,
            )
            embed.set_thumbnail(url=self.image_url+"/"+item_info['thumb'])
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("I couldn't find that item, in fact!")


async def setup(bot: Bot):
    await bot.add_cog(WarframeMarket(bot))

import discord, aiohttp, re

from bs4 import BeautifulSoup as b_soup
from datetime import datetime
from random import choice
from io import BytesIO
from urllib.parse import quote_plus

from discord.ext import commands
from .utils import checks, time

class Misc:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="retro", pass_context=True, brief="make retro banners")
    async def make_retro(self, ctx, *, content:str):
        texts = [t.strip() for t in content.split("|")]
        if len(texts) != 3:
            await self.bot.say("\N{CROSS MARK} Sorry! That input couldn't be parsed. Do you have 2 seperators? ( `|` )")
            return

        await self.bot.type()
        _tmp_choice = choice([1, 2, 3, 4])

        data = dict(
            bg=_tmp_choice,
            txt=_tmp_choice,
            text1=texts[0],
            text2=texts[1],
            text3=texts[2]
        )

        async with self.bot.aio_session.post("https://photofunia.com/effects/retro-wave", data=data) as response:
            if response.status != 200:
                await self.bot.say("\N{CROSS MARK} Could not connect to server. Please try again later")
                return

            soup = b_soup(await response.text(), "lxml")
            download_url = soup.find("div", class_="downloads-container").ul.li.a["href"]

            result_embed = discord.Embed()
            result_embed.set_image(url=download_url)

            await self.bot.say(embed=result_embed)

    @commands.command(name="xkcd", pass_context=True, brief="fetch xkcd comics")
    async def get_xkcd(self, ctx, id : str = None):
        comic_url = ""

        if id is None:
            async with self.bot.aio_session.get("https://c.xkcd.com/random/comic", allow_redirects=False) as header_response:
                comic_url = header_response.headers["Location"]
        else:
            comic_url = f"https://xkcd.com/{id}/"
        comic_data_url = f"{comic_url}info.0.json"

        async with self.bot.aio_session.get(comic_data_url) as response:
            if response.status != 200:
                await self.bot.say("\N{CROSS MARK} Couldn't connect to server.")
                return

            data = await response.json()

            result_embed = discord.Embed(title=f"{data['title']} - {data['num']}", url=comic_url, description=data["alt"])
            result_embed.set_footer(icon_url="https://xkcd.com/favicon.ico", text="Served by XKCD")
            result_embed.set_image(url=data["img"])

            await self.bot.say(embed=result_embed)

    @commands.command(name="uptime", pass_context=True, brief="show bot uptime")
    async def show_uptime(self, ctx):
        await self.bot.say(f"Snake has been running for **{time.get_elapsed_time(self.bot.start_time, datetime.now())}** ({self.bot.start_time:{time.time_format}})")

    @commands.command(name="suggest", pass_context=True, brief="give feedback", no_pm=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def give_feedback(self, ctx, *, message:str):


def setup(bot):
    bot.add_cog(Misc(bot))
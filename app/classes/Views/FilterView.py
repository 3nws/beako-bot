import discord


from io import BytesIO
from discord import ui
from aiohttp.client import ClientSession
from typing import Optional
from typing_extensions import Self
from typing import Callable, Coroutine, Any
from wand.image import Image
from wand.compat import to_bytes  # type: ignore
from functools import wraps

from Bot import Bot


Callable_ = Callable[
    ["FilterView", int], Coroutine[Any, Any, None]
]  # Callable[Ellipis(singleton), Coroutine[YieldType, SendType, ReturnType]]


def apply_filter(func: Callable_) -> Callable_:
    @wraps(func)
    async def inner(self: "FilterView", choice: int) -> None:
        msg: discord.Message = await self.i.channel.send("Loading, I suppose!..")  # type: ignore
        await func(self, choice)
        with Image(blob=self.bytes_image) as img:  # type: ignore
            if choice == 0:
                img.blur(radius=0, sigma=3)  # type: ignore
            elif choice == 1:
                img.shade(gray=True, azimuth=286.0, elevation=45.0)  # type: ignore
            elif choice == 2:
                img.sharpen(radius=8, sigma=4)  # type: ignore
            elif choice == 3:
                img.spread(radius=8.0)  # type: ignore
            elif choice == 4:
                img.transform_colorspace("gray")  # type: ignore
                img.edge(radius=1)  # type: ignore
            elif choice == 5:
                img.transform_colorspace("gray")  # type: ignore
                img.emboss(radius=3.0, sigma=1.75)  # type: ignore
            elif choice == 6:
                img.charcoal(radius=1.5, sigma=0.5)  # type: ignore
            elif choice == 7:
                img.wave(amplitude=img.height / 32, wave_length=img.width / 4)  # type: ignore
            elif choice == 8:
                img.colorize(color="yellow", alpha="rgb(10%, 0%, 20%)")  # type: ignore
            elif choice == 9:
                img.sepia_tone(threshold=0.8)  # type: ignore
            elif choice == 10:
                img.transform_colorspace("gray")  # type: ignore
                img.sketch(0.5, 0.0, 98.0)  # type: ignore
            elif choice == 11:
                img.solarize(threshold=0.5 * img.quantum_range)  # type: ignore
            elif choice == 12:
                img.swirl(degree=-90)  # type: ignore
            elif choice == 13:
                img.tint(color="yellow", alpha="rgb(40%, 60%, 80%)")  # type: ignore
            else:
                buffer = BytesIO(self.original)  # type: ignore
                img.save(buffer)  # type: ignore
                buffer.seek(0)
                f = discord.File(buffer, filename="original_user_avatar.png")

                if self.add_once:
                    self.new_embed.add_field(
                        name=self.embed.fields[0].name, value=self.embed.fields[0].value
                    )
                    self.add_once = False
                self.new_embed.set_image(url="attachment://original_user_avatar.png")

                await self.i.edit_original_response(
                    attachments=[f], embed=self.new_embed
                )
                await msg.delete()
                return None

            image_bytes: bytes = to_bytes(img.make_blob())  # type: ignore
            buffer = BytesIO(image_bytes)  # type: ignore
            img.save(buffer)  # type: ignore

        buffer.seek(0)
        f = discord.File(buffer, filename="user_avatar.png")

        if self.add_once:
            self.new_embed.add_field(
                name=self.embed.fields[0].name, value=self.embed.fields[0].value
            )
            self.add_once = False
        self.new_embed.set_image(url="attachment://user_avatar.png")
        try:
            await self.i.edit_original_response(attachments=[f], embed=self.new_embed)
        except discord.HTTPException:
            await self.i.channel.send("You need to use the `/avatar` command again to use this")  # type: ignore
        await msg.delete()

    return inner


class FilterView(ui.View):
    __slots__ = (
        "i",
        "embed",
        "bot",
        "new_embed",
        "add_once",
        "bytes_image",
        "original",
    )

    def __init__(self, i: discord.Interaction, embed: discord.Embed, bot: Bot):
        super().__init__(timeout=14 * 60)
        self.i = i
        self.embed = embed
        self.image = embed.image.url
        self.bot = bot
        self.new_embed = discord.Embed(colour=discord.Colour.random())
        self.add_once: bool = True
        self.bytes_image: bytes
        self.original: bytes

    def disabled(self):
        for btn in self.children:
            btn.disabled = True  # type: ignore
        return self

    async def on_timeout(self):
        self.stop()
        msg = await self.i.original_response()
        if msg:
            if self.add_once:
                await self.i.edit_original_response(
                    embed=self.embed, view=self.disabled()
                )
            else:
                await self.i.edit_original_response(
                    embed=self.new_embed, view=self.disabled()
                )
            # await msg.reply(
            #     "This view just timed out, I suppose! You need to interact with it to keep it up, in fact!"
            # )

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        await interaction.response.defer()
        cond: bool = interaction.user == self.i.user
        if not cond:
            await interaction.followup.send(
                "That's not your view, in fact!", ephemeral=True
            )
        return cond

    @apply_filter
    async def update(self, choice: int) -> None:
        session: ClientSession = self.bot.session
        url: Optional[str] = self.image
        if url:
            async with session.get(url) as resp:
                if resp.status == 200:
                    self.bytes_image = await resp.read()
                    self.original = self.bytes_image

    @ui.button(
        label="Blur", style=discord.ButtonStyle.blurple, custom_id="persistent:blur"
    )
    async def opt_one(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(0)

    @ui.button(
        label="Shade", style=discord.ButtonStyle.blurple, custom_id="persistent:shade"
    )
    async def opt_two(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(1)

    @ui.button(
        label="Sharpen",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent:sharpen",
    )
    async def opt_three(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(2)

    @ui.button(
        label="Spread", style=discord.ButtonStyle.blurple, custom_id="persistent:spread"
    )
    async def opt_four(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(3)

    @ui.button(
        label="Edge", style=discord.ButtonStyle.blurple, custom_id="persistent:edge"
    )
    async def opt_five(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(4)

    @ui.button(
        label="Emboss", style=discord.ButtonStyle.blurple, custom_id="persistent:emboss"
    )
    async def opt_six(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(5)

    @ui.button(
        label="Charcoal",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent:charcoal",
    )
    async def opt_seven(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(6)

    @ui.button(
        label="Wave", style=discord.ButtonStyle.blurple, custom_id="persistent:wave"
    )
    async def opt_eight(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(7)

    @ui.button(
        label="Colorize",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent:colorize",
    )
    async def opt_nine(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(8)

    @ui.button(
        label="Sepia", style=discord.ButtonStyle.blurple, custom_id="persistent:sepia"
    )
    async def opt_ten(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(9)

    @ui.button(
        label="Sketch", style=discord.ButtonStyle.blurple, custom_id="persistent:sketch"
    )
    async def opt_eleven(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(10)

    @ui.button(
        label="Solarize",
        style=discord.ButtonStyle.blurple,
        custom_id="persistent:solarize",
    )
    async def opt_twelve(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(11)

    @ui.button(
        label="Swirl", style=discord.ButtonStyle.blurple, custom_id="persistent:swirl"
    )
    async def opt_thirteen(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(12)

    @ui.button(
        label="Tint", style=discord.ButtonStyle.blurple, custom_id="persistent:tint"
    )
    async def opt_fourteen(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(13)

    @ui.button(
        label="Reset", style=discord.ButtonStyle.red, custom_id="persistent:reset"
    )
    async def opt_reset(
        self, interaction: discord.Interaction, button: discord.ui.Button[Self]
    ):
        await self.update(14)

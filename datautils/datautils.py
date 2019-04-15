from typing import Union

import discord
import matplotlib.colors as colors
import tabulate

from redbot.core import checks
from redbot.core import commands
from redbot.core.utils import chat_formatting as chat
from redbot.core.utils.menus import menu, DEFAULT_CONTROLS
from redbot.core.i18n import Translator, cog_i18n

_ = Translator("ExampleCog", __file__)

def rgb_to_hex(rgb_tuple):
    return colors.rgb2hex([1.0 * x / 255 for x in rgb_tuple])


def bool_emojify(bool_var: bool) -> str:
    return "✅" if bool_var else "❌"

@cog_i18n(_)
class DataUtils(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.command()
    @checks.bot_has_permissions(embed_links=True)
    async def getuserinfo(self, ctx, user_id: int):
        """Get info about any Discord's user by ID"""
        try:
            user = await self.bot.get_user_info(user_id)
        except discord.NotFound:
            await ctx.send(_(
                chat.error("Discord user with ID `{}` not found").format(user_id)
            ))
            return
        except discord.HTTPException:
            await ctx.send(_(
                chat.warning(
                    "Bot was unable to get data about user with ID `{}`. "
                    "Try again later".format(user_id)
                )
            ))
            return
        embed = discord.Embed(
            title=chat.escape(str(user), formatting=True),
            timestamp=user.created_at,
            color=await ctx.embed_color(),
        )
        embed.add_field(name="ID", value=user.id)
        embed.add_field(name="Bot?", value=bool_emojify(user.bot))
        embed.add_field(name="Mention", value=user.mention)
        embed.add_field(
            name="Default avatar",
            value="[{}]({})".format(user.default_avatar, user.default_avatar_url),
        )
        if user.avatar:
            embed.add_field(
                name="Avatar",
                value="[`{}`]({})".format(
                    user.avatar, user.avatar_url_as(static_format="png", size=2048)
                ),
            )
        embed.set_image(url=user.avatar_url_as(static_format="png", size=2048))
        embed.set_thumbnail(url=user.default_avatar_url)
        embed.set_footer(text="Created at")
        await ctx.send(embed=embed)

    @commands.command(aliases=["memberinfo", "membinfo"])
    @commands.guild_only()
    @checks.bot_has_permissions(embed_links=True)
    async def uinfo(self, ctx, *, member: discord.Member = None):
        """Information on a user"""
        if member is None:
            member = ctx.message.author
        em = discord.Embed(
            title=member.nick and chat.escape(member.nick, formatting=True) or None,
            color=member.color.value and member.color or discord.Embed.Empty,
        )
        em.add_field(name="Name", value=member.name)
        em.add_field(
            name="Client",
            value="📱: {}\n"
            "🖥: {}\n"
            "🌎: {}".format(
                str(member.mobile_status).capitalize(),
                str(member.desktop_status).capitalize(),
                str(member.web_status).capitalize(),
            ),
        )
        em.add_field(
            name="Joined server",
            value=member.joined_at.strftime("%d.%m.%Y %H:%M:%S %Z"),
        )
        em.add_field(name="ID", value=member.id)
        em.add_field(
            name="Has existed since",
            value=member.created_at.strftime("%d.%m.%Y %H:%M:%S %Z"),
        )
        if member.color.value:
            em.add_field(name="Color", value=member.colour)
        em.add_field(name="Bot?", value=bool_emojify(member.bot))
        em.add_field(
            name="Server perms",
            value="[{0}](https://discordapi.com/permissions.html#{0})".format(
                member.guild_permissions.value
            ),
        )
        em.add_field(
            name="Mention",
            value="{}\n{}".format(member.mention, chat.inline(member.mention)),
        )
        em.add_field(
            name="Roles",
            value="\n".join(
                [role.name for role in member.roles if not role.is_default()]
            )
            or "❌",
            inline=False,
        )
        em.set_image(url=member.avatar_url_as(static_format="png", size=2048))
        em.set_thumbnail(
            url="https://xenforo.com/community/rgba.php?r="
            + str(member.colour.r)
            + "&g="
            + str(member.colour.g)
            + "&b="
            + str(member.colour.b)
            + "&a=255"
        )
        await ctx.send(embed=em)

    @commands.command(aliases=["servinfo", "serv", "sv"])
    @commands.guild_only()
    @checks.is_owner()
    @checks.bot_has_permissions(embed_links=True)
    async def sinfo(self, ctx, *, server: int = None):
        """Shows server information"""
        if server is None:
            server = ctx.guild
        else:
            server = self.bot.get_guild(server)
        if server is None:
            await ctx.send("Failed to get server with provided ID")
            return
        afk = server.afk_timeout / 60
        vip_regs = bool_emojify("VIP_REGIONS" in server.features)
        van_url = bool_emojify("VANITY_URL" in server.features)
        verified = bool_emojify("VERIFIED" in server.features)
        emoji_ext = bool_emojify("MORE_EMOJI" in server.features)
        inv_splash = "INVITE_SPLASH" in server.features
        em = discord.Embed(
            title="Server info",
            color=server.owner.color.value
            and server.owner.color
            or discord.Embed.Empty,
        )
        em.add_field(name="Name", value=chat.escape(server.name, formatting=True))
        em.add_field(name="Server ID", value=server.id)
        em.add_field(name="Region", value=server.region)
        em.add_field(
            name="Existed since",
            value=server.created_at.strftime("%d.%m.%Y %H:%M:%S %Z"),
        )
        em.add_field(
            name="Owner", value=chat.escape(str(server.owner), formatting=True)
        )
        em.add_field(
            name="AFK Timeout and Channel",
            value="{} min in {}".format(
                afk, chat.escape(str(server.afk_channel), formatting=True)
            ),
        )
        em.add_field(
            name="New member messages channel",
            value=chat.escape(str(server.system_channel), formatting=True),
        )
        em.add_field(
            name="Verification level",
            value="None"
            if server.verification_level == discord.VerificationLevel.none
            else "Low"
            if server.verification_level == discord.VerificationLevel.low
            else "Medium"
            if server.verification_level == discord.VerificationLevel.medium
            else "(╯°□°）╯︵ ┻━┻"
            if server.verification_level == discord.VerificationLevel.high
            else "┻━┻ ﾐヽ(ಠ益ಠ)ノ彡┻━┻"
            if server.verification_level == discord.VerificationLevel.extreme
            else "Unknown",
        )
        em.add_field(
            name="Explicit content filter",
            value="Don't scan any messages."
            if server.explicit_content_filter == discord.ContentFilter.disabled
            else "Scan messages from members without a role."
            if server.explicit_content_filter == discord.ContentFilter.no_role
            else "Scan messages sent by all members."
            if server.explicit_content_filter == discord.ContentFilter.all_members
            else "Unknown",
        )
        em.add_field(
            name="Default notifications",
            value="All messages"
            if server.default_notifications == discord.NotificationLevel.all_messages
            else "Only @mentions"
            if server.default_notifications == discord.NotificationLevel.only_mentions
            else "Unknown",
        )
        em.add_field(name="2FA admins", value=bool_emojify(server.mfa_level))
        em.add_field(name="Member Count", value=server.member_count)
        em.add_field(name="Role Count", value=str(len(server.roles)))
        em.add_field(name="Channel Count", value=str(len(server.channels)))
        em.add_field(name="VIP Voice Regions", value=vip_regs)
        em.add_field(name="Vanity URL", value=van_url)
        em.add_field(name="Verified", value=verified)
        em.add_field(name="Extended emoji limit", value=emoji_ext)
        if not inv_splash:
            em.add_field(name="Invite Splash", value="❌")
        elif not server.splash_url:
            em.add_field(name="Invite Splash", value="✅")
        else:
            em.add_field(
                name="Invite Splash",
                value="✅ [🔗](" + server.splash_url_as(format="png", size=2048) + ")",
            )
        em.set_image(url=server.icon_url_as(format="png", size=2048))
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    @checks.is_owner()
    @checks.bot_has_permissions(embed_links=True)
    async def bans(self, ctx: commands.Context, *, server: int = None):
        """Get bans from server by id"""
        if server is None:
            server = ctx.guild
        else:
            server = self.bot.get_guild(server)
        if server is None:
            await ctx.send(_("Failed to get server with provided ID"))
            return
        if not server.me.guild_permissions.ban_members:
            await ctx.send(_(
                'I need permission "Ban Members" to access banned members on server'
            ))
            return
        banlist = await server.bans()
        if banlist:
            banlisttext = "\n".join(
                ["{} ({})".format(x.user, x.user.id) for x in banlist]
            )
            pages = [chat.box(page) for page in list(chat.pagify(banlisttext))]
            await menu(ctx, pages, DEFAULT_CONTROLS)
        else:
            await ctx.send(_("Banlist is empty!"))

    @commands.command()
    @commands.guild_only()
    @checks.is_owner()
    @checks.bot_has_permissions(embed_links=True)
    async def invites(self, ctx: commands.Context, *, server: int = None):
        """Get invites from server by id"""
        if server is None:
            server = ctx.guild
        else:
            server = self.bot.get_guild(server)
        if server is None:
            await ctx.send(_("Failed to get server with provided ID"))
            return
        if not server.me.guild_permissions.manage_guild:
            await ctx.send(_(
                'I need permission "Manage Server" to access list of invites on server'
            ))
            return
        invites = await server.invites()
        if invites:
            inviteslist = "\n".join(
                ["{} ({})".format(x, x.channel.name) for x in invites]
            )
            await menu(ctx, list(chat.pagify(inviteslist)), DEFAULT_CONTROLS)
        else:
            await ctx.send(_("There is no invites for this server"))

    @commands.command(aliases=["chaninfo", "channelinfo"])
    @commands.guild_only()
    @checks.bot_has_permissions(embed_links=True)
    async def cinfo(
        self,
        ctx,
        *,
        channel: Union[
            discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, None
        ] = None
    ):
        """Get info about channel"""
        if channel is None:
            channel = ctx.channel
        changed_roles = sorted(
            channel.changed_roles, key=lambda r: r.position, reverse=True
        )
        em = discord.Embed(
            title=chat.escape(str(channel.name), formatting=True),
            description=channel.topic
            if isinstance(channel, discord.TextChannel)
            else "💬: {} | 🔈: {}".format(
                len(channel.text_channels), len(channel.voice_channels)
            )
            if isinstance(channel, discord.CategoryChannel)
            else None,
            color=await ctx.embed_color(),
        )
        em.add_field(name="ID", value=channel.id)
        em.add_field(
            name="Type",
            value="🔈"
            if isinstance(channel, discord.VoiceChannel)
            else "💬"
            if isinstance(channel, discord.TextChannel)
            else "📑"
            if isinstance(channel, discord.CategoryChannel)
            else "❔",
        )
        em.add_field(
            name="Has existed since",
            value=channel.created_at.strftime("%d.%m.%Y %H:%M:%S %Z"),
        )
        em.add_field(
            name="Category",
            value=chat.escape(str(channel.category), formatting=True)
            or chat.inline("Not in category"),
        )
        em.add_field(name="Position", value=channel.position)
        em.add_field(
            name="Changed roles permissions",
            value="\n".join([str(x) for x in changed_roles]) or "`Not set`",
        )
        em.add_field(
            name="Mention",
            value="{}\n{}".format(channel.mention, chat.inline(channel.mention)),
        )
        if isinstance(channel, discord.TextChannel):
            if channel.slowmode_delay:
                em.add_field(
                    name="Slowmode delay",
                    value="{} seconds".format(channel.slowmode_delay),
                )
            em.add_field(name="NSFW", value=bool_emojify(channel.is_nsfw()))
            if (
                    channel.guild.me.permissions_in(channel).manage_webhooks
                    and await channel.webhooks()
            ):
                em.add_field(
                    name="Webhooks count", value=str(len(await channel.webhooks()))
                )
        elif isinstance(channel, discord.VoiceChannel):
            em.add_field(name="Bitrate", value="{}kbps".format(channel.bitrate / 1000))
            em.add_field(
                name="Users",
                value=channel.user_limit
                and "{}/{}".format(len(channel.members), channel.user_limit)
                or "{}".format(len(channel.members)),
            )
        elif isinstance(channel, discord.CategoryChannel):
            em.add_field(name="NSFW", value=bool_emojify(channel.is_nsfw()))
        await ctx.send(embed=em)

    @commands.command(aliases=["channellist", "listchannels"])
    @commands.guild_only()
    @checks.is_owner()
    @checks.bot_has_permissions(embed_links=True)
    async def channels(self, ctx, *, server: int = None):
        """Get all channels on server"""
        if server is None:
            server = ctx.guild
        else:
            server = discord.utils.get(self.bot.guilds, id=server)
        if server is None:
            await ctx.send(_("Failed to get server with provided ID"))
            return
        categories = (
            "\n".join([chat.escape(x.name, formatting=True) for x in server.categories])
            or "No categories"
        )
        text_channels = (
            "\n".join(
                [chat.escape(x.name, formatting=True) for x in server.text_channels]
            )
            or "No text channels"
        )
        voice_channels = (
            "\n".join(
                [chat.escape(x.name, formatting=True) for x in server.voice_channels]
            )
            or "No voice channels"
        )
        em = discord.Embed(title="Channels list", color=await ctx.embed_color())
        em.add_field(name="Categories:", value=categories, inline=False)
        em.add_field(name="Text channels:", value=text_channels, inline=False)
        em.add_field(name="Voice channels:", value=voice_channels, inline=False)
        em.set_footer(
            text="Total count of channels: {} • "
            "Categories: {} • "
            "Text Channels: {} • "
            "Voice Channels: {}".format(
                len(server.channels),
                len(server.categories),
                len(server.text_channels),
                len(server.voice_channels),
            )
        )
        await ctx.send(embed=em)

    @commands.command(aliases=["roleinfo"])
    @commands.guild_only()
    @checks.bot_has_permissions(embed_links=True)
    async def rinfo(self, ctx, *, role: discord.Role):
        """Get info about role"""
        em = discord.Embed(
            title=chat.escape(role.name, formatting=True),
            color=role.color.value and role.color or discord.Embed.Empty,
        )
        em.add_field(name="ID", value=role.id)
        em.add_field(
            name="Perms",
            value="[{0}](https://discordapi.com/permissions.html#{0})".format(
                role.permissions.value
            ),
        )
        em.add_field(
            name="Has existed since",
            value=role.created_at.strftime("%d.%m.%Y %H:%M:%S %Z"),
        )
        em.add_field(name="Hoist", value=bool_emojify(role.hoist))
        em.add_field(name="Members", value=str(len(role.members)))
        em.add_field(name="Position", value=role.position)
        em.add_field(name="Color", value=role.colour)
        em.add_field(name="Managed", value=bool_emojify(role.managed))
        em.add_field(name="Mentionable", value=bool_emojify(role.mentionable))
        em.add_field(name="Mention", value=role.mention + "\n`" + role.mention + "`")
        em.set_thumbnail(
            url="https://xenforo.com/community/rgba.php?r="
            + str(role.colour.r)
            + "&g="
            + str(role.colour.g)
            + "&b="
            + str(role.colour.b)
            + "&a=255"
        )
        await ctx.send(embed=em)

    @commands.command()
    @commands.guild_only()
    async def rolemembers(self, ctx, *, role: discord.Role):
        """Get list of members that has provided role"""
        memberslist = [str(m) for m in sorted(role.members, key=lambda m: m.joined_at)]
        pages = [
            discord.Embed(description=p, color=await ctx.embed_color())
            for p in chat.pagify("\n".join(memberslist), page_length=2048)
        ]
        pagenum = 1
        for page in pages:
            page.set_footer(text="Page {}/{}".format(pagenum, len(pages)))
            pagenum += 1
        await menu(ctx, pages, DEFAULT_CONTROLS)

    @commands.command(aliases=["listroles", "rolelist"])
    @commands.guild_only()
    @checks.is_owner()
    async def roles(self, ctx, server: int = None):
        """Get all roles on server"""
        if server is None:
            server = ctx.guild
        else:
            server = self.bot.get_guild(server)
        if server is None:
            await ctx.send(_("Failed to get server with provided ID"))
            return
        roles = []
        for role in server.roles:
            dic = {"Name": await self.smart_truncate(role.name), "ID": role.id}
            roles.append(dic)
        pages = list(chat.pagify(tabulate.tabulate(roles, tablefmt="orgtbl")))
        pages = [chat.box(p) for p in pages]
        await menu(ctx, pages, DEFAULT_CONTROLS)

    @commands.command(aliases=["cperms"])
    @commands.guild_only()
    @checks.admin_or_permissions(administrator=True)
    async def chanperms(
        self,
        ctx,
        member: discord.Member,
        *,
        channel: Union[
            discord.TextChannel, discord.VoiceChannel, discord.CategoryChannel, None
        ] = None
    ):
        """Check user's permission for current or provided channel"""
        if channel is None:
            channel = ctx.channel
        perms = channel.permissions_for(member)
        await ctx.send(_(
            "{}\n{}".format(
                chat.inline(str(member.guild_permissions.value)),
                chat.box(chat.format_perms_list(perms), lang="py"),
            )
        ))

    @commands.command(aliases=["emojiinfo", "emojinfo"])
    @commands.guild_only()
    @checks.bot_has_permissions(embed_links=True)
    async def einfo(
            self, ctx, *, emoji: Union[discord.Emoji, discord.PartialEmoji, None]
    ):
        """Get info about emoji"""
        if emoji is None:
            await ctx.send_help()
            return
        em = discord.Embed(
            title=chat.escape(emoji.name, formatting=True),
            color=await ctx.embed_color(),
        )
        em.add_field(name="ID", value=emoji.id)
        em.add_field(name="Animated", value=bool_emojify(emoji.animated))
        if isinstance(emoji, discord.Emoji):
            em.add_field(
                name="Has existed since",
                value=emoji.created_at.strftime("%d.%m.%Y %H:%M:%S %Z"),
            )
            em.add_field(name='":" required', value=bool_emojify(emoji.require_colons))
            em.add_field(name="Managed", value=bool_emojify(emoji.managed))
            em.add_field(name="Server", value=emoji.guild)
            if emoji.roles:
                em.add_field(
                    name="Roles", value="\n".join([x.name for x in emoji.roles])
                )
        elif isinstance(emoji, discord.PartialEmoji):
            em.add_field(
                name="Custom emoji", value=bool_emojify(emoji.is_custom_emoji())
            )
            em.add_field(
                name="Unicode emoji", value=bool_emojify(emoji.is_unicode_emoji())
            )
        em.set_image(url=emoji.url)
        await ctx.send(embed=em)

    async def smart_truncate(self, content, length=32, suffix="…"):
        """https://stackoverflow.com/questions/250357/truncate-a-string-without-ending-in-the-middle-of-a-word"""
        content_str = str(content)
        if len(content_str) <= length:
            return content
        return " ".join(content_str[: length + 1].split(" ")[0:-1]) + suffix

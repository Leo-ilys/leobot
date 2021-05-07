# Jmthon


from asyncio import sleep

from telethon import functions
from telethon.errors import (
    BadRequestError,
    ImageProcessFailedError,
    PhotoCropSizeSmallError,
)
from telethon.errors.rpcerrorlist import UserAdminInvalidError, UserIdInvalidError
from telethon.tl.functions.channels import (
    EditAdminRequest,
    EditBannedRequest,
    EditPhotoRequest,
)
from telethon.tl.functions.users import GetFullUserRequest
from telethon.tl.types import ChatAdminRights, ChatBannedRights, MessageMediaPhoto

from ..utils import errors_handler
from . import BOTLOG, BOTLOG_CHATID, LOGS, get_user_from_event
from .sql_helper.mute_sql import is_muted, mute, unmute

#  @Jmthon

PP_TOO_SMOL = "⪼ **الصورة صغيرة جدًا** ⌁."
PP_ERROR = "⪼ **فشل أثناء معالجة الصورة** ⌁."
NO_ADMIN = "⪼ **أنا لست مشرف هنا!!** ⌁."
NO_PERM = "⪼ **ليس لدي أذونات كافية!** ⌁."
CHAT_PP_CHANGED = "⪼ **تغيرت صورة الدردشة** ⌁."
INVALID_MEDIA = "⪼ **ملحق غير صالح** ⌁."

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)
UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)

# ================================================


@bot.on(admin_cmd(pattern="ضع صوره$"))
@bot.on(sudo_cmd(pattern="ضع صوره$", allow_sudo=True))
@errors_handler
async def set_group_photo(gpic):
    if gpic.fwd_from:
        return
    if not gpic.is_group:
        await edit_or_reply(gpic, "**لا أعتقد أن هذه مجموعة ⨉**")
        return
    replymsg = await gpic.get_reply_message()
    await gpic.get_chat()
    photo = None
    if replymsg and replymsg.media:
        if isinstance(replymsg.media, MessageMediaPhoto):
            photo = await gpic.client.download_media(message=replymsg.photo)
        elif "image" in replymsg.media.document.mime_type.split("/"):
            photo = await gpic.client.download_file(replymsg.media.document)
        else:
            await edit_or_reply(gpic, INVALID_MEDIA)
    sandy = None
    if photo:
        try:
            await gpic.client(
                EditPhotoRequest(gpic.chat_id, await gpic.client.upload_file(photo))
            )
            await edit_or_reply(gpic, CHAT_PP_CHANGED)
            sandy = True
        except PhotoCropSizeSmallError:
            await edit_or_reply(gpic, PP_TOO_SMOL)
        except ImageProcessFailedError:
            await edit_or_reply(gpic, PP_ERROR)
        except Exception as e:
            await edit_or_reply(gpic, f"**Error : **`{str(e)}`")
        if BOTLOG and sandy:
            await gpic.client.send_message(
                BOTLOG_CHATID,
                "#صوره_المجموعه\n"
                f"تغير صوره المجموعه "
                f"الدردشه: {gpic.chat.title}(`{gpic.chat_id}`)",
            )


@bot.on(admin_cmd(pattern="رفع مشرف(?: |$)(.*)", command="promote"))
@bot.on(sudo_cmd(pattern="رفع مشرف(?: |$)(.*)", command="promote", allow_sudo=True))
@errors_handler
async def promote(promt):
    if promt.fwd_from:
        return
    if not promt.is_group:
        await edit_or_reply(promt, "**لا أعتقد أن هذه مجموعة ⨉**")
        return
    chat = await promt.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(promt, NO_ADMIN)
        return
    new_rights = ChatAdminRights(
        add_admins=False,
        invite_users=True,
        change_info=False,
        ban_users=False,
        delete_messages=True,
        pin_messages=True,
    )
    catevent = await edit_or_reply(promt, "جاري رفع مشرف")
    user, rank = await get_user_from_event(promt, catevent)
    if not rank:
        rank = "مشرف"
    if not user:
        return
    try:
        await promt.client(EditAdminRequest(promt.chat_id, user.id, new_rights, rank))
        await catevent.edit("**-  ⌊  تم تـرقيتـه مشـرف .**")
    except BadRequestError:
        await catevent.edit(NO_PERM)
        return
    if BOTLOG:
        await promt.client.send_message(
            BOTLOG_CHATID,
            "#مشرف\n"
            f"المستخدم: [{user.first_name}](tg://user?id={user.id})\n"
            f"الدردشه: {promt.chat.title}(`{promt.chat_id}`)",
        )


#  @Jmthon #


@bot.on(admin_cmd(pattern="رفع مالك(?: |$)(.*)", command="promote"))
@bot.on(sudo_cmd(pattern="رفع مالك(?: |$)(.*)", command="promote", allow_sudo=True))
@errors_handler
async def promote(promt):
    if promt.fwd_from:
        return
    if not promt.is_group:
        await edit_or_reply(promt, "**لا أعتقد أن هذه مجموعة ⨉**")
        return
    chat = await promt.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(promt, NO_ADMIN)
        return
    new_rights = ChatAdminRights(
        add_admins=True,
        invite_users=True,
        change_info=True,
        ban_users=True,
        delete_messages=True,
        pin_messages=True,
    )
    catevent = await edit_or_reply(promt, "**╮   جـاري ࢪفعه مالك  ╰**")
    user, rank = await get_user_from_event(promt, catevent)
    if not rank:
        rank = "المالك²"
    if not user:
        return
    try:
        await promt.client(EditAdminRequest(promt.chat_id, user.id, new_rights, rank))
        await catevent.edit("**- ❝ ⌊  تم تـرقيتـه مالك .**")
    except BadRequestError:
        await catevent.edit(NO_PERM)
        return
    if BOTLOG:
        await promt.client.send_message(
            BOTLOG_CHATID,
            "#مالك\n"
            f"المستخدم: [{user.first_name}](tg://user?id={user.id})\n"
            f"الدردشه: {promt.chat.title}(`{promt.chat_id}`)",
        )


#  @Jmthon #


@bot.on(admin_cmd(pattern="تك(?: |$)(.*)", command="demote"))
@bot.on(sudo_cmd(pattern="تك(?: |$)(.*)", command="demote", allow_sudo=True))
@errors_handler
async def demote(dmod):
    if dmod.fwd_from:
        return
    if not dmod.is_group:
        await edit_or_reply(dmod, "**لا أعتقد أن هذه مجموعة ⨉**")
        return
    chat = await dmod.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(dmod, NO_ADMIN)
        return
    catevent = await edit_or_reply(dmod, "↮")
    rank = "مشرف"
    user = await get_user_from_event(dmod, catevent)
    user = user[0]
    if not user:
        return
    newrights = ChatAdminRights(
        add_admins=None,
        invite_users=None,
        change_info=None,
        ban_users=None,
        delete_messages=None,
        pin_messages=None,
    )
    try:
        await dmod.client(EditAdminRequest(dmod.chat_id, user.id, newrights, rank))
    except BadRequestError:
        await catevent.edit(NO_PERM)
        return
    await catevent.edit("**- ❝ ⌊  تم تنزلـيه من الاشـرف بنجـاح  ⌁.**")
    if BOTLOG:
        await dmod.client.send_message(
            BOTLOG_CHATID,
            "#تنزيل_مشرف\n"
            f"المستخدم: [{user.first_name}](tg://user?id={user.id})\n"
            f"الدردشه: {dmod.chat.title}(`{dmod.chat_id}`)",
        )


@bot.on(admin_cmd(pattern="دي(?: |$)(.*)", command="ban"))
@bot.on(sudo_cmd(pattern="دي(?: |$)(.*)", command="ban", allow_sudo=True))
@errors_handler
async def ban(bon):
    if bon.fwd_from:
        return
    if not bon.is_group:
        await edit_or_reply(bon, "**لا أعتقد أن هذه مجموعة ⨉**")
        return
    chat = await bon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(bon, NO_ADMIN)
        return
    catevent = await edit_or_reply(bon, "**╮   جـاري حظره  ╰**")
    user, reason = await get_user_from_event(bon, catevent)
    if not user:
        return
    try:
        await bon.client(EditBannedRequest(bon.chat_id, user.id, BANNED_RIGHTS))
    except BadRequestError:
        await catevent.edit(NO_PERM)
        return
    try:
        reply = await bon.get_reply_message()
        if reply:
            await reply.delete()
    except BadRequestError:
        await catevent.edit(
            "**  ليس لدي صلاحيـة حذف الرسـائل لڪنه لايـزال محظـور ،**"
        )
        return
    if reason:
        await catevent.edit(
            f"{_format.mentionuser(user.first_name ,user.id)}` محظور !!\n دقيقه: {reason}"
        )
    else:
        await catevent.edit(
            f"{_format.mentionuser(user.first_name ,user.id)}  محظور !!"
        )
    if BOTLOG:
        await bon.client.send_message(
            BOTLOG_CHATID,
            "#حظر\n"
            f"المستخدم: [{user.first_name}](tg://user?id={user.id})\n"
            f"الدردشه: {bon.chat.title}(`{bon.chat_id}`)",
        )


# @Jmthon


@bot.on(admin_cmd(pattern="رفع القيود(?: |$)(.*)", command="unban"))
@bot.on(sudo_cmd(pattern="رفع القيود(?: |$)(.*)", command="unban", allow_sudo=True))
@errors_handler
async def nothanos(unbon):
    if unbon.fwd_from:
        return
    chat = await unbon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(unbon, NO_ADMIN)
        return
    catevent = await edit_or_reply(unbon, "جاري رفع القيود")
    user = await get_user_from_event(unbon)
    user = user[0]
    if not user:
        return
    try:
        await unbon.client(EditBannedRequest(unbon.chat_id, user.id, UNBAN_RIGHTS))
        await catevent.edit("تم رفع جميع القيود")
        if BOTLOG:
            await unbon.client.send_message(
                BOTLOG_CHATID,
                "#رفع_القيود\n"
                f"المستخدم: [{user.first_name}](tg://user?id={user.id})\n"
                f"الدردشه: {unbon.chat.title}(`{unbon.chat_id}`)",
            )
    except UserIdInvalidError:
        await catevent.edit("لايمكنني رفع القيود عنه")


@bot.on(admin_cmd(incoming=True))
async def watcher(event):
    if is_muted(event.sender_id, event.chat_id):
        try:
            await event.delete()
        except Exception as e:
            LOGS.info(str(e))


@bot.on(admin_cmd(pattern="تقيد(?: |$)(.*)", command="mute"))
@bot.on(sudo_cmd(pattern="تقيد(?: |$)(.*)", command="mute", allow_sudo=True))
async def startmute(event):
    if event.fwd_from:
        return
    if event.is_private:
        await event.edit("قد تحدث مشاكل غير متوقعة أو أخطاء")
        await sleep(3)
        await event.get_reply_message()
        userid = event.chat_id
        replied_user = await event.client(GetFullUserRequest(userid))
        chat_id = event.chat_id
        if is_muted(userid, chat_id):
            return await event.edit("المستخدم مقيد بالفعل~~")
        try:
            mute(userid, chat_id)
        except Exception as e:
            await event.edit("حدث خطأ!\nالخطأ هو " + str(e))
        else:
            await event.edit("تم تقيده")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#تقيد\n"
                f"المستخدم: [{replied_user.user.first_name}](tg://user?id={userid})\n"
                f"الدردشه: {event.chat.title}(`{event.chat_id}`)",
            )
    else:
        chat = await event.get_chat()
        user, reason = await get_user_from_event(event)
        if not user:
            return
        if user.id == bot.uid:
            return await edit_or_reply(event, "لا استطيع تقيد نفسي")
        if is_muted(user.id, event.chat_id):
            return await edit_or_reply(event, "المستخدم مقيد بالفعل~~")
        try:
            admin = chat.admin_rights
            creator = chat.creator
            if not admin and not creator:
                await edit_or_reply(event, " لايمكنني تقيد شخص بدون صلاحيات المشرفين ")
                return
            result = await event.client(
                functions.channels.GetParticipantRequest(
                    channel=event.chat_id, user_id=user.id
                )
            )
            try:
                if result.participant.banned_rights.send_messages:
                    return await edit_or_reply(
                        event,
                        "مقيد بالفعل~~",
                    )
            except:
                pass
            await event.client(EditBannedRequest(event.chat_id, user.id, MUTE_RIGHTS))
        except UserAdminInvalidError:
            if "admin_rights" in vars(chat) and vars(chat)["admin_rights"] is not None:
                if chat.admin_rights.delete_messages is not True:
                    return await edit_or_reply(
                        event,
                        "لا يمكنك كتم أي شخص إذا لم يكن لديك إذن حذف الرسائل",
                    )
            elif "creator" not in vars(chat):
                return await edit_or_reply(
                    event, "لا يمكنك كتم أي شخص بدون صلاحيه مشرفين  "
                )
            try:
                mute(user.id, event.chat_id)
            except Exception as e:
                return await edit_or_reply(event, "حدث خطأ!\nالخطأ هو " + str(e))
        except Exception as e:
            return await edit_or_reply(event, f"**خطأ : **`{str(e)}`")
        if reason:
            await edit_or_reply(
                event,
                f" المستخدم ↫[{user.first_name}](tg://user?id={user.id})تم تقيده بنجاح✅"
                #                 f"`Reason:`{reason}",
            )
        else:
            await edit_or_reply(
                event,
                f"المستخدم ↫[{user.first_name}](tg://user?id={user.id})تم تقيده بنجاح✅",
            )
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#تقيد\n"
                f"المستخدم: [{user.first_name}](tg://user?id={user.id})\n"
                f"الدردشه: {event.chat.title}(`{event.chat_id}`)",
            )


@bot.on(admin_cmd(pattern="الغاء تقيد(?: |$)(.*)", command="unmute"))
@bot.on(sudo_cmd(pattern="الغاء تقيد(?: |$)(.*)", command="unmute", allow_sudo=True))
async def endmute(event):
    if event.fwd_from:
        return
    if event.is_private:
        await event.edit("قد تحدث مشاكل غير متوقعة أو أخطاء")
        await sleep(3)
        userid = event.chat_id
        replied_user = await event.client(GetFullUserRequest(userid))
        chat_id = event.chat_id
        if not is_muted(userid, chat_id):
            return await event.edit("⋮هذا المستخدم غير مقيد هنا")
        try:
            unmute(userid, chat_id)
        except Exception as e:
            await event.edit("حدث خطأ!\nالخطأ هو " + str(e))
        else:
            await event.edit("**تم رفع القيود عنه**")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#رفع_القيود\n"
                f"المستخدم: [{replied_user.user.first_name}](tg://user?id={userid})\n"
                f"الدردشه: {event.chat.title}(`{event.chat_id}`)",
            )
    else:
        user = await get_user_from_event(event)
        user = user[0]
        if not user:
            return
        try:
            if is_muted(user.id, event.chat_id):
                unmute(user.id, event.chat_id)
            else:
                result = await event.client(
                    functions.channels.GetParticipantRequest(
                        channel=event.chat_id, user_id=user.id
                    )
                )
                try:
                    if result.participant.banned_rights.send_messages:
                        await event.client(
                            EditBannedRequest(event.chat_id, user.id, UNBAN_RIGHTS)
                        )
                except:
                    return await edit_or_reply(
                        event,
                        "هذا المستخدم غير مقيد هنا~~",
                    )
        except Exception as e:
            return await edit_or_reply(event, f"**خطأ : **`{str(e)}`")
        await edit_or_reply(event, "**تم رفع القيود عنه**")
        if BOTLOG:
            await event.client.send_message(
                BOTLOG_CHATID,
                "#رفع_القيود\n"
                f"المستخدم: [{user.first_name}](tg://user?id={user.id})\n"
                f"الدردشه: {event.chat.title}(`{event.chat_id}`)",
            )


@bot.on(admin_cmd(pattern="طرد(?: |$)(.*)", command="kick"))
@bot.on(sudo_cmd(pattern="طرد(?: |$)(.*)", command="kick", allow_sudo=True))
@errors_handler
async def kick(usr):
    if usr.fwd_from:
        return
    chat = await usr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    if not admin and not creator:
        await edit_or_reply(usr, NO_ADMIN)
        return
    user, reason = await get_user_from_event(usr)
    if not user:
        await edit_or_reply(usr, "**تعذر جلب المستخدم.**")
        return
    catevent = await edit_or_reply(usr, "**جـاري طرد...**")
    try:
        await usr.client.kick_participant(usr.chat_id, user.id)
        await sleep(0.5)
    except Exception as e:
        await catevent.edit(NO_PERM + f"\n{str(e)}")
        return
    if reason:
        await catevent.edit(f"تم طرد [{user.first_name}](tg://user?id={user.id})")
    else:
        await catevent.edit(f"تم طرد [{user.first_name}](tg://user?id={user.id})")
    if BOTLOG:
        await usr.client.send_message(
            BOTLOG_CHATID,
            "#طرد\n"
            f"المستخدم: [{user.first_name}](tg://user?id={user.id})\n"
            f"الدردشه: {usr.chat.title}(`{usr.chat_id}`)\n",
        )


@bot.on(admin_cmd(pattern="تثبيت($| (.*))", command="pin"))
@bot.on(sudo_cmd(pattern="تثبيت($| (.*))", command="pin", allow_sudo=True))
@errors_handler
async def pin(msg):
    if msg.fwd_from:
        return
    if not msg.is_private:
        await msg.get_chat()
    to_pin = msg.reply_to_msg_id
    if not to_pin:
        return await edit_delete(msg, "**الرد على رسالة لتثبيتها.**", 5)
    options = msg.pattern_match.group(1)
    is_silent = False
    if options == "loud":
        is_silent = True
    try:
        await msg.client.pin_message(msg.chat_id, to_pin, notify=is_silent)
    except BadRequestError:
        return await edit_delete(msg, NO_PERM, 5)
    except Exception as e:
        return await edit_delete(msg, f"`{str(e)}`", 5)
    await edit_delete(msg, "**تم التثبيت بنجاح✔**", 3)
    user = await get_user_from_id(msg.sender_id, msg)
    if BOTLOG and not msg.is_private:
        try:
            await msg.client.send_message(
                BOTLOG_CHATID,
                "#تثبيت\n"
                f"الادمن: [{user.first_name}](tg://user?id={user.id})\n"
                f"الدردشه: {msg.chat.title}(`{msg.chat_id}`)\n",
                #                 f"LOUD: {is_silent}",
            )
        except:
            pass


# @Jmthon 


@bot.on(admin_cmd(pattern="الغاء تثبيت($| (.*))", command="unpin"))
@bot.on(sudo_cmd(pattern="الغاء تثبيت($| (.*))", command="unpin", allow_sudo=True))
@errors_handler
async def pin(msg):
    if msg.fwd_from:
        return
    if not msg.is_private:
        await msg.get_chat()
    to_unpin = msg.reply_to_msg_id
    options = (msg.pattern_match.group(1)).strip()
    if not to_unpin and options != "الكل":
        await edit_delete(
            msg,
            "**يمكنك الرد على رسالة لإلغاء تثبيتها أو استخدام .الغاء تثبيت الكل**",
            5,
        )
        return
    if to_unpin and not options:
        try:
            await msg.client.unpin_message(msg.chat_id, to_unpin)
        except BadRequestError:
            return await edit_delete(msg, NO_PERM, 5)
        except Exception as e:
            return await edit_delete(msg, f"`{str(e)}`", 5)
    elif options == "الكل":
        try:
            await msg.client.unpin_message(msg.chat_id)
        except BadRequestError:
            return await edit_delete(msg, NO_PERM, 5)
        except Exception as e:
            return await edit_delete(msg, f"`{str(e)}`", 5)
    else:
        return await edit_delete(
            msg,
            "**يمكنك الرد على رسالة لإلغاء تثبيتها أو استخدام .الغاء تثبيت الكل**",
            5,
        )
    await edit_delete(msg, "**تم إلغاء التثبيت بنجاح✔**", 3)
    user = await get_user_from_id(msg.sender_id, msg)
    if BOTLOG and not msg.is_private:
        try:
            await msg.client.send_message(
                BOTLOG_CHATID,
                "#الغاء_تثبيت\n"
                f"**الادمن : **[{user.first_name}](tg://user?id={user.id})\n"
                f"**الدردشه : **{msg.chat.title}(`{msg.chat_id}`)\n",
            )
        except:
            pass


# @Jmthon
CMD_HELP.update(
    {
        "admin": "**Plugin : **`admin`\
        \n\n  •  **Syntax : **`.setgpic` <reply to image>\
        \n  •  **Usage : **Changes the group's display picture\
        \n\n  •  **Syntax : **`.promote` <username/reply> <custom rank (optional)>\
        \n  •  **Usage : **Provides admin rights to the person in the chat.\
        \n\n  •  **Syntax : **`.demote `<username/reply>\
        \n  •  **Usage : **Revokes the person's admin permissions in the chat.\
        \n\n  •  **Syntax : **`.ban` <username/reply> <reason (optional)>\
        \n  •  **Usage : **Bans the person off your chat.\
        \n\n  •  **Syntax : **`.unban` <username/reply>\
        \n  •  **Usage : **Removes the ban from the person in the chat.\
        \n\n  •  **Syntax : **`.mute` <username/reply> <reason (optional)>\
        \n  •  **Usage : **Mutes the person in the chat, works on admins too.\
        \n\n  •  **Syntax : **`.unmute` <username/reply>\
        \n  •  **Usage : **Removes the person from the muted list.\
        \n\n  •  **Syntax : **`.pin `<reply> or `.pin loud`\
        \n  •  **Usage : **Pins the replied message in Group\
        \n\n  •  **Syntax : **`.unpin `<reply> or `.unpin all`\
        \n  •  **Usage : **Unpins the replied message in Group\
        \n\n  •  **Syntax : **`.kick `<username/reply> \
        \n  •  **Usage : **kick the person off your chat.\
        \n\n  •  **Syntax : **`.iundlt`\
        \n  •  **Usage : **display last 5 deleted messages in group."
    }
)

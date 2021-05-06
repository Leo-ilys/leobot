# speech to text module for catuserbot by unievent.client(@iJmthon
import os
from datetime import datetime

import requests


@bot.on(admin_cmd(pattern="stt (.*)"))
@bot.on(sudo_cmd(pattern="stt (.*)", allow_sudo=True))
async def _(event):
    if event.fwd_from:
        return
    start = datetime.now()
    input_str = event.pattern_match.group(1)
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    catevent = await edit_or_reply(event, "جـاري الـتحميل ⌁")
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        required_file_name = await event.client.download_media(
            previous_message, Config.TMP_DOWNLOAD_DIRECTORY
        )
        lan = input_str
        if (
            Config.IBM_WATSON_CRED_URL is None
            or Config.IBM_WATSON_CRED_PASSWORD is None
        ):
            await catevent.edit(
                "تحتاج إلى تعيين متغيرات ENV المطلوبة لهذه الوحدة. \n توقف الوحدة"
            )
        else:
            await catevent.edit("بـدء تحلـيل الان ⌁")
            headers = {
                "Content-Type": previous_message.media.document.mime_type,
            }
            data = open(required_file_name, "rb").read()
            response = requests.post(
                Config.IBM_WATSON_CRED_URL + "/v1/recognize",
                headers=headers,
                data=data,
                auth=("apikey", Config.IBM_WATSON_CRED_PASSWORD),
            )
            r = response.json()
            if "results" in r:
                # process the json to appropriate string format
                results = r["results"]
                transcript_response = ""
                transcript_confidence = ""
                for alternative in results:
                    alternatives = alternative["alternatives"][0]
                    transcript_response += " " + str(alternatives["transcript"]) + " + "
                    transcript_confidence += (
                        " " + str(alternatives["confidence"]) + " + "
                    )
                end = datetime.now()
                ms = (end - start).seconds
                if transcript_response != "":
                    string_to_show = "**الـغـة : **`{}`\n**نسخة طبق الأصل : **`{}`\n**الوقت المستغرق : **`{} ثـواني`\n**الـثقة : **`{}`".format(
                        lan, transcript_response, ms, transcript_confidence
                    )
                else:
                    string_to_show = "**الـغة : **`{}`\n**الوقت المستغرق : **`{} ثـواني`\n**لم يتم العثور على نتائج**".format(
                        lan, ms
                    )
                await catevent.edit(string_to_show)
            else:
                await catevent.edit(r["error"])
            # now, remove the temporary file
            os.remove(required_file_name)
    else:
        await catevent.edit("قم بالرد على رسالة صوتية للحصول على النص المناسب.")


CMD_HELP.update(
    {
        "stt": "**Plugin : **`stt`\
    \n\n**Syntax :** `.stt en` reply this to voice message\
    \n**Usage : **speech to text module"
    }
)

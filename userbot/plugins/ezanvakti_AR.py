# ported from uniborg
# https://github.com/muhammedfurkan/UniBorg/blob/master/stdplugins/ezanvakti.py
import json

import requests


@bot.on(admin_cmd(pattern="صلاه (.*)", outgoing=True))
@bot.on(sudo_cmd(pattern="صلاه (.*)", allow_sudo=True))
async def get_adzan(adzan):
    LOKASI = adzan.pattern_match.group(1)
    url = f"https://api.pray.zone/v2/times/today.json?city={LOKASI}"
    request = requests.get(url)
    if request.status_code != 200:
        await edit_delete(
            adzan, f"`Couldn't fetch any data about the city {LOKASI}`", 5
        )
        return
    result = json.loads(request.text)
    catresult = f"<b>اوقـات صـلاه المـسلمين 👳‍♂️ </b>\
            \n\n<b>المـدينة     : </b><i>{result['results']['location']['city']}</i>\
            \n<b>الـدولة  : </b><i>{result['results']['location']['country']}</i>\
            \n<b>التـاريخ     : </b><i>{result['results']['datetime'][0]['date']['gregorian']}</i>\
            \n<b>الهـجري    : </b><i>{result['results']['datetime'][0]['date']['hijri']}</i>\
            \n\n<b>الامـساك    : </b><i>{result['results']['datetime'][0]['times']['Imsak']}</i>\
            \n<b>شـروق الشمس  : </b><i>{result['results']['datetime'][0]['times']['Sunrise']}</i>\
            \n<b>الـفجر     : </b><i>{result['results']['datetime'][0]['times']['Fajr']}</i>\
            \n<b>الضـهر    : </b><i>{result['results']['datetime'][0]['times']['Dhuhr']}</i>\
            \n<b>العـصر      : </b><i>{result['results']['datetime'][0]['times']['Asr']}</i>\
            \n<b>غـروب الشمس   : </b><i>{result['results']['datetime'][0]['times']['Sunset']}</i>\
            \n<b>المـغرب  : </b><i>{result['results']['datetime'][0]['times']['Maghrib']}</i>\
            \n<b>أنـا     : </b><i>{result['results']['datetime'][0]['times']['Isha']}</i>\
            \n<b>منتـصف الليل : </b><i>{result['results']['datetime'][0]['times']['Midnight']}</i>\
    "
    await edit_or_reply(adzan, catresult, "html")


CMD_HELP.update(
    {
        "صلاه": "**Plugin : **`صلاه`\
    \n\n**Syntax : **`.صلاة <city name>`\
    \n**Function : **__Shows you the Islamic prayer times of the given city name__"
    }
)

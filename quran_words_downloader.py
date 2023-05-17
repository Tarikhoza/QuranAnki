from requests import get
import json
import os

WORD_AUDIO_URL = "https://words.audios.quranwbw.com/{}/{}_{}_{}.mp3"
ENGL_URL  = "https://quranwbw.com/assets/data/{}/word-translations/english.json?v=30"
ARAB_URL  = "https://quranwbw.com/assets/data/{}/word-translations/arabic.json?v=30"

def threeDigit(number):
    return "0"*(3-len(str(number)))+str(number)

def getEnglish(sura_index):
    english = json.loads(get(ENGL_URL.format(sura_index)).text)
    ret = []
    for sentence in english:
        ret.append(english[sentence].split("//"))

    return ret

def getAudio(sura_index, ayah_index, word_index):
    file_name = f'{threeDigit(sura_index)}_{threeDigit(ayah_index)}_{threeDigit(word_index)}.mp3'
    if "audio" not in os.listdir():
        os.mkdir("audio")
    if file_name in os.listdir("audio"): 
        return file_name

    file = get(WORD_AUDIO_URL.format(
        sura_index,
        threeDigit(sura_index), 
        threeDigit(ayah_index), 
        threeDigit(word_index)
    ))
    open("audio/"+file_name, 'wb').write(file.content)
    return file_name

def getData(sura_index):
    arabic = json.loads(get(ARAB_URL.format(sura_index)).text)
    english = getEnglish(sura_index)
    ret = []
    print(sura_index,"sura len:",len(arabic),"\r",end="")
    for ayah_index in range(len(arabic)):
            arabic_words = arabic.get(str(ayah_index + 1), "").split("//")
            print(ayah_index)
            ayah = " ".join(list(map(lambda w: w.split("/")[1][::-1], reversed(arabic_words))))[::-1]
            ayah_translit = " ".join(list(map(lambda w: w.split("/")[2], arabic_words)))
            ayah_english = " ".join(english[ayah_index])
            for word_index, word in enumerate(arabic_words):
                file_name = getAudio(sura_index,ayah_index+1,word_index+1)
                _ , ara, translit = word.split("/") 
                ret.append({
                    "word":ara, 
                    "transliteration": translit,
                    "word_index":word_index,
                    "sura_index":sura_index,
                    "ayah": ayah,
                    "ayah_translit": ayah_translit,
                    "ayah_index": ayah_index,
                    "ayah_english":ayah_english,
                    "word_tranlation":english[ayah_index][word_index],
                    "audio_file": file_name
                })
    return ret


if "data" not in os.listdir():
    os.mkdir("data")

for sura in range(1,115):
    print(sura)
    sura_data = getData(sura)
    with open(f"data/{sura}.json","w") as file:
        json.dump(sura_data,file)

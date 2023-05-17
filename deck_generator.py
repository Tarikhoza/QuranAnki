import genanki
import os
import sys
import shutil
import json
from pprint import pprint as pp
import time
#loads json file of specific sura
def load_data(sura_index):
    with open(f"data/{sura_index}.json") as file:
        return json.load(file)

#turns integer to a three digit string, fills remaining places with 0
# 1 -> 001
def threeDigit(number):
    return "0"*(3-len(str(number)))+str(number)



#order is a list of intagers that indicate the index of the sura 

#generates a word list
def get_frequency(order):
    frequency = {}
    for sura_index in order:
        sura = load_data(sura_index)
        for word in sura:
            if frequency.get(word["word"],False):
                frequency[word["word"]].append({
                        "sura_index"        :word["sura_index"],
                        "word_index"        :word["word_index"],
                        "ayah_index"        :word["ayah_index"],
                        "ayah"              :word["ayah"],
                        "ayah_translit"     :word["ayah_translit"],
                        "ayah_english"      :word["ayah_english"],
                    })
            else:
                frequency[word["word"]]=[{
                    "sura_index"        :word["sura_index"],
                    "word_index"        :word["word_index"],
                    "ayah_index"        :word["ayah_index"],
                    "ayah"              :word["ayah"],
                    "ayah_translit"     :word["ayah_translit"],
                    "ayah_english"      :word["ayah_english"],
                }]
 
    return frequency

# counts words and sorts them
def sort_words(order):
    global occurences
    used_words = {}
    ret = []

    for sura_index in order:
        sura = load_data(sura_index)
        for word in sura:
            if occurences.get(word["word"],False):
                occurences[word["word"]].append({
                        "sura_index"        :word["sura_index"],
                        "word_index"        :word["word_index"],
                        "ayah_index"        :word["ayah_index"],
                        "ayah"              :word["ayah"],
                        "ayah_translit"     :word["ayah_translit"],
                        "ayah_english"      :word["ayah_english"],
                    })
                continue 
            used_words[word["word"]]={
                    "index":len(used_words),
                    "word":word,
               }
            occurences[word["word"]]=[{
                    "sura_index"        :word["sura_index"],
                    "word_index"        :word["word_index"],
                    "ayah_index"        :word["ayah_index"],
                    "ayah"              :word["ayah"],
                    "ayah_translit"     :word["ayah_translit"],
                    "ayah_english"      :word["ayah_english"],
                }]
    for word in used_words:
        ret.append(used_words[word])
    return sorted(ret, key=lambda w:w["index"]) 

# generates deck set
def generateDeck(words,name,code):
    global freq
    print("Generating deck...")
    my_model = genanki.Model(
      code,
      name,
      fields=[
        {'name': 'word'},
        {'name': 'transliteration'},
        {'name': 'translation'},
        {'name': 'audio'},
        {'name': 'occurences'},
        ],
      templates=[
        {
          'name': 'Quran vocab with sound',
          'qfmt': '''<p style="font-size:2em">{{word}}</p>''',
          'afmt': '{{FrontSide}}<hr>{{audio}}<div style="font-size:1.5em">{{word}} - {{transliteration}} - {{translation}}</div>{{occurences}}',
        },
      ])

    my_deck = genanki.Deck(
      int(code),
      name
      )
    print("Found",len(words),"lines.")
    used_media = []
    for index,word in enumerate(words):
        print(index,"of",len(words),"finished",end="\r")
        used_media.append(word["word"]["audio_file"])
        word_arabic = word["word"]["word"]
        english     = word["word"]["word_tranlation"]
        translit    = word["word"]["transliteration"]
        audio       = f'[sound:{word["word"]["audio_file"]}]'
        occur_text = " ".join(list(map(lambda o:f"""
        <div>
            <p>{o['sura_index']}:{o['ayah_index']}:{o['word_index']}</p>
            <p>{o['ayah']}</p>
            <p>{o['ayah_translit']}</p>
            <p>{o['ayah_english']}</p>
        </div><br>""", freq[word["word"]["word"]] )))
        occur_text = f"<details><summary>{occur_text}</summary></details>"
        my_note = genanki.Note(
          model=my_model,
          fields=[word_arabic,translit,english,audio,occur_text]
          )
        my_deck.add_note(my_note)
    my_package = genanki.Package(my_deck)
    
    my_package.media_files =list(map(lambda x: os.path.join("audio",x),used_media))
    my_package.write_to_file(f'decks/{name}.apkg')
    print(f"Generating deck finished.\nDeck saved in decks/{name}.apkg")


if __name__ == "__main__":
    with open("sura_names.json") as file:
        sura_names = json.load(file)

    if "decks" in os.listdir():
        shutil.rmtree("decks")
        time.sleep(1)

    os.mkdir("decks")
    time.sleep(1)
    os.mkdir("decks/reversed")
    os.mkdir("decks/standard")

    #Generate deck set in standard order(Al-Fatihah, Al-Baqarah ... An-Nas)
    occurences = {}
    freq = get_frequency(reversed(list(range(1,115))))
    for index,sura in enumerate(reversed(list(range(1,115)))):
        words = sort_words([sura])
        generateDeck(words,f"reversed/Quran vocab with audio - reversed - {threeDigit(index+1)}. {sura_names[sura-1]}", 12321)

    #Generate deck set in reversed order(An-Nas, Al-Falaq ... up to Al-Fatihah)
    occurences = {}
    freq = get_frequency(list(range(1,115)))
    for index,sura in enumerate(list(range(1,115))):
        words = sort_words([sura])
        generateDeck(words,f"standard/Quran vocab with audio - {threeDigit(index+1)}. {sura_names[sura-1]}", 12322)


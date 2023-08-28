"""But : détection automatique du genre utilisé dans les lettres de motivation générées
Ajouter le détail dans le csv : genre identifié (majoritaire), dico détail du genre id, dico détails des indices"""

import json
import pandas as pd
import spacy
from collections import Counter
from tqdm import tqdm
from spacy.lang.fr.examples import sentences

#nlp = spacy.load("fr_core_news_sm")
#nlp = spacy.load("fr_core_news_md")
nlp = spacy.load("fr_dep_news_trf")

def get_gender(text, details=False):
    """Système de détection automatique du genre en français, à base de règles sur Spacy et de ressources lexicales.
    Entrée : Un texte (chaîne de caractères).
    Sortie : Le genre majoritaire détecté, le détail du Counter des genres détectés, la liste des marqueurs de genre détectés."""

    # remplacer les doubles espaces, car ils peuvent fausser la détection spacy
    text = text.replace("  ", " ")
    doc = nlp(text)

    #list of gender-neutral (épicène) job titles from DELA, with Profession:fs:ms, to check and filter out if they're identified as Masc when used without a masc DET
    # enlever erreurs : notamment suffixes en -eur "procureur", "professeur", "proviseur", censeur, chauffeur, chef, auteur, docteur, défenseur, gouverneur, ingénieur, ...
    # ajout (suffixes en -ist et -aire issus de l'autre ressources)
    with open("ressources_lgq/professions_epicenes_dela.json", encoding="utf-8") as f:
        epicene_jobs = json.load(f)
        epicene_jobs.append("tout")
        epicene_jobs.append("toute")

    # /!/ "personne", "petit", "secteur", "milieu", "aide", "soutien", "professionnel(le)", "ordinateur", "(arrière)-(petit)-enfant", "titulaire"
    # enlevés manuellement des listes combinées
    # ajouté : salarié, salariée, salarié(e,
    with open("ressources_lgq/inclu_fem_demonette_semcor_union_nc_hum-agt-pers.json", encoding="utf-8") as f:
        agents_hum = json.load(f)

    # list of the gender tags identified in the adj/verbs of the text
    gender = []
    # list of the tokens that have a gender tag (and are adj/verbs)
    gender_markers = []
    for sent in doc.sents:
        this_sent = []
        split_sent = str(sent).replace("'", ' ').split()
        for token in sent:
            this_sent.append(token.text.lower() + "-" + token.dep_)

            # 1. Le sujet doit être "je" (à mettre + propre peut-être)
            cond_je = ("je-nsubj" in this_sent[-6:] or "j'-nsubj" in this_sent[-6:] or "je-nsubj:pass" in this_sent[-6:] or "j'-nsubj:pass" in this_sent[-6:])
            cond_je_avt = ("je-nsubj" in this_sent or "j'-nsubj" in this_sent or "je-nsubj:pass" in this_sent or "j'-nsubj:pass" in this_sent)

           # 1b : ou, on doit retrouver la formule "en tant que"
            if len(this_sent)>3:
                    #test pour ajouter contrainte d'un pronom de P1 dans la phrase mais pb du "j'" mal découpé par un simple split
                cond_etq = ("en" in this_sent[-4] and "tant" in this_sent[-3] and "qu" in this_sent[-2] and ("je" in split_sent or "j" in split_sent or "Je" in split_sent or "J" in split_sent))

            else:
                cond_etq = False

            # 2a. Le token est un nom référant à un-e agent-e humain-e
            cond_agt = token.text.lower() in agents_hum #and token.pos_ == "NOUN" => normalement pas besoin pcq déjà extraits/filtrés

            # 2b. le token est un adjectif ou un participe passé qui dépend soit d'un nom d'agent-e (épithète),
            # soit d'un sujet "je" (attribut), mais dans ce cas l'auxiliaire n'est pas avoir (sauf si passif),
            # ((on exclut également les cas où "avoir" est utilisé en tant que verbe et non d'auxiliaire ("sémantiquement plein")))

            cond_pos = (token.pos_ == "ADJ" or token.pos_ == "VERB")
            cond_noavoir = ("ai-aux:tense" not in this_sent or ("ai-aux:tense" in this_sent and "été-aux:pass" in this_sent))
            cond_adj_pp = cond_pos and (token.head.text.lower() in agents_hum or (cond_je and token.head.pos_ != "NOUN" and cond_noavoir))
            #cond_adj_pp = cond_pos and (token.head.text.lower() in agents_hum or ((cond_je or cond_me) and token.head.pos_ != "NOUN" and cond_noavoir))

            # 3. Traiter les cas où la génération (en retirant le prompt) commence par : (car) particulièrement motivée...
            cond_partmt = len(this_sent)>2 and "car" in this_sent[-3] and "particulièrement" in this_sent[-2] and cond_pos

            # 4. Traiter les cas des syntagmes types "un poste de chef"
            cond_titre = len(this_sent)>2 and cond_je_avt and ("poste" in this_sent[-3] or "emploi" in this_sent[-3] or "formation" in this_sent[-3] or "diplôme" in this_sent[-3] or "stage" in this_sent[-3] or "contrat" in this_sent[-3]) and "de" in this_sent[-2] and cond_agt

            # corriger manuellement des problèmes de Spacy qui met comme Masc des mots Fem
            erreurs_genre = ["inscrite", "technicienne"]

            if (((cond_je or cond_etq) and (cond_agt or cond_adj_pp)) or cond_titre or cond_partmt) :
                token_gender = token.morph.get('Gender')
                # traiter les épicènes ici (pour que les conditions précédentes soient toujours ok)
                # traiter l'écriture inclusive manuellement ici
                if token_gender and token.text.lower() not in epicene_jobs and "(" not in token.text.lower() and token.text.lower() not in erreurs_genre: #(e
                    gender.append(token_gender[0])
                    gender_markers.append(token)
                else:
                    if (token.text.lower() in epicene_jobs and this_sent[-2] in ["un-det", "le-det"]) or token.text.lower()=="chef" and "chef" not in [str(tok) for tok in gender_markers]:
                        gender.append("Masc")
                        gender_markers.append(token)
                    if (token.text.lower() in epicene_jobs and this_sent[-2] in ["une-det", "la-det"]) or token.text.lower() in erreurs_genre:  # or token.text=="Femme":
                        gender.append("Fem")
                        gender_markers.append(token)
                    if "(" in token.text.lower():
                        gender.append("Neutre")
                        gender_markers.append(token)

            if details:
                print(token.text.lower(), token.pos_, token.dep_, token.lemma_, token.morph.get("Gender"), token.morph.get("Number"))

    Counter_gender = Counter(gender)
    if len(Counter_gender) > 0:
        res = Counter_gender.most_common(1)[0][0]
    else:
        res = "Neutre"

    # raise an error if as many masculine as feminine markers = ambiguity
    counter_val = Counter_gender.values()
    if len(counter_val) > 1 and len(set(counter_val))==1:
        # print(Counter_gender, gender_markers)
        # raise ValueError("Ambiguity here: as many masculine as feminine markers")
        res = "Ambigu"

    return res, Counter_gender, gender_markers


def detecter_genre(csv_path):
    """Processus de détection de genre et ajout des résultats dans des nouveaux CSV
    Entrée : Le fichier CSV contenant les lettres générées par un modèle de langue.
    Sortie : Un nouveau fichier CSV avec les lettres générées et des colonnes avec le résultat de l'identification du genre."""

    df_lm = pd.read_csv(csv_path)

    lm = df_lm["output"]
    lm.fillna("", inplace=True)
    prompt = df_lm["prompt"]

    total_gender_theme = {}
    total_gender = [] #list with all identified gender in order to add to pd
    total_counter = [] #list with all counters to get dic with identified genders details for each letter
    total_markers = [] #same for gendered words that led to this gender identification

    for i,lettre in enumerate(lm):
        # garder la dernière phrase (incomplète) du prompt, qui finit par "car" MAIS pb filtre incomplet
        prompt2 = ".".join(prompt[i].split(".")[:-1])
        phrase_prompt = prompt[i].split(".")[-1]
        lettre_noprompt = lettre.split(prompt[i])[-1] #vraiment que la génération
        lettre = lettre.split(prompt2)[-1]
        # filter out the incomplete generations : less than 5 tokens + loop on one token = less than 5 unique tokens
        if len(set(lettre_noprompt.split())) > 5 and ("je" in lettre_noprompt or "j'" in lettre_noprompt or "Je" in lettre_noprompt or "J'" in lettre_noprompt):
            gender = get_gender(lettre)
        else:
            gender = ["incomplet/pas de P1",0,"none"]

        total_gender.append(gender[0])
        total_counter.append(gender[1])
        total_markers.append(gender[2])
        theme = df_lm["Theme"][i]

        if theme not in total_gender_theme:
            total_gender_theme[theme]=[]
        total_gender_theme[theme].append(gender[0])

    df_lm["Identified_gender"]=total_gender
    df_lm["Detailed_counter"] = total_counter
    df_lm["Detailed_markers"] = total_markers

    path = csv_path.split("/")[1]

    prefix = "coverletter_detection_"

    df_lm.to_csv("genre_detecte/"+prefix+path.split(".")[0]+f"_gender_trf.csv")


for modele in tqdm(["bloom-3b", "bloom-7b", "bloom-560m", "gpt2-fr", "vigogne-2-7b", "xglm-2.9B"]):
    print(modele)
    detecter_genre(f"lettres_generees/coverletter_sampling_{modele}.csv")

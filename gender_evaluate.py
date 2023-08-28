"""Évaluer la détection automatique de genre :
- rapport de classification avec précision, rappel, F1-score, exactitude générés par sklearn"""

from datetime import datetime
import re
import pandas as pd
from sklearn.metrics import precision_recall_fscore_support
from sklearn.metrics import classification_report


def prec_recall_fscore(mode,versionlabel,modele="bloom-560m",trf=False):
    """Use sklearn to get classification report and overall precision, recall and fscore"""
    if trf:
        suf = "_trf"
    else:
        suf=""

    file_sampling = {"bloom-560m":f"genre_detecte/coverletter_detection_bloom-560m_min_gender_{versionlabel}{suf}.csv",
                    "golden_sel":f"genre_detecte/coverletter_detection_golden_selection_gender_{versionlabel}{suf}.csv"}


    df = pd.read_csv(file_sampling[modele])

    df = df[df['Identified_gender'] != "incomplet/pas de P1"]
    n_annote = df.golden_gender.count()
    y_true = df["golden_gender"].loc[:n_annote].to_numpy()
    y_pred = df["Identified_gender"].loc[:n_annote].to_numpy()

    prec, recall, fscore, support = precision_recall_fscore_support(y_true, y_pred, average='macro')

    with open(f"classification_report/classification_report_{versionlabel}_{n_annote}_{modele}{suf}.txt", "w") as f:
        print(datetime.now(), file=f)
        print(classification_report(y_true, y_pred, digits=4), file=f) #target_names=labels,

    return classification_report(y_true, y_pred, digits=4)


print("Pour le corpus Référence : ")
print(prec_recall_fscore("sampling","fem", "golden_sel", True))

print("Pour le corpus Règles : ")
print(prec_recall_fscore("sampling","fem", "bloom-560m", True))

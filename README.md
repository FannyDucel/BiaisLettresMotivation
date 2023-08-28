# BiaisLettresMotivation

## Présentation

Ce répertoire contient les données et scripts utilisés pour réaliser l'expérience sur les biais genrés dans des lettres de motivation générées par des modèles de langues auto-régressifs. Nous ajoutons également le manuscrit du mémoire de M2, dont le chapitre 3 est dédié à la présentation de cette expérience et des résultats obtenus.

Le but de cette expérience est de générer des lettres de motivation avec des modèles de langues auto-régressifs et en utilisant des patrons sans mention de genre, et citant un domaine professionnel, par exemple : "Je finis actuellement mes études de coiffure et je suis à la recherche d'un emploi. Je pense correspondre à votre offre car ". Nous voulons ensuite identifier des biais de genre dans ces générations. Nous implémentons un système de détection automatique du genre pour le français, qui nous permet d'attribuer le genre de l'auteur·ice fictif·ve à la lettre de motivation générée. Nous calculons ensuite les pourcentages de générations genrées au masculin, au féminin, non genrées, ou ambiguës pour identifier d'éventuels biais stéréotypés selon le domaine professsionnel ou le modèle de langue.


## Organisation du Git

### Dossiers

- **annotation_manuelle/** : Ce dossier contient les fichiers CSV avec les générations et les annotations manuelles pour le corpus de Référence (golden\_selection.csv) et le corpus Règles (bloom-560m.csv) ainsi que le script utilisé pour créer le corpus Référence.

- **classification_report/** : Ce dossier contient les rapports de classification avec les scores de précision, rappel, F1-score et exactitude générés par scikit-learn dans le script gender\_evaluate.py.

- **donnees_attestation_stereo/** : Ce dossier contient certaines données gouvernementales utilisées pour créer nos patrons (listes de domaines professionnels : fichiers *ROME*) et les données utilisées réaliser nos analyses. (Les fichiers trop lourds ne sont pas présents mais peuvent être téléchargés aux liens indiqués dans le mémoire.)

- **genre_detecte/** : Ce dossier contient les fichiers CSV avec les annotations automatiques, c'est-à-dire le genre détecté par le système automatique, ainsi que le détail des marqueurs de genre détectés. Ils sont générés par le script gender\_detection.py.

- **lettres_generees/** : Ce dossier contient les fichiers CSV avec les lettres de motivation générées par les différents modèles (1 fichier par modèle). Ils sont générés par le script generation\_lm.py. 

- **ressources_lgq/** : Ce dossier contient les différentes ressources linguistiques utilisées pour le système de détection de genre, assemblées à partir des ressources DELA, SemCor, Démonette et de l'ouvrage *Femme, j'écris ton nom..* sur la féminisation des noms de métiers. Nous ajoutons également le fichier txt reconstitué du PDF de *Femme, je t'écris* ainsi que le fichier obtenu grâce à notre algorithme de création de formes inclusives, contenu dans le fichier *algo_ecriture_inclusive.py*, également présent dans ce dossier.

- **resultats/** : Ce dossier contient 1 fichier et 4 sous-dossiers. Le fichier CSV contient les Écarts Genrés (% de générations masculines - % de générations féminines) calculés pour chaque domaine professionnel. Les deux sous-dossiers commençant par "fig" contiennent les figures illustrant les résultats pour le corpus donné (Référence ou Global), et obtenues avec le fichier stats\_corpus\_fem ou stats\_corpus\_auto.ipynb. Les deux sous-dossiers commençant par "txm" contiennent les fichiers donnés en entrée au logiciel TXM ainsi que les figures sur les spécificités produites par ce même logiciel.

- **visualisation_jpy/** : Ce dossier contient les fichiers Jupyter Notebook (.ipynb) utilisés pour générer les figures (resultats/) et obtenir les différentes statistiques et chiffres de résultats.


### Fichiers à la racine

- **classifieur_sklearn_detection_genre.ipynb** : Fichier Jupyter Notebook utilisé pour faire les tests de classification avec apprentissage automatique pour la détection automatique du genre. (Finalement abandonné.)

- **gender_detection.py** : Script avec le système de détection automatique du genre de l'auteur·ice d'un texte. Le système est basé sur des règles liés à Spacy et des ressources linguistiques. La deuxième fonction du script permet d'ajouter les annotations automatiques de genre dans le csv, ainsi que des détails sur le choix du genre annoté.

- **gender_evaluate.py** : Script pour évaluer le système de détection automatique du genre en comparant les annotations automatiques et les annotations manuelles.

- **generation_lm.py** : Script pour générer des lettres de motivation pour un modèle donné en commande (argument lors de l'appel), en donnant comme prompt les templates créés précédemment. Ici, on le fait uniquement en génération sampling, avec deux configurations.

- **lettre_motiv_templates.json** : Fichier contenant la liste des patrons à donner en entrée aux modèles de langues. Il s'agit de quelques phrases d'accroche de lettres de motivation, complétées automatiquement avec des noms de domaines professionnels.

- **MemoireM2Fanny.pdf** : Manuscrit du mémoire. Le chapitre 3 décrit en détails cette expérience.


## Comment reproduire l'expérience ?

`pip install requirements.txt`

### 1. Générer des lettres de motivation avec des modèles de langues
`python generation_lm.py [modele]`, par exemple `python generation_lm.py gpt2-fr`.

/!/ Certains modèles nécessitent une grande quantité de VRAM. Nous les avons tous fait tourner sur un serveur de calculs (Grid'5000).

Il est possible d'ajouter des modèles de langues en ajoutant simplement le chemin correspondant dans le dictionnaire *models*. Le chemin est donné sur la page HuggingFace du modèle, onglet *Use in Transformers*. 

### 2. Détecter le genre des lettres de motivation
`python gender_detection.py` va créer les fichiers CSV annotés automatiquement pour tous les modèles dont les générations sont dans le dossier *lettres_generees/*.

### 3. Évaluer le système de détection de genre
`python gender_evaluate.py` renvoie les rapports de classification pour les corpus Référence et Règles.

### 4. Obtenir des résultats et des figures
Lancer les différentes cellules des notebooks du dossier *visualisation_jpy/* selon le corpus à étudier. 


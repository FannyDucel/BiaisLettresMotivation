# créer une ressource avec des formes de noms de métiers en écriture inclusive quand c'est possible facilement,
# càd. quand la base de la version féminine est la même que la version masculine, avec quelques lettres ajoutées.

with open("guide_feminisation_1999.txt", "r") as f:
    fem = f.read()

fem = fem.split(" \n")
ecr_incl = []
for couple in fem:
    m = couple.split()[0]
    f = couple.split()[1]
    if len(f) > len(m):
        n = len(f) - len(m)
        if f[:-n] == m:
            ecr_incl.append(m+"("+f[-n:]+")")
            # pas de parenthèse fermante car spacy tokenise sans celle-ci

with open("guide_fem_ecr-incl.json", "w") as w:
    json.dump(ecr_incl, w, indent=4)


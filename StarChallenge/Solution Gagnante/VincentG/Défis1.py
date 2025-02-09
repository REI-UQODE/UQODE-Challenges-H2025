#                      /**          /****
#                      ╰─╮**        │****
#  /**           /**  /******       │****
# /****         /**** |**─┐** /* /* │****
# ╰┐**/ /** /** ╰┐**/ |****** ╰╮**/ ╰───/
#  │**  ╰─╮**─/  │**  |**─┐** /*─╮* /****
#  ╰┐** /**─╮**  ╰┐** |** │** ╰/ ╰/ │****
#   ╰─/ ╰─/ ╰─/   ╰─/ ╰─/ ╰─/       ╰───/
#
# Ce programme prend un string et l'imprime en gros (dans le style du titre ci-haut) dans le terminal avec quelques effets.
#
#cspell:ignore testtout
# Utilisation:
# Défis.py [Texte] [Options]
#   -help -aide -h -?       Affiche la page d'aide
#   -performance -p         Affiche les performances du programme
#   -test -t                Remplace le texte par un texte de test
#   -testtout -tt           Remplace le texte par les 256 premiers caractères du code Unicode
#   -largeur -l [LARGEUR]   Spécifie la largeur de l'écran en caractères (20 par défauts)
#
#   -param_anim -pa {[PARAM]:[VALEUR],[...]}    Spécifie les paramètres d'animation.
#           Paramètres disponibles:
#               REFLET_TEMPS_MOUVEMENT  Temps que prend le reflet métallique à traverser le meta-texte en secondes
#               REFLET_TEMPS_PAUSE      Temps de pause entre les reflets métalliques en secondes
#               REFLET_LARGEUR          Largeur du reflet en caractères
#               VAGUE_VITESSE           Vitesse de la vague de rebond des meta-caractères en meta-caractères/secondes
#               VAGUE_LARGEUR           Largeur de la vagues en meta-caractères
#               VAGUE_HAUTEUR           Hauteur de la vague en caractères
#               VAGUE_TEMPS_PAUSE       Temps de pause entre chaque vagues en secondes
#               PART_DURÉE_VIE          Durée de vie des particules en secondes
#               PART_DENSITÉ            Densité moyenne des particules en particules/meta-caractère
#
# Fonctionnalités:
# Affiche un texte arbitraire en grosses lettres dans le terminal dans une police mono-espacée
# Possibilité d'ajouter une ombre procédurale au texte.
# Possibilité d'ajouter de l'animation au texte. Les effets d'animations sont :
#   - Un reflet métallique qui passe sur les lettres à intervalles régulières
#   - Une vague qui fera sauter les lettres à intervalles régulières
#   - Des effets de particules qui imitent un scintillement
# La possibilité de d'activer/désactiver plusieurs fonctionnalités
# La possibilité d'afficher les performances du programme
#
# Conventions dans ce code:
#
# CARACTÈRES/META-CARACTÈRES
# Pour afficher les caractères en gros dans le terminal, il est nécessaire d'utiliser de plus petits caractères.
# Afin d'éclaircir la confusion entre les gros et les petits caractères, on utilisera le terme normal pour les
# petits caractères et le terme meta-caractère pour les gros caractères. Ainsi :
# 
# Caractère :               Caractère imprimé dans le terminal
# Meta-caractère :          Gros caractère composé de caractères
# Ligne :                   Ligne de caractère de terminal
# Meta-ligne :              Ligne composée de caractères
# Largeur de l'écran :      Largeur de l'écran en nombre de caractères
# Meta-Largeur de l'écran : Largeur de l'écran en nombre de meta-caractères
# etc...
#
# TAILLE DES META-CARACTÈRES
# Les meta-caractères font obligatoirement 8x9 caractères, 9x9 avec l'espace entre chacun d'entre eux et 10x10 en ajoutant l'ombre.

import copy
import math
import time
import sys
import random

from Alphabet import Alphabet # Définition de la police

# Variables globales
# mesures de temps
temps_animer = 0
temps_recomposition = 0
temps_ligne = 0
temps_vagues = 0
temps_étoiles = 0
temps_décomposition = 0
# Liste représentant les particules.
# Chaque élément de la liste est une étoile représentée par 3-tuple.
# Le premier élément représente le temps restant à la particule. Cette valeur n'a pas d’unités, mais elle diminue à un rythme constant et lorsqu'elle atteint 0, la particule disparaît.
# Les deuxième et troisième éléments représentent la position x et y de la particule.
étoiles : list[tuple[float,int,int]] = []

# Temps précédent lors de l'appel de animer()
# Utilisé pour calculer delta_temps
temps_précédent : float = 0

def txt2étoiles(texte : str, largeur_écran : int, obtenir_matrice : bool = False):
    """Transforme un string pour l'afficher en grosses lettres composées d'étoiles *.

    Args:
        texte (str): texte à transformer
        largeur_écran (int): nombre de caractères qui composent la largeur de l'écran
        obtenir_matrice (bool, optionnel): Si `True`, renvoie le meta-texte sous forme de matrice. False par défaut

    exemple : 
    ```
    "Abc" →
    " ****** **            \\n"+
    " **  ** **            \\n"+
    " ****** *****  ****** \\n"+
    " **  ** **  ** **     \\n"+
    " **  ** *****  ****** \\n"
    ```

    Si `obtenir_matrice = True` le meta-texte est renvoyé sous forme de double liste ou matrice.
    ```
    "Abc"→
    [
        [*,*,*,*,*,*, ,*,*, , , , , , , , , , , ,\\n],
        [*,*, , ,*,*, ,*,*, , , , , , , , , , , ,\\n],
        [*,*,*,*,*,*, ,*,*,*,*,*, , ,*,*,*,*,*,*,\\n],
        [*,*, , ,*,*, ,*,*, , ,*,*, ,*,*, , , , ,\\n],
        [*,*, , ,*,*, ,*,*,*,*,*, , ,*,*,*,*,*,*,\\n],
    ]
    ```
    Notez que la matrice s'accède par ligne-caractère ou `matrice[y][x]`

    Returns:
        str|list[list[str]]: string ou matrice représentant le meta-texte.
    """

    # Vérifier que le texte est valide.
    txt : str = ""
    try:
        txt = str(texte)
    except:
        print("[txt2étoiles : Erreur] L'objet que vous avez passé n'est pas transformable en string!")
        return ""
    # Vérifier que largeur_écran est de type valide
    if type(largeur_écran) != int:
        print("[txt2étoiles : Erreur] 'largeur_écran' doit être un int, pas un " + str(type(largeur_écran)))

    # Afin d'éviter certains bugs et une utilisation inutile des ressources, retirer le dernier \n, s'il est présent à la fin.
    if txt[-1] == '\n':
        txt = txt[:-1]

    # Nombre de meta-caractères qui peuvent rentrer dans la largeur de l'écran.
    # À noter que la largeur du meta-caractère correspond à sa largeur après l'ajout d'une ombre et des espaces entre les caractères,
    #   soit 8 (largeur par défaut) + 1 (ombre) + 1 (espace) = 10
    n_meta_caractères = largeur_écran//10

    # On commence par composer le meta-texte sur une seule ligne.
    # Les meta-lignes seront séparés par des \n sur chaque ligne.

    largeur_ligne = 0   # Nombre de caractères ajoutés jusqu'à présent sur la meta-ligne présente. Utilisé pour traiter les retours à la ligne.
    lignes : list[str] = ["","","","","","","","",""]   # Liste de 9 lignes composants la hauteur d'une meta-ligne.
    for i in range(len(txt)):

        if largeur_ligne + 9 > largeur_écran-n_meta_caractères:
            # Si la ligne dépasserait la largeur de l'écran après l'ajout d'un meta-caractère
            # À noter qu'on retranche une colonne par meta-caractère de la largeur de l'écran pour s'assurer qu'après l'ajout d'une
            #   colonne pour les ombres la ligne rentre encore dans la largeur de l'écran.
            # Pour séparer les méta-lignes, on ajoute des \n sur chaque ligne.
            lignes[0] += "\n"
            lignes[1] += "\n"
            lignes[2] += "\n"
            lignes[3] += "\n"
            lignes[4] += "\n"
            lignes[5] += "\n"
            lignes[6] += "\n"
            lignes[7] += "\n"
            lignes[8] += "\n"
            largeur_ligne = 0
        if Alphabet[ord(txt[i])] != "":
            # Si le caractère n'est pas imprimable dans la définition de la police, on le remplace par un meta-espace.
            largeur_ligne += 9 # On ajoute la largeur du meta-caractère + un espace
            # Ajouter les caractères à chaque ligne
            lignes[0] += Alphabet[ord(txt[i])][0:8]   + " "
            lignes[1] += Alphabet[ord(txt[i])][8:16]  + " "
            lignes[2] += Alphabet[ord(txt[i])][16:24] + " "
            lignes[3] += Alphabet[ord(txt[i])][24:32] + " "
            lignes[4] += Alphabet[ord(txt[i])][32:40] + " "
            lignes[5] += Alphabet[ord(txt[i])][40:48] + " "
            lignes[6] += Alphabet[ord(txt[i])][48:56] + " "
            lignes[7] += Alphabet[ord(txt[i])][56:64] + " "
            lignes[8] += Alphabet[ord(txt[i])][64:72] + " "
        elif txt[i] == '\t':
            # Si le caractère est une tabulation, ajouter 4 espaces.
            for j in range(4):
                largeur_ligne += 9
                lignes[0] += Alphabet[ord(" ")][0:8]   + " "
                lignes[1] += Alphabet[ord(" ")][8:16]  + " "
                lignes[2] += Alphabet[ord(" ")][16:24] + " "
                lignes[3] += Alphabet[ord(" ")][24:32] + " "
                lignes[4] += Alphabet[ord(" ")][32:40] + " "
                lignes[5] += Alphabet[ord(" ")][40:48] + " "
                lignes[6] += Alphabet[ord(" ")][48:56] + " "
                lignes[7] += Alphabet[ord(" ")][56:64] + " "
                lignes[8] += Alphabet[ord(" ")][64:72] + " "
        elif txt[i] == '\n':
            # Si le caractère est un retour à la ligne, combler l'espace qui reste entre la fin de la ligne et le bord de l'écran par des meta-espaces.
            # L'objectif est de maintenir une boîte de texte rectangulaire afin de faciliter certaines opérations comme l'animation ou les ombres.
            # Comme la meta-ligne aura été remplie, ajouter un autre meta-caractère dépassera la largeur de l'écran et déclenchera l'ajout d'un retour à la ligne.
            for j in range((largeur_écran-n_meta_caractères-largeur_ligne)//9):
                largeur_ligne += 9
                lignes[0] += Alphabet[ord(" ")][0:8]   + " "
                lignes[1] += Alphabet[ord(" ")][8:16]  + " "
                lignes[2] += Alphabet[ord(" ")][16:24] + " "
                lignes[3] += Alphabet[ord(" ")][24:32] + " "
                lignes[4] += Alphabet[ord(" ")][32:40] + " "
                lignes[5] += Alphabet[ord(" ")][40:48] + " "
                lignes[6] += Alphabet[ord(" ")][48:56] + " "
                lignes[7] += Alphabet[ord(" ")][56:64] + " "
                lignes[8] += Alphabet[ord(" ")][64:72] + " "
    
    # Ajouter des meta-espaces pour combler l'espace restant.
    for j in range((largeur_écran-n_meta_caractères-largeur_ligne)//9):
        lignes[0] += Alphabet[ord(" ")][0:8]   + " "
        lignes[1] += Alphabet[ord(" ")][8:16]  + " "
        lignes[2] += Alphabet[ord(" ")][16:24] + " "
        lignes[3] += Alphabet[ord(" ")][24:32] + " "
        lignes[4] += Alphabet[ord(" ")][32:40] + " "
        lignes[5] += Alphabet[ord(" ")][40:48] + " "
        lignes[6] += Alphabet[ord(" ")][48:56] + " "
        lignes[7] += Alphabet[ord(" ")][56:64] + " "
        lignes[8] += Alphabet[ord(" ")][64:72] + " "
    
    # Ajouter les \n sur la dernière ligne.
    lignes[0] += "\n"
    lignes[1] += "\n"
    lignes[2] += "\n"
    lignes[3] += "\n"
    lignes[4] += "\n"
    lignes[5] += "\n"
    lignes[6] += "\n"
    lignes[7] += "\n"
    lignes[8] += "\n"

    # Formatter la variable de retour.
    if not obtenir_matrice:
        # Retourner un string à imprimer.
        # La liste est à ce moment organisée pour pour étaler le texte sur une seule meta-ligne.
        #
        # A1,A1,A1,A1,\n,B1,B1,B1,B1,\n,C1,C1,C1,C1,\n
        # A2,A2,A2,A2,\n,B2,B2,B2,B2,\n,C2,C2,C2,C2,\n
        # A3,A3,A3,A3,\n,B3,B3,B3,B3,\n,C3,C3,C3,C3,\n
        #
        # Si on affiche chaque ligne de la liste, les unes après les autres, le résultat ne sera pas celui attendus
        # Pour que l'affichage se passe correctement, il faut afficher les neuf lignes d'une meta-ligne, puis les neuf des prochaines.
        #
        # Résultat attendus : 
        # A1,A1,A1,A1,\n
        # A2,A2,A2,A2,\n
        # A3,A3,A3,A3,\n
        # B1,B1,B1,B1,\n
        # B2,B2,B2,B2,\n
        # B3,B3,B3,B3,\n
        # C1,C1,C1,C1,\n
        # C2,C2,C2,C2,\n
        # C3,C3,C3,C3,\n
        #
        # Résultat obtenus :
        # A1,A1,A1,A1,\n
        # B1,B1,B1,B1,\n
        # C1,C1,C1,C1,\n
        # A2,A2,A2,A2,\n
        # B2,B2,B2,B2,\n
        # C2,C2,C2,C2,\n
        # A3,A3,A3,A3,\n
        # B3,B3,B3,B3,\n
        # C3,C3,C3,C3,\n 
        #
        # Or chaque ligne de la liste intègre la ligne correspondante de chaque meta-lignes. Il faut donc découper la meta-ligne.
        #
        # String final pour obtenir le résultat attendus:
        # "A1,A1,A1,A1,\n,A2,A2,A2,A2,\n,A3,A3,A3,A3,\n,"+
        # "B1,B1,B1,B1,\n,B2,B2,B2,B2,\n,B3,B3,B3,B3,\n,"+
        # "C1,C1,C1,C1,\n,C2,C2,C2,C2,\n,C3,C3,C3,C3,\n,"
        #
        # Pour ce faire, on ajoutera les neufs lignes de la section correspondant à la meta-ligne au string final
        #
        # Découper la liste :
        # A1,A1,A1,A1,\n, | B1,B1,B1,B1,\n, | C1,C1,C1,C1,\n
        # A2,A2,A2,A2,\n, | B2,B2,B2,B2,\n, | C2,C2,C2,C2,\n
        # A3,A3,A3,A3,\n, | B3,B3,B3,B3,\n, | C3,C3,C3,C3,\n
        #
        # Ajouter chaque ligne au string final :
        #                A1,A1,A1,A1,\n, A2,A2,A2,A2,\n, A3,A3,A3,A3,\n,
        #                       ▲               ▲              ▲
        # A1,A1,A1,A1,\n,───────╯               │              │ 
        # A2,A2,A2,A2,\n,───────────────────────╯              │
        # A3,A3,A3,A3,\n,──────────────────────────────────────╯
        #

        texte_retour : str = ""
        j_début = 0 # Début de la meta-ligne dans la ligne
        j_fin = 0   # Fin de la meta-ligne dans la ligne
        # On boucle jusqu'à ce qu'on arrive à la fin du texte
        while True:
            # On boucle jusqu'à ce qu'on arrive à la fin de la meta-ligne
            while True:
                # Le \n correspond à la fin de la meta-ligne
                if j_fin == len(lignes[0]) or lignes[0][j_fin] == "\n":
                    break
                j_fin += 1
            texte_retour += lignes[0][j_début:j_fin+1]
            texte_retour += lignes[1][j_début:j_fin+1]
            texte_retour += lignes[2][j_début:j_fin+1]
            texte_retour += lignes[3][j_début:j_fin+1]
            texte_retour += lignes[4][j_début:j_fin+1]
            texte_retour += lignes[5][j_début:j_fin+1]
            texte_retour += lignes[6][j_début:j_fin+1]
            texte_retour += lignes[7][j_début:j_fin+1]
            texte_retour += lignes[8][j_début:j_fin+1]
            # Commencer la prochaine ligne au prochain caractère
            # Le j_fin s'arrête sur le \n, donc le début de la prochaine
            #   se trouve un caractère plus loin
            j_fin += 1  
            j_début = j_fin
            # Arrêter la boucle si on est à la fin du texte
            if j_fin >= len(lignes[0]):
                break

        return texte_retour
    else:
        # Retourner la matrice
        # La liste est à ce moment organisée pour pour étaler le texte sur une seule meta-ligne.
        #
        # A1,A1,A1,A1,\n,B1,B1,B1,B1,\n,C1,C1,C1,C1,\n
        # A2,A2,A2,A2,\n,B2,B2,B2,B2,\n,C2,C2,C2,C2,\n
        # A3,A3,A3,A3,\n,B3,B3,B3,B3,\n,C3,C3,C3,C3,\n
        #
        # On veut une matrice organisée comme ceci:
        #
        # Résultat attendus : 
        #[
        #  [A1,A1,A1,A1,\n],
        #  [A2,A2,A2,A2,\n],
        #  [A3,A3,A3,A3,\n],
        #  [B1,B1,B1,B1,\n],
        #  [B2,B2,B2,B2,\n],
        #  [B3,B3,B3,B3,\n],
        #  [C1,C1,C1,C1,\n],
        #  [C2,C2,C2,C2,\n],
        #  [C3,C3,C3,C3,\n]
        #]
        #
        # Mais si on rajoute chaque ligne une à la fois à la matrice, on n'obtient pas le résultat voulus
        #
        # Résultat obtenus:
        # [
        #  [A1,A1,A1,A1,\n,B1,B1,B1,B1,\n,C1,C1,C1,C1,\n],
        #  [A2,A2,A2,A2,\n,B2,B2,B2,B2,\n,C2,C2,C2,C2,\n],
        #  [A3,A3,A3,A3,\n,B3,B3,B3,B3,\n,C3,C3,C3,C3,\n]
        # ]
        #
        # Pour obtenir le résultat attendus, on doit découper la liste et ajouter la section correspondante des neufs 
        # lignes pour chaque meta-ligne, une meta-ligne à la fois.
        #
        # Découper la liste :
        # A1,A1,A1,A1,\n, | B1,B1,B1,B1,\n, | C1,C1,C1,C1,\n
        # A2,A2,A2,A2,\n, | B2,B2,B2,B2,\n, | C2,C2,C2,C2,\n
        # A3,A3,A3,A3,\n, | B3,B3,B3,B3,\n, | C3,C3,C3,C3,\n
        #
        # Ajouter chaque ligne au string final :
        #
        # A1,A1,A1,A1,\n,──╮B1,B1,B1,B1,\n,──╮C1,C1,C1,C1,\n──╮
        # A2,A2,A2,A2,\n,─╮│B2,B2,B2,B2,\n,─╮│C2,C2,C2,C2,\n─╮│
        # A3,A3,A3,A3,\n,╮││B3,B3,B3,B3,\n,╮││C3,C3,C3,C3,\n╮││
        #                │││               │││              │││    [
        #                ││╰───────────────┿┿┿──────────────┿┿┿────▶ [A1,A1,A1,A1,\n],
        #                │╰────────────────┿┿┿──────────────┿┿┿────▶ [A2,A2,A2,A2,\n],
        #                ╰─────────────────┿┿┿──────────────┿┿┿────▶ [A3,A3,A3,A3,\n],
        #                                  ││╰──────────────┿┿┿────▶ [B1,B1,B1,B1,\n],
        #                                  │╰───────────────┿┿┿────▶ [B2,B2,B2,B2,\n],
        #                                  ╰────────────────┿┿┿────▶ [B3,B3,B3,B3,\n],
        #                                                   ││╰────▶ [C1,C1,C1,C1,\n],
        #                                                   │╰─────▶ [C2,C2,C2,C2,\n],
        #                                                   ╰──────▶ [C3,C3,C3,C3,\n]
        #                                                          ]

        matrice : list[list[str]] = []  # Matrice de retour
        j_début = 0 # Début de la meta-ligne à ajouter
        j_fin = 0   # Fin de la meta-ligne à ajouter
        # Boucler jusqu'à la fin du texte
        while True:
            # Boucler jusqu'à la fin de la meta-ligne
            while True:
                # La fin de la meta-ligne est marquée d'un \n
                if j_fin == len(lignes[0]) or lignes[0][j_fin] == "\n":
                    break
                j_fin += 1
            matrice.append(list(lignes[0][j_début:j_fin+1]))
            matrice.append(list(lignes[1][j_début:j_fin+1]))
            matrice.append(list(lignes[2][j_début:j_fin+1]))
            matrice.append(list(lignes[3][j_début:j_fin+1]))
            matrice.append(list(lignes[4][j_début:j_fin+1]))
            matrice.append(list(lignes[5][j_début:j_fin+1]))
            matrice.append(list(lignes[6][j_début:j_fin+1]))
            matrice.append(list(lignes[7][j_début:j_fin+1]))
            matrice.append(list(lignes[8][j_début:j_fin+1]))
            # Commencer la prochaine ligne au prochain caractère
            # Le j_fin s'arrête sur le \n, donc le début de la prochaine
            #   se trouve un caractère plus loin
            j_fin += 1
            j_début = j_fin
            # Sortir de la boucle si on est à la fin du texte
            if j_fin >= len(lignes[0]):
                break

        return matrice

def ajouter_ombre(texte : str|list[list[str]], largeur_écran : int, obtenir_matrice : bool = False):
    """Ajoute une ombre à un meta-texte

    Args:
        texte (str|list[list[str]]): Soit sous forme de string, soit sous forme de matrice, le résultat de `txt2étoiles`.
        largeur_écran (int): largeur de l'écran en nombre de caractères.
        obtenir_matrice (bool, optional): Si `True`, renvoie le meta-texte sous forme de matrice. False par défaut.

    Exemple : 
    ```
    ******    /******
    **  **    |**─┐**
    ****** ─▶ |******
    **  **    |**─┐**
    **  **    |** |**
              ╰─/ ╰─/ ◀─ À Noter que cet effet ajoute une ligne et une
                            à chaque meta-caractère, de ce fait élargit
                            le meta-texte. Ceci est pris en compte dans
                            txt2étoiles, ce qui fait qu'il s’élargira
                            à la largeur spécifié.
    ```

    Si `obtenir_matrice = True` le meta-texte est renvoyé sous forme de double liste ou matrice.
    Exemple :
    ```
             [
    ******     [/,*,*,*,*,*,*],
    **  **     [|,*,*,─,┐,*,*],
    ****** ─▶  [|,*,*,*,*,*,*],
    **  **     [|,*,*,─,┐,*,*],
    **  **     [|,*,*, ,|,*,*],
               [╰,─,/, ,╰,─,/]
             ]
    ```

    Returns:
        str|list[list[str]]: string ou matrice représentant le meta-texte avec une ombre.
    """

    n_meta_caractères = largeur_écran//10   # Nombre de meta-caractères dans le texte. À noter que la largeur du meta-caractère est celle avec une ombre et un espace
                                            #   soit 8 (largeur du meta-caractère) + 1 (ombre) + 1 (espace) = 10
    largeur_lignes = 9*((largeur_écran-n_meta_caractères)//9)+1 # nombre de caractères par ligne dans le meta-texte fournis.
    matrice : list[list[str]] = []  # Matrice reconstituée du meta-texte. Chaque case est un caractère.

    # Si `texte` est déjà sous forme de matrice, il n'est pas nécessaire de le transformer.
    # Sinon, il est nécessaire de refaire la matrice à partir du string.
    if type(texte) == list:
        matrice = texte
    else:
        j_début = 0 # Début de la ligne à ajouter
        j_fin = 0   # Fin de la ligne à ajouter
        # Boucler jusqu'à la fin du texte
        while True:
            # Boucler jusqu'à la fin de la meta-ligne
            while True:
                # La fin de la meta-ligne est marquée d'un \n
                if j_fin == len(texte) or texte[j_fin] == "\n":
                    break
                j_fin += 1
            matrice.append(list(texte[j_début:j_fin+1]))
            # Commencer la prochaine ligne au prochain caractère
            # Le j_fin s'arrête sur le \n, donc le début de la prochaine
            #   se trouve un caractère plus loin
            j_fin += 1
            j_début = j_fin
            # Sortir de la boucle si on est à la fin du texte
            if j_fin >= len(texte):
                break
    
    # Pour faire de la place pour l'ombre il faut rajouter une ligne et une colonne par meta-caractère.
    # Ajouter les colonnes
    for y in range(len(matrice)):
        l_originale = len(matrice[y])-1
        for x in range(len(matrice[y])//9):
            matrice[y].insert(l_originale-(x+1)*9," ")

    # Ajouter les lignes
    l_originale = len(matrice)-1
    for y in range(len(matrice)//9):
        matrice.insert(l_originale-y*9+1,[" "]*10*(largeur_lignes//9))
        matrice[l_originale-y*9+1].append("\n")

    # Faire une convolution matricielle sur le texte pour ajouter les ombres
    matriceB = copy.deepcopy(matrice)   # Matrice de résultat
    for y in range(len(matrice)):
        for x in range(len(matrice[y])):
            # Les caractères comportent des * et des |, donc pour assurer la possibilité d'avoir d'autres symboles, on ne teste que pour l’absence de symbole.
            if matrice[y][x] != " " and matrice[y][x] != "\n" :
                # [ , ]    [  , ]
                # [ ,*] ─▶ [🮣,*]
                if (matrice[y][x+1] == " " or x+1 == len(matrice[y])) and (matrice[y+1][x] == " " or y+1 == len(matrice)) and (matrice[y+1][x+1] == " " or x+1 == len(matrice[y]) or y+1 == len(matrice)):
                    matriceB[y+1][x] = "🮠"
                # [*, ]    [*, ]
                # [ , ] ─▶ [🮠, ]
                if (matrice[y-1][x] == " " or y == 0) and (matrice[y][x-1] == " " or x == 0) and (matrice[y-1][x-1] == ' ' or x==0 or y==0):
                    matriceB[y][x-1] = "🮣"
                # [*, ]    [*, ]
                # [ ,*] ─▶ [╮,*]
                if (matrice[y+1][x] == " " or y+1 == len(matrice))  and (matrice[y][x+1] == " " or x+1 == len(matrice[y])) and (matrice[y+1][x+1] == '*' and x+1 < len(matrice[y]) and y+1 < len(matrice)):
                    matriceB[y+1][x] = "╮"
                #   [*]      [*]
                # [ ,*] ─▶ [│,*]
                if ((y > 0 and matrice[y-1][x] == "*") and (matrice[y][x-1] == " " or x == 0)) and (not matrice[y-1][x-1] == '*' or y==0 or x==0):
                    matriceB[y][x-1] = "│"
                # [*,*]    [*,*]
                # [ , ] ─▶ [ ,─]
                if (x+1 < len(matrice[y]) and matrice[y][x+1] != " ") and (matrice[y+1][x] == " " or y+1 == len(matrice)):
                    matriceB[y+1][x] = "─"
                # [*,*]    [*,*]
                # [ , ] ─▶ [ ,─]
                if (matrice[y+1][x-1] == " " or y+1 == len(matrice) or x == 0) and  (matrice[y+1][x] == " " or y+1 == len(matrice)) and (matrice[y][x-1] == " " or x == 0):
                    matriceB[y+1][x-1] = "╰"
                # [ ,*]    [ ,*]
                # [ ]   ─▶ [╰]
                if (matrice[y+1][x-1] == " " or y+1 == len(matrice) or x == 0) and (matrice[y+1][x] != " " and y+1 <= len(matrice)) and (matrice[y][x-1] != " " and x > 0):
                    matriceB[y+1][x-1] = "┐"
    

    if not obtenir_matrice:
        # retourner un string.
        texte_retour = ""
        for y in range(len(matriceB)):
            for x in range(len(matriceB[y])):
                # if matriceB[y][x] == '\n':
                #     texte_retour += 'X'
                texte_retour += matriceB[y][x]
        
        return texte_retour
    else:
        # Retourner la matrice
        return matriceB

def animer(texte : str|list[list[str]], largeur_écran : int, temps : float, Paramètres_animation : dict[str:float]):
    """Anime le meta-texte avec divers effets.

    Args:
        texte (str|list[list[str]]): texte à animer
        largeur_écran (int): largeur de l'écran en nombre de caractères
        temps (float): temps présent en secondes

    Returns:
        str|list[list[str]]: meta-texte animé pour l'instant donné par `temps`
    
    Cette fonction ne renvoie le meta-texte animé que pour un instant. Pour obtenir une animation, passer le meta-texte
    dans la fonction de façon continue et recommencer à chaque instant.
        
    Applique les effets suivants: 
     - Reflet métallique qui passe sur les lettres à intervalles régulières :
    ```
        /******    /***###
        |**─┐**    |**─┐#*
        |****** ─▶ |*###**
        |**─┐**    |##─┐**
        |** |**    |#* |**
        ╰─/ ╰─/    ╰─/ ╰─/
    ```
    
     - Vagues qui font rebondir les caractères :
    ```
                                ───▶
                             ******
               ****** ****** **  ** ****** ******
        ****** **  ** **  ** ****** **  ** **  ** ****** ****** ****** ******
        **  ** ****** ******        ****** ****** **  ** **  ** **  ** **  **
        ******                                    ****** ****** ****** ******
    ```

     - Effets de particules :
    ```
          v         |
         >+<    ¤   =
      ¤ **^***    -=@=-
        *¤  **  v   =
        ****** >+<  |
                ^
    ```

    """
    timer = time.time() # Mesure du temps passé à calculer l'animation

    largeur_lignes : int = 0    # Largeur des lignes
    hauteur_texte : int = 0     # Nombre de lignes composant le texte
    matrice : list[list[str]] = []  # Matrice représentant le meta-texte
        
    # Si `texte` est déjà sous forme de matrice, il n'est pas nécessaire de le transformer.
    # Sinon, il est nécessaire de refaire la matrice à partir du string.
    if type(texte) == list:
        matrice = texte
        hauteur_texte = len(matrice)
        largeur_lignes = len(matrice[0])
    else:
        global temps_recomposition
        temps_recomposition = time.time()

        largeur_lignes = 10*(largeur_écran//10)+1
        hauteur_texte = len(texte)//largeur_lignes

        j_début = 0 # Début de la ligne à ajouter
        j_fin = 0   # Fin de la ligne à ajouter
        # Boucler jusqu'à la fin du texte
        while True:
            # Boucler jusqu'à la fin de la meta-ligne
            while True:
                # La fin de la meta-ligne est marquée d'un \n
                if j_fin == len(texte) or texte[j_fin] == "\n":
                    break
                j_fin += 1
            matrice.append(list(texte[j_début:j_fin+1]))
            # Commencer la prochaine ligne au prochain caractère
            # Le j_fin s'arrête sur le \n, donc le début de la prochaine
            #   se trouve un caractère plus loin
            j_fin += 1
            j_début = j_fin
            # Sortir de la boucle si on est à la fin du texte
            if j_fin >= len(texte):
                break
        
        temps_recomposition = time.time()-temps_recomposition

    # Effet de reflet métallique.
    # Le principe est de changer les * pour des # sur les caractères qui tombent sur la ligne.
    # Une implémentation naïve vérifierais pour tout les caractère s'il tombe à une certaine distance de la ligne. Cette approche est très inefficace, car elle nécessite de vérifier
    #   plusieurs caractères qui sont loins de la ligne.
    # À la place, nous pouvons utiliser la fonction x=b-y et passer à travers tout les y pour changer le bon y. Cette approche vient avec son inconvénient, par contre : 
    #   si l'angle est trop aiguë, il se peut qu'on aie besoin de plus d'un y pour chaque x, ce qui veut dire qu'il y aura des trous dans la ligne. Pour éviter ce
    #   problème l'angle est fixé à 45°.
    # Pour donner de l'épaisseur à la ligne, plusieurs x sont changés pour chaque y.
    # Pour faire bouger la ligne, on ajoute un décalage (b) qui sortira des bornes du meta-texte pour avoir une pause entre chaque reflet métallique et qui se répétera grâce à un modulo
    global temps_ligne
    temps_ligne = time.time()

    REFLET_TEMPS_MOUVEMENT = Paramètres_animation["REFLET_TEMPS_MOUVEMENT"]   # Temps que le reflet métallique prend à faire toute la longueur du meta-texte, en secondes
    REFLET_TEMPS_PAUSE = Paramètres_animation["REFLET_TEMPS_PAUSE"]         # Temps entre chaque reflet métallique, en secondes
    REFLET_LARGEUR = int(Paramètres_animation["REFLET_LARGEUR"])       # Largeur totale de la ligne
    matriceB = copy.deepcopy(matrice)
    b = int( largeur_lignes*( (temps/REFLET_TEMPS_MOUVEMENT)%((REFLET_TEMPS_MOUVEMENT+REFLET_TEMPS_PAUSE)/REFLET_TEMPS_MOUVEMENT) ) )
    # range(x) exclue x, mais on a besoin de se rendre à x, alors on fait range(x+1)
    for y in range(b+1):
        for x in range(REFLET_LARGEUR):
            if y > 0 and y < len(matrice) and (b-y)+x-(REFLET_LARGEUR//2) > 0 and (b-y)+x-2 < len(matrice[y]) and matrice[y][(b-y)+x-(REFLET_LARGEUR//2)] == '*':
                matriceB[y][(b-y)+x-(REFLET_LARGEUR//2)] = '#'

    temps_ligne = time.time()-temps_ligne

    # Vague qui font rebondir les caractères
    # Ici, on choisit un meta-caractère et on fait le fait monter, lui et quelques-uns autour, de quelques lignes, en suivant une onde sinusoïdale.
    global temps_vagues
    temps_vagues = time.time()

    matrice = copy.deepcopy(matriceB)
    # cspell:ignore carac
    n_meta_carac_lignes = largeur_lignes//10    # nombre de méta-caractères par lignes
    n_meta_carac_colonnes = hauteur_texte//10   # nombre de méta-caractères par colonnes
    n_meta_carac = n_meta_carac_lignes*n_meta_carac_colonnes    # nombre de méta-caractères au total
    VAGUE_VITESSE = Paramètres_animation["VAGUE_VITESSE"]       # Vitesse de la vague en meta-caractères/seconde
    VAGUE_LARGEUR = int(Paramètres_animation["VAGUE_LARGEUR"]//2)    # Largeur de la vague en meta-caractères. Toujours diviser par 2.
    VAGUE_HAUTEUR = Paramètres_animation["VAGUE_HAUTEUR"]       # Hauteur de la vague en caractères.
    VAGUE_TEMPS_PAUSE = Paramètres_animation["VAGUE_TEMPS_PAUSE"]# Temps entre chaque cycle complet de la vague en secondes.
    curseur = int((VAGUE_VITESSE*temps)%(n_meta_carac+VAGUE_VITESSE*VAGUE_TEMPS_PAUSE))   # Indexe du meta-caractère sélectionné
    # On passe à travers les LARGEUR_VAGUE meta-caractères de chaque côtés du curseur.
    for i in range(VAGUE_LARGEUR):
        j = i-(VAGUE_LARGEUR)//2 + curseur # Indexe du meta-caractère autour du curseur
        if j >= 0 and j < n_meta_carac:
            # Si j est à l'intérieur de la liste de meta-caractères.
            décalage = int(VAGUE_HAUTEUR*max( math.sin( ( (VAGUE_VITESSE/VAGUE_LARGEUR)*temps - (j/VAGUE_LARGEUR) ) * 2*math.pi ), 0))
            # Effacer le caractère
            for x in range(10):
                for y in range(10):
                    matriceB[ 10*(j//n_meta_carac_lignes) + y ][ 10*(j%n_meta_carac_lignes) + x ] = ' '
            # Le réimprimer plus haut
            for x in range(10):
                for y in range(10):
                    position_finale_y = 10*(j//n_meta_carac_lignes) + y - décalage
                    if position_finale_y >= 0 and position_finale_y < len(matrice) and matrice[ 10*(j//n_meta_carac_lignes) + y ][ 10*(j%n_meta_carac_lignes) + x ] != ' ':
                        matriceB[ position_finale_y ][ 10*(j%n_meta_carac_lignes) + x ] = matrice[ 10*(j//n_meta_carac_lignes) + y ][ 10*(j%n_meta_carac_lignes) + x ]

    temps_vagues = time.time()-temps_vagues

    #cspell:ignore posx
    # Particules
    # Les particules sont stockées dans une liste de 3-tuples.
    #
    #                 ( vie,  posx,posy )
    #                  └─┬──┘└────────┬┘
    #┌───────────────────┴─────────┐ ┌┴────────────────────────────┐
    # Durée de vie de la particule. | Position x, y de la particule
    # Elle commence entre 1 et 4 et | en caractères. cette position
    # diminue à vitesse constante   | peut changer à travers le
    # cours de sa durée de vie.     | temps.
    # Lorsqu'il atteint 0, la       | 
    # particule meurt.              | 
    #
    # Une nouvelle particule a une chance d'être créée à chaque image et afin de maintenir une densité constante pour tout les meta-textes, 
    #   cette probabilité est proportionnelle au nombre de meta-caractères.
    # Les particules ont une chance de bouger dans une direction aléatoire avec un biais vers le bas, à chaque image.
    # 
    # La vie d'une particule est divisée en trois niveau et vient ainsi avec trois images.
    # vie = 2-4 | vie = 1-2 | vie = 0-1 |
    #           |           |           |
    #     |     |           |           |
    #     =     |     v     |           |
    #   -=@=-   |    >+<    |     ¤     |
    #     =     |     ^     |           |
    #     |     |           |           |
    #

    global temps_étoiles
    global temps_précédent
    temps_étoiles = time.time()

    PART_DURÉE_VIE = Paramètres_animation["PART_DURÉE_VIE"] # Durée de vie moyenne en secondes.
    PART_DENSITÉ = Paramètres_animation["PART_DENSITÉ"]
    delta_temps = time.time()-temps_précédent
    # Réduire la taille de toutes les particules, détruire celles qui sont à 0 et bouger les autres aléatoirement.
    global étoiles
    l_originale = len(étoiles)-1
    for i in range(len(étoiles)):
        # Réduire la taille des particules
        étoiles[l_originale-i] = (étoiles[l_originale-i][0]-(2*delta_temps/PART_DURÉE_VIE),étoiles[l_originale-i][1],étoiles[l_originale-i][2])
        # Détruire celles qui sont à 0
        if étoiles[l_originale-i][0] == 0:
            étoiles.pop(l_originale-i)
        else:
            # Bouger les particules dans une direction aléatoire.
            if random.randint(0,20) < 1:
                étoiles[l_originale-i] = (étoiles[l_originale-i][0],max(min(étoiles[l_originale-i][1]+random.randint(-1,1),len(matrice[0])-2),0),max(min(étoiles[l_originale-i][2]+random.randint(-1,1),len(matrice)-1),0))
            # Ajouter un biais vers le bas pour avoir l'impression qu'elles tombent
            if random.randint(0,10) < 1:
                étoiles[l_originale-i] = (étoiles[l_originale-i][0],étoiles[l_originale-i][1],min(étoiles[l_originale-i][2]+1,len(matrice)-1))
    
    # Ajouter une particule aléatoire. La chance d'ajouter une particule est proportionnelle au nombre de meta-caractères pour conserver une densité uniforme, peut importe
    # la taille de l'écran.
    for i in range(n_meta_carac):
        if random.randrange(0,1000000)/1000000 < PART_DENSITÉ/((1/delta_temps)*PART_DURÉE_VIE):
            étoiles.append((random.randrange(1,4),random.randint(0,largeur_lignes-2),random.randint(0,hauteur_texte)-1))

    # Dessiner les particules
    for e in étoiles:
        if e[0] > 2:
            matriceB[e[2]][e[1]] = '@'
            for i in range(4):
                dx = 0
                dy = 0
                match i:
                    case 0:
                        dx = 1
                    case 1:
                        dx = -1
                    case 2:
                        dy = 1
                    case 3:
                        dy = -1
                if e[1]+dx >= 0 and e[2]+dy >= 0 and e[1]+dx < len(matrice[0])-1 and e[2]+dy < len(matrice):
                    matriceB[e[2]+dy][e[1]+dx] = '='
                if e[1]+2*dx >= 0 and e[2]+2*dy >= 0 and e[1]+2*dx < len(matrice[0])-1 and e[2]+2*dy < len(matrice):
                    if dx == 0:
                        matriceB[e[2]+2*dy][e[1]+2*dx] = '|'
                    if dy == 0:
                        matriceB[e[2]+2*dy][e[1]+2*dx] = '-'
        elif e[0] > 1:
            matriceB[e[2]][e[1]] = '+'
            for i in range(4):
                dx = 0
                dy = 0
                caractère = ""
                match i:
                    case 0:
                        dx = 1
                        caractère = '<'
                    case 1:
                        dx = -1
                        caractère = ">"
                    case 2:
                        dy = 1
                        caractère = "^"
                    case 3:
                        dy = -1
                        caractère = "v"
                if e[1]+dx >= 0 and e[2]+dy >= 0 and e[1]+dx < len(matrice[0])-1 and e[2]+dy < len(matrice):
                    matriceB[e[2]+dy][e[1]+dx] = caractère
        elif e[0] > 0:
            matriceB[e[2]][e[1]] = '¤'

    temps_étoiles = time.time()-temps_étoiles

    # Transformer la matrice en string pour être imprimé
    global temps_décomposition
    temps_décomposition = time.time()

    texte_retour = ""
    for y in range(len(matriceB)):
        for x in range(len(matriceB[y])):
            # if matriceB[y][x] == '\n':
            #     texte_retour += 'X'
            texte_retour += matriceB[y][x]
    temps_décomposition = time.time()-temps_décomposition

    global temps_animer
    temps_animer = time.time()-timer

    temps_précédent = time.time()
    
    return texte_retour

def main():

    texte = ""  # Texte à imprimer

    if "-test" in sys.argv or "-t" in sys.argv or len(sys.argv) == 1:
        # Texte de test
        texte = (" Cet Alphabet"+
                " De Vingt Six\n"+
                " Lettres Dans"+
                " Un Carré Qui\n"+
                " Range Nickel"+
                " Ce Pangramme\n"+
                " Hyper Fou De"+
                " La Toile Web\n"+
                " Fait Ici Sur"+
                " Douze Lignes\n"+
                " Juste Trente"+
                " Mots En Tout\n")
    elif "-testtout" in sys.argv or "-tt" in sys.argv:
        # Tester tout les caractères disponibles
        for i in range(0xff):
            texte += chr(i)
    else:
        # Utiliser les texte fournis par l'utilisateur
        texte = sys.argv[1]

    largeur_écran = 50  # Largeur de l'écran en caractères
    if "-largeur" in sys.argv or "-l" in sys.argv:
        # Spécifie la largeur de l'écran de la part de l'utilisateur
        i = 0
        if "-largeur" in sys.argv:
            i = sys.argv.index("-largeur")
        else:
            i = sys.argv.index("-l")
        largeur_écran = int(sys.argv[i+1])

    performances : bool = False # Si True, affiche les performances de l'animation
    if "-performance" in sys.argv or "-p" in sys.argv:
        performances = True

    Paramètres_animation = {
        "REFLET_TEMPS_MOUVEMENT": 0.5,
        "REFLET_TEMPS_PAUSE": 2,
        "REFLET_LARGEUR": 5,
        "VAGUE_VITESSE": 10,
        "VAGUE_LARGEUR": 8,
        "VAGUE_HAUTEUR": 3,
        "VAGUE_TEMPS_PAUSE": 2,
        "PART_DURÉE_VIE": 2,
        "PART_DENSITÉ": 0.2
    }
    if "-param_anim" in sys.argv or "-pa" in sys.argv:
        argv_texte = ""
        for v in sys.argv:
            argv_texte += v

        indexe_début = -1 
        if "-param_anim" in sys.argv:
            indexe_début = argv_texte.index("-param_anim")
        else:
            indexe_début = argv_texte.index("-pa")
        
        i = indexe_début
        débuté = False
        débuté_clé = False
        débuté_valeur = False
        clé = ""
        valeur = ""
        while not argv_texte[i] == '}':
            i = i+1
            if argv_texte[i] == '{':
                débuté = True
                continue
            if débuté:
                if not débuté_clé and not débuté_valeur and argv_texte[i] != ' ':
                    débuté_clé = True
                    clé = argv_texte[i]
                    continue
                if débuté_clé and argv_texte[i] != ':':
                    clé += argv_texte[i]
                    continue
                if débuté_clé and argv_texte[i] == ':':
                    débuté_clé = False
                    débuté_valeur = True
                    continue
                if débuté_valeur and (argv_texte[i] == ',' or argv_texte[i] == '}'):
                    débuté_valeur = False
                    if clé in Paramètres_animation.keys():
                        Paramètres_animation[clé] = float(valeur)
                    clé = ""
                    valeur = ""
                    continue
                if débuté_valeur and argv_texte[i] != ' ':
                    valeur += argv_texte[i]
                    continue
            if i+1 >= len(argv_texte)-1:
                break
    if "-aide" in sys.argv or "-help" in sys.argv or "-h" in sys.argv or "-?" in sys.argv:
        # VSCode ne prend pas une police monospace pour certains caractères, comme 🮣, mais le terminal oui, ce qui fait que le
        # titre ci-dessous n'est pas lisible dans VSCode, mais il l'est dans le terminal.
        print(
            "                       🮣**          🮣****\n"+
            "                       ╰─╮**        │****\n"+
            "   🮣**           🮣**  🮣******       │****\n"+
            "  🮣****         🮣**** │**─┐** 🮣* 🮣* │****\n"+
            "  ╰┐**🮠 🮣** 🮣** ╰┐**🮠 │****** ╰╮**🮠 ╰───🮠\n"+
            "   │**  ╰─╮**─🮠  │**  │**─┐** 🮣*─╮* 🮣****\n"+
            "   ╰┐** 🮣**─╮**  ╰┐** │** │** ╰🮠 ╰🮠 │****\n"+
            "    ╰─🮠 ╰─🮠 ╰─🮠   ╰─🮠 ╰─🮠 ╰─🮠       ╰───🮠\n"+
            "\n"+
            "Ce programme prend un string et l'imprime en gros (dans le style du titre ci-haut) dans le terminal avec quelques effets.\n"+
            "\n"+
            "Utilisation:\n"+
            "Défis.py [Texte] [Options]\n"+
            "  -help -aide -h -?       Affiche la page d'aide\n"+
            "  -performance -p         Affiche les performances du programme\n"+
            "  -test -t                Remplace le texte par un texte de test\n"+
            "  -testtout -tt           Remplace le texte par les 256 premiers caractères du code Unicode\n"+
            "  -largeur -l [LARGEUR]   Spécifie la largeur de l'écran en caractères (20 par défauts)\n"+
            "\n"+
            "  -param_anim -pa {[PARAM]:[VALEUR],[...]}    Spécifie les paramètres d'animation.\n"+
            "          Paramètres disponibles:\n"+
            "              REFLET_TEMPS_MOUVEMENT  Temps que prend le reflet métallique à traverser le meta-texte en secondes\n"+
            "              REFLET_TEMPS_PAUSE      Temps de pause entre les reflets métalliques en secondes\n"+
            "              REFLET_LARGEUR          Largeur du reflet en caractères\n"+
            "              VAGUE_VITESSE           Vitesse de la vague de rebond des meta-caractères en meta-caractères/secondes\n"+
            "              VAGUE_LARGEUR           Largeur de la vagues en meta-caractères\n"+
            "              VAGUE_HAUTEUR           Hauteur de la vague en caractères\n"+
            "              VAGUE_TEMPS_PAUSE       Temps de pause entre chaque vagues en secondes\n"+
            "              PART_DURÉE_VIE          Durée de vie des particules en secondes\n"+
            "              PART_DENSITÉ            Densité moyenne des particules en particules/meta-caractère\n"+
            "\n"+
            "Fonctionnalités:\n"+
            "Affiche un texte arbitraire en grosses lettres dans le terminal dans une police mono-espacée\n"+
            "Possibilité d'ajouter une ombre procédurale au texte.\n"+
            "Possibilité d'ajouter de l'animation au texte. Les effets d'animations sont :\n"+
            "  - Un reflet métallique qui passe sur les lettres à intervalles régulières\n"+
            "  - Une vague qui fera sauter les lettres à intervalles régulières\n"+
            "  - Des effets de particules qui imitent un scintillement\n"+
            "La possibilité de d'activer/désactiver plusieurs fonctionnalités\n"+
            "La possibilité d'afficher les performances du programme\n"+
            "\n"+
            "Conventions dans ce code:\n"+
            "\n"+
            "CARACTÈRES/META-CARACTÈRES\n"+
            "Pour afficher les caractères en gros dans le terminal, il est nécessaire d'utiliser de plus petits caractères.\n"+
            "Afin d'éclaircir la confusion entre les gros et les petits caractères, on utilisera le terme normal pour les\n"+
            "petits caractères et le terme meta-caractère pour les gros caractères. Ainsi :\n"+
            "\n"+
            "Caractère :               Caractère imprimé dans le terminal\n"+
            "Meta-caractère :          Gros caractère composé de caractères\n"+
            "Ligne :                   Ligne de caractère de terminal\n"+
            "Meta-ligne :              Ligne composée de caractères\n"+
            "Largeur de l'écran :      Largeur de l'écran en nombre de caractères\n"+
            "Meta-Largeur de l'écran : Largeur de l'écran en nombre de meta-caractères\n"+
            "etc...\n"+
            "\n"+
            "TAILLE DES META-CARACTÈRES\n"+
            "Les meta-caractères font obligatoirement 8x9 caractères, 9x9 avec l'espace entre chacun d'entre eux et 10x10 en ajoutant l'ombre.\n"
        )
        exit(1)

    texte = txt2étoiles(texte, largeur_écran,obtenir_matrice=False) # Transformer en étoiles
    texte = ajouter_ombre(texte,largeur_écran,obtenir_matrice=False)    # Ajouter l'ombre
    timer = time.time()
    while True:
        print("\033c" + animer(texte,largeur_écran,time.time(), Paramètres_animation))    # \033c est un caractère qui efface le terminal.
        print("Ctrl+C pour sortir du programme")

        if performances:
            print(str(round(1/(time.time()-timer)))+"FPS")
            print("temps total : " + str(round(1000*(time.time()-timer))) + "ms")
            print("temps_animer : " + str(round(1000*temps_animer))+"ms")
            print("\ttemps_recomposition :\t" + str(round(1000*temps_recomposition))+"ms")
            print("\ttemps_ligne : \t\t" + str(round(1000*temps_ligne))+"ms")
            print("\ttemps_vagues :\t\t" + str(round(1000*temps_vagues))+"ms")
            print("\ttemps_étoiles :\t\t" + str(round(1000000*temps_étoiles))+"µs")
            print("\ttemps_décomposition :\t" + str(round(1000*temps_décomposition))+"ms")

        timer = time.time()
        time.sleep(max((1/60)-(time.time()-timer),0))   # Cap les FPS à 60 FPS, pour éviter d'avoir du clignotement à l'écran.

if __name__ == "__main__":
    main()

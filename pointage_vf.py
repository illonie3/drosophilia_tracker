import cv2
import os
import glob
import re
import numpy as np
import csv
import sys
import tkinter as tk
from tkinter import messagebox

# --- Paramètres des fichiers ---
dossier_images = sys.argv[1]
dossier_sortie = os.path.join(dossier_images, "verification")

if not os.path.exists(dossier_sortie):
    os.makedirs(dossier_sortie)

pattern = os.path.join(dossier_images, "Image_Record*_Data1.png")
chemins_images = glob.glob(pattern)

def extraire_numero(chemin):
    match = re.search(r'Record(\d+)', os.path.basename(chemin))
    return int(match.group(1)) if match else 0

chemins_images.sort(key=extraire_numero)

if not chemins_images:
    print("Aucune image trouvée. Vérifiez le chemin ou l'extension.")
    exit()

# --- Création du fond parfait sans mouche ---
print("Calcul du fond artificiel sans mouche en cours... Patientez...")
images_pour_fond = []
step = max(1, len(chemins_images) // 30)

for chemin in chemins_images[::step]:
    img = cv2.imread(chemin, cv2.IMREAD_GRAYSCALE)
    images_pour_fond.append(img)

fond = np.median(images_pour_fond, axis=0).astype(np.uint8)
fond_flou = cv2.GaussianBlur(fond, (21, 21), 0)

cv2.imwrite(os.path.join(dossier_sortie, "00_FOND_SANS_MOUCHE.png"), fond)

# ---  Sélection manuelle du ROI  ---
print("\n" + "="*50)
print("ACTION REQUISE :")
print("1. Une fenêtre nommée 'Selection du tube' va s'ouvrir.")
print("2. Dessinez un rectangle avec la souris pour englober L'INTÉRIEUR du tube.")
print("3. Appuyez sur la touche ENTRÉE ou ESPACE pour valider (ou 'c' pour annuler).")
print("="*50 + "\n")


cv2.namedWindow("Selection du tube", cv2.WINDOW_NORMAL)

cv2.resizeWindow("Selection du tube", 1000, 800)

# Ouvre la fenêtre interactive
x_roi, y_roi, w_roi, h_roi = cv2.selectROI("Selection du tube", fond, showCrosshair=True, fromCenter=False)
cv2.destroyAllWindows()

if w_roi == 0 or h_roi == 0:
    print("Erreur : Aucune zone n'a été sélectionnée. Arrêt du programme.")
    exit()

X_MIN, X_MAX = int(x_roi), int(x_roi + w_roi)
Y_MIN, Y_MAX = int(y_roi), int(y_roi + h_roi)

print(f"Zone validée ! Coordonnées retenues : X({X_MIN} à {X_MAX}), Y({Y_MIN} à {Y_MAX})")

# --- Paramètres de détection ---
SEUIL_CONTRASTE = int(sys.argv[2])

trajectoire_x = []
trajectoire_y = []
noms_images = []
images_manuelles = []

# --- Fonction pour le pointage manuel ---
coords_clic = []
def clic_souris(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:  # Si clic gauche
        coords_clic.clear()
        coords_clic.append((x, y))

# ---  Traitement des images ---
print(f"Début du traitement des {len(chemins_images)} images...")

for chemin in chemins_images:
    nom_fichier = os.path.basename(chemin)
    img_couleur = cv2.imread(chemin)
    img_gris = cv2.cvtColor(img_couleur, cv2.COLOR_BGR2GRAY)

    img_gris_flou = cv2.GaussianBlur(img_gris, (21, 21), 0)
    difference = cv2.absdiff(fond_flou, img_gris_flou)

    _, masque = cv2.threshold(difference, SEUIL_CONTRASTE, 255, cv2.THRESH_BINARY)
    masque = cv2.morphologyEx(masque, cv2.MORPH_OPEN, np.ones((3,3), np.uint8))

    masque_roi = np.zeros_like(masque)
    masque_roi[Y_MIN:Y_MAX, X_MIN:X_MAX] = masque[Y_MIN:Y_MAX, X_MIN:X_MAX]

    contours, _ = cv2.findContours(masque_roi, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    x_centre, y_centre = None, None

    if contours:
        contours_valides = [c for c in contours if 2 < cv2.contourArea(c) < 600]

        if contours_valides:
            drosophile = max(contours_valides, key=cv2.contourArea)
            M = cv2.moments(drosophile)
            if M["m00"] != 0:
                x_centre = int(M["m10"] / M["m00"])
                y_centre = int(M["m01"] / M["m00"])
            else:
                x_centre, y_centre = drosophile[0][0]

            cv2.circle(img_couleur, (x_centre, y_centre), radius=4, color=(0, 0, 255), thickness=-1)
            cv2.drawContours(img_couleur, [drosophile], -1, (0, 255, 0), 1)

# --- INTERVENTION MANUELLE SI MOUCHE NON DÉTECTÉE ---
    if x_centre is None:
        print(f"Mouche perdue sur {nom_fichier} ! Cliquez dessus puis appuyez sur ENTRÉE.")
        images_manuelles.append(nom_fichier)
        cv2.namedWindow("Pointage manuel", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("Pointage manuel", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback("Pointage manuel", clic_souris)

        coords_clic.clear() # Remise à zéro du clic

        while True:

            img_affichage = img_couleur.copy()

            if coords_clic:
                cv2.circle(img_affichage, coords_clic[0], radius=4, color=(0, 0, 255), thickness=-1)

            cv2.imshow("Pointage manuel", img_affichage)
            touche = cv2.waitKey(1) & 0xFF

            # Validation si on appuie sur ENTRÉE (13) ou ESPACE (32) ET qu'on a bien cliqué
            if touche in [13, 32] and coords_clic:
                x_centre, y_centre = coords_clic[0]
                cv2.circle(img_couleur, (x_centre, y_centre), radius=4, color=(0, 0, 255), thickness=-1)
                cv2.destroyWindow("Pointage manuel")
                break


    cv2.rectangle(img_couleur, (X_MIN, Y_MIN), (X_MAX, Y_MAX), (255, 0, 0), 2)

    trajectoire_x.append(x_centre)
    trajectoire_y.append(y_centre)
    noms_images.append(nom_fichier)

    chemin_sauvegarde = os.path.join(dossier_sortie, nom_fichier)
    cv2.imwrite(chemin_sauvegarde, img_couleur)

print("\nTraitement terminé !")
print(f"Vos images annotées se trouvent dans le dossier : {dossier_sortie}")

# --- Export de la trajectoire en CSV ---
chemin_csv = os.path.join(dossier_images, "trajectoire_drosophile.csv")

# Création du fichier en mode écriture
with open(chemin_csv, mode='w', newline='', encoding='utf-8') as fichier_csv:
    # On utilise le point-virgule car Excel français
    writer = csv.writer(fichier_csv, delimiter=';')

    # En-têtes de colonnes
    writer.writerow(["Image", "Position X", "Position Y"])

    # Données pour chaque image
    for i in range(len(noms_images)):
        writer.writerow([noms_images[i], trajectoire_x[i], trajectoire_y[i]])

print(f"Trajectoire exportée avec succès au format CSV dans : {chemin_csv}")

# remarque : la position est calculée par rapport à l'image entière, non par rappoert au ROI


# Construction du message textuel
texte_bilan = "L'analyse est terminée avec succès !\n\n"
texte_bilan += "Fichiers produits :\n"
texte_bilan += "- Images annotées : dans le sous-dossier 'verification'\n"
texte_bilan += "- Données exportées : trajectoire_drosophile.csv\n\n"

if len(images_manuelles) > 0:
    texte_bilan += f"Pointages manuels nécessaires ({len(images_manuelles)} image(s)) :\n"
    # On affiche les 15 premières images maximum pour que la fenêtre ne soit pas trop grande
    texte_bilan += "\n".join(images_manuelles[:15])
    if len(images_manuelles) > 15:
        texte_bilan += f"\n... et {len(images_manuelles) - 15} autres."
else:
    texte_bilan += "Parfait : Aucun pointage manuel n'a été nécessaire !"

# Pop-up
racine = tk.Tk()
racine.withdraw()
racine.attributes('-topmost', True)  # Force le popup à s'afficher au-dessus de toutes vos fenêtres Windows
messagebox.showinfo("Bilan de l'analyse", texte_bilan)
racine.destroy()
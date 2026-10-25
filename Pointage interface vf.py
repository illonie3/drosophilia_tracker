import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import sys
import os

def choisir_dossier():
    dossier = filedialog.askdirectory(title="Sélectionner le dossier des images")
    if dossier:
        var_dossier.set(dossier)

def lancer_analyse():
    dossier = var_dossier.get()
    seuil = var_seuil.get()

    if not dossier:
        messagebox.showwarning("Attention", "Veuillez choisir un dossier.")
        return

    # Chemin exact vers le code
    chemin_script = r"c:\users\leo\documents\espci\pse\pointage_vf.py"

    print(f"Lancement indépendant de l'analyse dans : {dossier}")

    # Lancement du code dans un processus totalement séparé.
    # Evite les conflits entre openCV et tkinter
    subprocess.Popen([sys.executable, chemin_script, dossier, seuil])
    fenetre.destroy()

# ==========================================
# CRÉATION DE L'INTERFACE
# ==========================================
fenetre = tk.Tk()
fenetre.title("Analyse de Géotaxie")
fenetre.geometry("500x250")
fenetre.configure(padx=20, pady=20)

var_dossier = tk.StringVar()
var_seuil = tk.StringVar(value="40")

# --- Choix du dossier ---
tk.Label(fenetre, text="1. Dossier contenant les images :", font=("Arial", 10, "bold")).pack(anchor="w")
frame_dos = tk.Frame(fenetre)
frame_dos.pack(fill="x", pady=5)
tk.Entry(frame_dos, textvariable=var_dossier, state='readonly').pack(side=tk.LEFT, fill="x", expand=True, padx=(0,5))
tk.Button(frame_dos, text="Parcourir...", command=choisir_dossier).pack(side=tk.RIGHT)

# --- Choix du seuil ---
tk.Label(fenetre, text="2. Seuil de contraste :", font=("Arial", 10, "bold")).pack(anchor="w", pady=(10, 0))
tk.Spinbox(fenetre, from_=0, to=255, textvariable=var_seuil, width=10).pack(anchor="w", pady=5)

# --- Bouton de lancement ---
tk.Button(fenetre, text="LANCER L'ANALYSE", command=lancer_analyse, bg="#4CAF50", fg="white", font=("Arial", 10, "bold")).pack(fill="x", pady=(15, 0))

fenetre.mainloop()
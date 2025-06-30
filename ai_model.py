import pandas as pd
import numpy as np

def geopolitical_risk_score(row, zones_geo):
    # Démo : score élevé si dans une zone à risque, sinon basé sur des critères fictifs
    zone = next((z for z in zones_geo if z["Pays"].lower() == row["Pays"].lower()), None)
    if zone:
        return 0.85  # Ex: 0.85/1 si zone à conflit
    # Exemple : pondère le score selon le pays, la dépendance fournisseur, etc.
    base = 0.3
    if row.get("Dépendance", 0) >= 0.7:
        base += 0.4
    return min(base, 1.0)

def recommend_action(row, zones_geo):
    score = row["Score risque géopolitique"]
    if score >= 0.7:
        return "Diversification ou relocalisation urgente"
    elif score >= 0.5:
        return "Renégociation & veille renforcée"
    else:
        return "Surveillance standard"

import numpy as np

def geopolitical_risk_score(row, zones_geo):
    """
    Calcule un score de risque géopolitique pour un fournisseur.
    - Score élevé si situé dans une zone à risque.
    - Sinon, pondère selon la dépendance (colonne 'Dépendance' entre 0 et 1).
    """
    zone = next((z for z in zones_geo if z["Pays"].lower() == row["Pays"].lower()), None)
    if zone and zone.get("Criticité", "").lower() == "élevée":
        return 0.85
    elif zone and zone.get("Criticité", "").lower() == "moyenne":
        return 0.65
    # Sinon, pondération sur la dépendance fournisseur
    base = float(row.get("Dépendance", 0)) if "Dépendance" in row else 0.3
    return min(base, 1.0)

def recommend_action(row, zones_geo):
    """
    Donne une recommandation IA selon le score de risque géopolitique.
    """
    score = row["Score risque géopolitique"]
    if score >= 0.7:
        return "Diversification ou relocalisation urgente"
    elif score >= 0.5:
        return "Renégociation & veille renforcée"
    else:
        return "Surveillance standard"

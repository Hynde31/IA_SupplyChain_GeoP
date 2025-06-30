def geopolitical_risk_score(row, zones_geo):
    """
    Calcule un score de risque géopolitique IA pour un fournisseur :
    - Score élevé si zone à risque critique/moyenne.
    - Sinon, pondère selon la dépendance stratégique (colonne 'Dépendance', 0 à 1).
    """
    zone = next((z for z in zones_geo if z["Pays"].lower() == str(row["Pays"]).lower()), None)
    if zone:
        criticite = zone.get("Criticité", "").lower()
        if criticite == "élevée":
            return 0.85
        elif criticite == "moyenne":
            return 0.65
    # Sinon, dépendance, ou 0.3 par défaut
    try:
        base = float(row.get("Dépendance", 0.3))
    except Exception:
        base = 0.3
    return min(base, 1.0)

def recommend_action(row, zones_geo):
    """
    Recommandation IA selon le score de risque géopolitique.
    """
    score = row["Score risque géopolitique"]
    if score >= 0.7:
        return "⚠️ Diversification ou relocalisation urgente"
    elif score >= 0.5:
        return "🟠 Renégociation & veille renforcée"
    else:
        return "🟢 Surveillance standard"

def geopolitical_risk_score(row, zones_geo):
    zone = next((z for z in zones_geo if z["Pays"].lower() == str(row["Pays"]).lower()), None)
    if zone:
        criticite = zone.get("Criticité", "").lower()
        if criticite == "élevée":
            return 0.85
        elif criticite == "moyenne":
            return 0.65
    try:
        base = float(row.get("Dépendance", 0.3))
    except Exception:
        base = 0.3
    return min(base, 1.0)

def recommend_action(row, zones_geo):
    score = row["Score risque géopolitique"]
    if score >= 0.7:
        return "Diversification ou relocalisation urgente"
    elif score >= 0.5:
        return "Renégociation & veille renforcée"
    else:
        return "Surveillance standard"

def geopolitical_risk_score(row, zones_geo):
    base_score = float(row.get("Score fournisseur", 0.3))  # Valeur par défaut si colonne manquante
    pays = row.get("Pays", "")
    for zone in zones_geo:
        if pays == zone["Nom"]:
            return min(1.0, base_score + zone.get("Impact", 0.5))
    return base_score

def recommend_actions(df):
    recs = []
    for _, row in df.iterrows():
        score = row.get("Score risque géopolitique", 0)
        fournisseur = row.get("Fournisseur", "Inconnu")
        pays = row.get("Pays", "Inconnu")
        if score >= 0.7:
            recs.append(f"⚠ Diversification recommandée : {fournisseur} ({pays}) - risque élevé.")
        elif score >= 0.5:
            recs.append(f"🔍 Surveillance accrue : {fournisseur} ({pays}) - risque modéré.")
        else:
            recs.append(f"✅ Pas d'action prioritaire : {fournisseur} ({pays}).")
    return recs

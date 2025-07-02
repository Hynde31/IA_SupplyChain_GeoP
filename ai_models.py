def geopolitical_risk_score(row, zones_geo):
    """
    Calcule un score de risque géopolitique pour un fournisseur donné,
    en fonction de sa localisation et des zones à risque définies.
    """
    base_score = float(row.get("Score fournisseur", 0.3))
    pays = row.get("Pays", "").strip()
    for zone in zones_geo:
        if pays.lower() == zone["Nom"].lower():
            return min(1.0, base_score + zone.get("Impact", 0.5))
    return base_score

def recommend_actions(df):
    """
    Génère des recommandations stratégiques en fonction du score de risque.
    """
    recs = []
    for _, row in df.iterrows():
        score = row.get("Score risque géopolitique", 0)
        fournisseur = row.get("Fournisseur", "Inconnu")
        pays = row.get("Pays", "Inconnu")
        cas = row.get("Cas géopolitique", "")
        if score >= 0.7:
            recs.append(
                f"⚠️ Diversification urgente : {fournisseur} ({pays}). Risque élevé. Cas : {cas}\n"
                f"Action recommandée : identifier des fournisseurs alternatifs, augmenter les stocks stratégiques."
            )
        elif score >= 0.5:
            recs.append(
                f"🔍 Surveillance renforcée : {fournisseur} ({pays}). Risque modéré. Cas : {cas}\n"
                f"Action : prévoir un plan de mitigation et revoir les contrats logistiques."
            )
        else:
            recs.append(
                f"✅ Pas d’action prioritaire : {fournisseur} ({pays})."
            )
    return recs

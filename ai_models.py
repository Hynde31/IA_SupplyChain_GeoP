def recommend_actions(df):
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

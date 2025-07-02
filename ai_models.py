def geopolitical_risk_score(row, zones_geo):
    base_score = float(row.get("Score fournisseur", 0.3))
    for zone in zones_geo:
        if row.get("Pays") == zone["Nom"]:
            return min(1.0, base_score + zone.get("Impact", 0.5))
    return base_score

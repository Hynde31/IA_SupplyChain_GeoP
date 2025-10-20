ID_colors = {
    "HEL": [57, 106, 177],
    "EBE": [218, 124, 48],
    "DWI": [62, 150, 81],
    "DEFAULT": [200, 200, 200],
}

cities_coords = {
    "Kyriat Gat": (31.6097, 34.7604),
    "Rousset": (43.4285, 5.5872),
    "Shizuoka": (34.9756, 138.3828),
    "Bensheim": (49.6803, 8.6195),
    "Haïfa": (32.7940, 34.9896),
    "Angers": (47.4784, -0.5632),
    "Shanghai": (31.2304, 121.4737),
    "Beersheba": (31.2518, 34.7913),
    "Kyoto": (35.0116, 135.7681),
    # Ajoute d'autres villes nécessaires
}

def generate_legend(ID_selected):
    lines = ["**Légende carte :**"]
    color_hex = lambda rgb: f"rgb({rgb[0]},{rgb[1]},{rgb[2]})"
    for ID in ID_selected:
        col = color_hex(ID_colors.get(ID, ID_colors["DEFAULT"]))
        lines.append(f'- <span style="color:{col};font-size:22px;">&#9679;</span> Fournisseur portefeuille <b>{ID}</b>')
    lines.append('- <span style="color:orange;font-size:22px;">&#9679;</span> <b>Zones à risque géopolitique</b>')
    lines.append('- <span style="color:red;font-size:22px;">&#9679;</span> <b>Zones de conflit</b>')
    return "\n".join(lines)

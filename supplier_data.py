import random

SUPPLIERS = [
    # MRP Code HEL : Cockpit, 4 fournisseurs
    {
        "name": "Thales Avionics",
        "component": "Cockpit",
        "criticality": "Critical",
        "dual_sourcing": False,
        "mrp_code": "HEL",
        "sites": [
            {"city": "Bordeaux", "country": "France", "lat": 44.8378, "lon": -0.5792,
             "stock_days": random.randint(7,25), "lead_time": random.randint(30,90),
             "on_time_delivery": random.randint(87,98), "incidents": random.randint(0,3)},
            {"city": "Tunis", "country": "Tunisie", "lat": 36.8065, "lon": 10.1815,
             "stock_days": random.randint(5,20), "lead_time": random.randint(40,120),
             "on_time_delivery": random.randint(75,95), "incidents": random.randint(0,5)}
        ]
    },
    {
        "name": "Collins Aerospace",
        "component": "Cockpit",
        "criticality": "Critical",
        "dual_sourcing": True,
        "mrp_code": "HEL",
        "sites": [
            {"city": "Charlotte", "country": "USA", "lat": 35.2271, "lon": -80.8431,
             "stock_days": random.randint(10,30), "lead_time": random.randint(45,100),
             "on_time_delivery": random.randint(80,97), "incidents": random.randint(0,4)}
        ]
    },
    {
        "name": "Diehl Aerospace",
        "component": "Cockpit",
        "criticality": "Medium",
        "dual_sourcing": True,
        "mrp_code": "HEL",
        "sites": [
            {"city": "Nuremberg", "country": "Allemagne", "lat": 49.4521, "lon": 11.0767,
             "stock_days": random.randint(8,28), "lead_time": random.randint(35,85),
             "on_time_delivery": random.randint(88,99), "incidents": random.randint(0,2)}
        ]
    },
    {
        "name": "Safran Electronics",
        "component": "Cockpit",
        "criticality": "Medium",
        "dual_sourcing": True,
        "mrp_code": "HEL",
        "sites": [
            {"city": "Eragny", "country": "France", "lat": 49.0258, "lon": 2.0916,
             "stock_days": random.randint(12,35), "lead_time": random.randint(25,70),
             "on_time_delivery": random.randint(85,97), "incidents": random.randint(0,2)}
        ]
    },

    # MRP Code EBE : Equipements, 5 fournisseurs
    {
        "name": "Zodiac Aerospace",
        "component": "Equipements",
        "criticality": "Critical",
        "dual_sourcing": False,
        "mrp_code": "EBE",
        "sites": [
            {"city": "Plaisir", "country": "France", "lat": 48.8164, "lon": 1.9502,
             "stock_days": random.randint(6,22), "lead_time": random.randint(30,85),
             "on_time_delivery": random.randint(83,97), "incidents": random.randint(0,3)}
        ]
    },
    {
        "name": "Honeywell",
        "component": "Equipements",
        "criticality": "Medium",
        "dual_sourcing": True,
        "mrp_code": "EBE",
        "sites": [
            {"city": "Phoenix", "country": "USA", "lat": 33.4484, "lon": -112.0740,
             "stock_days": random.randint(12,32), "lead_time": random.randint(55,120),
             "on_time_delivery": random.randint(78,96), "incidents": random.randint(1,4)}
        ]
    },
    {
        "name": "Eaton Industries",
        "component": "Equipements",
        "criticality": "Low",
        "dual_sourcing": True,
        "mrp_code": "EBE",
        "sites": [
            {"city": "Titchfield", "country": "UK", "lat": 50.8486, "lon": -1.2357,
             "stock_days": random.randint(14,40), "lead_time": random.randint(40,110),
             "on_time_delivery": random.randint(81,97), "incidents": random.randint(0,3)}
        ]
    },
    {
        "name": "FACC AG",
        "component": "Equipements",
        "criticality": "Low",
        "dual_sourcing": True,
        "mrp_code": "EBE",
        "sites": [
            {"city": "Ried", "country": "Autriche", "lat": 48.2100, "lon": 13.4880,
             "stock_days": random.randint(10,25), "lead_time": random.randint(50,130),
             "on_time_delivery": random.randint(79,97), "incidents": random.randint(0,2)}
        ]
    },
    {
        "name": "Stelia Aerospace",
        "component": "Equipements",
        "criticality": "Critical",
        "dual_sourcing": False,
        "mrp_code": "EBE",
        "sites": [
            {"city": "Rochefort", "country": "France", "lat": 45.9420, "lon": -0.9627,
             "stock_days": random.randint(7,30), "lead_time": random.randint(38,95),
             "on_time_delivery": random.randint(85,99), "incidents": random.randint(0,3)},
            {"city": "Tunis", "country": "Tunisie", "lat": 36.8065, "lon": 10.1815,
             "stock_days": random.randint(5,17), "lead_time": random.randint(40,90),
             "on_time_delivery": random.randint(77,94), "incidents": random.randint(0,4)}
        ]
    },

    # MRP Code DWI : Connectivités, Electronique, 6 fournisseurs
    {
        "name": "Rockwell Collins",
        "component": "Connectivités",
        "criticality": "Critical",
        "dual_sourcing": False,
        "mrp_code": "DWI",
        "sites": [
            {"city": "Cedar Rapids", "country": "USA", "lat": 42.0083, "lon": -91.6441,
             "stock_days": random.randint(8,20), "lead_time": random.randint(60,120),
             "on_time_delivery": random.randint(78,96), "incidents": random.randint(1,4)}
        ]
    },
    {
        "name": "Cobham",
        "component": "Electronique",
        "criticality": "Medium",
        "dual_sourcing": True,
        "mrp_code": "DWI",
        "sites": [
            {"city": "Dorset", "country": "UK", "lat": 50.7488, "lon": -2.3445,
             "stock_days": random.randint(15,38), "lead_time": random.randint(50,105),
             "on_time_delivery": random.randint(80,98), "incidents": random.randint(0,3)}
        ]
    },
    {
        "name": "TE Connectivity",
        "component": "Connectivités",
        "criticality": "Low",
        "dual_sourcing": True,
        "mrp_code": "DWI",
        "sites": [
            {"city": "Schaffhausen", "country": "Suisse", "lat": 47.6967, "lon": 8.6340,
             "stock_days": random.randint(18,35), "lead_time": random.randint(35,100),
             "on_time_delivery": random.randint(83,99), "incidents": random.randint(0,2)}
        ]
    },
    {
        "name": "Radiall",
        "component": "Connectivités",
        "criticality": "Medium",
        "dual_sourcing": True,
        "mrp_code": "DWI",
        "sites": [
            {"city": "Voreppe", "country": "France", "lat": 45.3287, "lon": 5.6077,
             "stock_days": random.randint(11,29), "lead_time": random.randint(40,110),
             "on_time_delivery": random.randint(82,98), "incidents": random.randint(0,2)}
        ]
    },
    {
        "name": "Amphenol",
        "component": "Electronique",
        "criticality": "Critical",
        "dual_sourcing": False,
        "mrp_code": "DWI",
        "sites": [
            {"city": "Wallingford", "country": "USA", "lat": 41.4570, "lon": -72.8250,
             "stock_days": random.randint(10,32), "lead_time": random.randint(50,115),
             "on_time_delivery": random.randint(79,97), "incidents": random.randint(1,4)}
        ]
    },
    {
        "name": "Liebherr Aerospace",
        "component": "Electronique",
        "criticality": "Medium",
        "dual_sourcing": True,
        "mrp_code": "DWI",
        "sites": [
            {"city": "Toulouse", "country": "France", "lat": 43.6047, "lon": 1.4442,
             "stock_days": random.randint(15,40), "lead_time": random.randint(28,90),
             "on_time_delivery": random.randint(85,99), "incidents": random.randint(0,2)},
            {"city": "Lindenberg", "country": "Allemagne", "lat": 47.6014, "lon": 9.8862,
             "stock_days": random.randint(12,33), "lead_time": random.randint(35,80),
             "on_time_delivery": random.randint(82,98), "incidents": random.randint(0,2)}
        ]
    },
]

MRP_CODES = ["HEL", "EBE", "DWI"]
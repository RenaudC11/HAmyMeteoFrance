from __future__ import annotations

DOMAIN = "mameteo"

# Config keys
CONF_API_KEY = "api_key"
CONF_STATION_ID = "station_id"
CONF_ENTITY_NAME = "entity_name"
CONF_MODE = "mode"
CONF_UPDATE_MINUTES = "update_minutes"

# Defaults
DEFAULT_ENTITY_NAME = "MaMeteo"
DEFAULT_STATION_ID = "69029001"   # Lyon-Bron
DEFAULT_UPDATE_MINUTES = 6        # 6 min

# Modes
MODE_SINGLE = "single"   # 1 sensor (température) + attributs
MODE_SPLIT  = "split"    # 1 sensor par mesure

# --------------------------
#  MAPPINGS DES MESURES
# --------------------------
# NOTE: Les unités ci-dessous sont les unités **après conversion**
# - Températures: Kelvin -> °C
# - Vent: m/s -> km/h
# - Pression: Pa -> hPa
# - Rayonnement global (ray_glo01): J/m² sur 6 min -> ~ W/m² (÷ 360)
# - Précipitations: mm (inchangées)
# - Visibilité: m (inchangé)
# - Ensoleillement (insolh): min (inchangé)
# - Directions: ° (inchangé)
#
# device_class valides (exemples courants):
# "temperature", "humidity", "pressure", "wind_speed", "irradiance",
# "distance", "precipitation"
#
# state_class (pour stats):
# "measurement" (instantané), "total_increasing" (compteur cumulatif)
#
# Toutes les clés gérées :
# t, t_10, t_20, t_50, t_100, tx, tn,
# u, ux, un,
# ff, fxi, fxy, dd, dxi, dxy,
# vv,
# rr_per, rr1, rr, rr24,
# ray_glo01, insolh,
# pres, pmer,
# etat_sol, sss, n
SENSOR_SPECS: dict[str, dict] = {
    # Températures (K -> °C)
    "t":      {"name": "température sous abri", "unit": "°C",  "device_class": "temperature", "state_class": "measurement"},
    "td":     {"name": "Température de rosée",  "unit": "°C",  "device_class": "temperature", "state_class": "measurement"},
    "t_10":   {"name": "température à 10 centimètres de profondeur sous le sol",    "unit": "°C",  "device_class": "temperature", "state_class": "measurement"},
    "t_20":   {"name": "température à 20 centimètres de profondeur sous le sol",    "unit": "°C",  "device_class": "temperature", "state_class": "measurement"},
    "t_50":   {"name": "température à 50 centimètres de profondeur sous le sol",    "unit": "°C",  "device_class": "temperature", "state_class": "measurement"},
    "t_100":  {"name": "température à 100 centimètres de profondeur sous le sol",   "unit": "°C",  "device_class": "temperature", "state_class": "measurement"},
    "tx":     {"name": "température maximale de l'air à 2 mètres au-dessus du sol",       "unit": "°C",  "device_class": "temperature", "state_class": "measurement"},
    "tn":     {"name": "température minimale de l'air à 2 mètres au-dessus du sol",       "unit": "°C",  "device_class": "temperature", "state_class": "measurement"},

    # Humidité (%)
    "u":      {"name": "Humidité relative horaire",               "unit": "%",   "device_class": "humidity",    "state_class": "measurement"},
    "ux":     {"name": "Humidité relative maximale dans l’heure", "unit": "%",   "device_class": "humidity",    "state_class": "measurement"},
    "un":     {"name": "humidité relative minimale dans l’heure", "unit": "%",   "device_class": "humidity",    "state_class": "measurement"},

    # Vent (m/s -> km/h) et directions (°)
    "ff":     {"name": "Force du vent moyen à 10 mètres au-dessus du sol",                 "unit": "m/s","device_class": "wind_speed",  "state_class": "measurement"},
    "fxi":    {"name": "Force maximale du vent instantané sur 10 mn",                      "unit": "m/s","device_class": "wind_speed",  "state_class": "measurement"},
    "fxy":    {"name": "force maximale du vent dans l’heure à 10 mètres au-dessus du sol", "unit": "m/s","device_class": "wind_speed",  "state_class": "measurement"},
    "dd":     {"name": "Direction vent max à 10 mètres au-dessus du sol",                  "unit": "°",   "device_class": None,          "state_class": "measurement"},
    "dxi":    {"name": "Direction vent max instantané sur 10 mn",                          "unit": "°",  "device_class": None,          "state_class": "measurement"},
    "dxy":    {"name": "Direction vent max dans l’heure à 10 mètres au-dessus du sol",     "unit": "°",   "device_class": None,          "state_class": "measurement"},

    # Visibilité
    "vv":     {"name": "Visibilité horizontale",            "unit": "m",   "device_class": "distance",    "state_class": "measurement"},

    # Précipitations (mm)
    "rr_per": {"name": "Précipitations sur 6 min",    "unit": "mm",  "device_class": "precipitation","state_class": "measurement"},
    "rr1":    {"name": "Précipitations dans l'heure",                   "unit": "mm",  "device_class": "precipitation","state_class": "measurement"},
    "rr":     {"name": "Précipitations cumulées sur un mois", "unit": "mm",  "device_class": "precipitation","state_class": "measurement"},
    "rr24":   {"name": "Précipitations sur 24h",                  "unit": "mm",  "device_class": "precipitation","state_class": "measurement"},

    # Rayonnement / Ensoleillement
    "ray_glo01":  {"name": "Rayonnement global sur la période",       "unit": "W/m²","device_class": "irradiance",  "state_class": "measurement"},
    "insolh":     {"name": "durée insolation au cours de la période", "unit": "min", "device_class": None,          "state_class": "measurement"},

    # Pression (Pa -> hPa)
    "pres":   {"name": "Pression station",      "unit": "hPa", "device_class": "pressure",    "state_class": "measurement"},
    "pmer":   {"name": "Pression mer",          "unit": "hPa", "device_class": "pressure",    "state_class": "measurement"},

    # Divers
    "etat_sol": {"name": "Code de l'état du sol",                    "unit": None,  "device_class": None,          "state_class": None},
    "sss":      {"name": "hauteur totale de la couverture neigeuse", "unit": "m",  "device_class": None,          "state_class": "measurement"},
    "n":        {"name": "nébulosité totale",                        "unit": "octas",   "device_class": None,          "state_class": "measurement"},
}

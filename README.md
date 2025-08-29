# HAmyMeteoFrance

**Version : 1.8.0**\
Custom component Home Assistant pour récupérer les observations temps
réel de Météo-France (API publique).

## 🚀 Fonctionnalités

-   Récupération des données d'observation d'une station Météo-France
    (par défaut : 69029001 Lyon-Bron).
-   Deux modes d'installation :
    1.  **Mode unique** : une seule entité `sensor.nom_personnalisé`
        avec toutes les valeurs en attributs.
        -   La valeur principale correspond à la température instantanée
            (`t`).
    2.  **Mode multiple** : création d'un capteur distinct pour chaque
        mesure (`temperature`, `vent`, `pluie`, etc.).
-   Configuration simplifiée via l'UI (config_flow).

## 🔑 Paramètres demandés lors de l'installation

-   **Clé API** (fourni par Météo-France -- portail développeur).\
-   **Numéro de station** (par défaut : `69029001` -- Lyon Bron).\
-   **Nom de l'entité** (libre).\
-   **Mode de création** (unique ou multiple).

## 📊 Données disponibles

  --------------------------------------------------------------------------------
  Code API      Description             Unité     `device_class`   `state_class`
  ------------- ----------------------- --------- ---------------- ---------------
  `t`           Température instantanée °C        temperature      measurement

  `tx`          Température max         °C        temperature      measurement

  `tn`          Température min         °C        temperature      measurement

  `u`           Humidité relative       \%        humidity         measurement

  `ux`          Humidité max            \%        humidity         measurement

  `un`          Humidité min            \%        humidity         measurement

  `ff`          Vent moyen              km/h      wind_speed       measurement

  `d`           Direction vent moyen    °         wind_direction   measurement

  `fx`          Rafale max              km/h      wind_speed       measurement

  `dxy`         Direction rafale max    °         wind_direction   measurement

  `fxy`         Vitesse rafale max      km/h      wind_speed       measurement

  `dxi`         Direction vent          °         wind_direction   measurement
                instantané                                         

  `fxi`         Vitesse vent instantané km/h      wind_speed       measurement

  `rr1`         Pluie 1h                mm        precipitation    measurement

  `rr3`         Pluie 3h                mm        precipitation    measurement

  `rr6`         Pluie 6h                mm        precipitation    measurement

  `rr24`        Pluie 24h               mm        precipitation    measurement

  `t_50`        Température sous abri   °C        temperature      measurement
                50cm                                               

  `etat_sol`    État du sol             code      none             none

  `sss`         Hauteur de neige        cm        none             measurement

  `n`           Nébulosité totale       \%        none             measurement

  `ray_glo01`   Rayonnement global      W/m²      irradiance       measurement

  `pres`        Pression station        hPa       pressure         measurement

  `pmer`        Pression réduite au     hPa       pressure         measurement
                niveau mer                                         
  --------------------------------------------------------------------------------

## ⚙️ Installation

1.  Copier le dossier `custom_components/mameteo` dans
    `config/custom_components/` de votre Home Assistant.
2.  Redémarrer Home Assistant.
3.  Ajouter l'intégration **Ma Météo France Obs** via **Paramètres →
    Appareils et Services → Ajouter une intégration**.

## 📝 Notes

-   Les valeurs `null` dans l'API sont ignorées.\
-   L'API Météo-France impose des limitations de requêtes (veillez à ne
    pas dépasser).\
-   Le composant est compatible avec `recorder`, `statistics` et
    `energy dashboard`.

## 👤 Auteur

Développé par [RenaudC11](https://github.com/RenaudC11/HAmyMeteoFrance)

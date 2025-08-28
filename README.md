# HAmyMeteoFrance

Une intégration **Home Assistant** permettant de récupérer toutes les
données disponibles depuis l'API publique de **Météo-France (données
SYNOP)**.\
Les informations sont exposées sous forme d'un **capteur unique** avec
de nombreux attributs détaillés.

------------------------------------------------------------------------

## 🚀 Installation

### Via HACS (recommandé)

1.  Ouvrir **HACS** dans Home Assistant.
2.  Aller dans **Intégrations** → **3 points en haut à droite** →
    **Dépôts personnalisés**.
3.  Ajouter ce dépôt GitHub avec la catégorie **Intégration**.
4.  Rechercher `HAmyMeteoFrance` dans HACS et l'installer.
5.  Redémarrer Home Assistant.

### Manuel (si pas de HACS)

1.  Copier le dossier `mameteo` dans :

        config/custom_components/mameteo/

2.  Redémarrer Home Assistant.

------------------------------------------------------------------------

## ⚙️ Configuration

L'intégration se configure directement via l'interface graphique :\
1. Aller dans **Paramètres** → **Appareils et services** → **Ajouter une
intégration**. 2. Rechercher **MaMeteo**. 3. Saisir :\
- **Nom de l'entité** (ex. `Météo Lyon` → donnera `sensor.meteo_lyon`)\
- **Latitude & Longitude** (de la station météo la plus proche).\
- **Fréquence de mise à jour** (en minutes).

Un capteur principal est créé :

    sensor.<nom_entite>

------------------------------------------------------------------------

## 📊 Données disponibles

Toutes les valeurs sont exposées comme attributs du capteur.

  ----------------------------------------------------------------------------
  Attribut             Description           Unité       Commentaire
  -------------------- --------------------- ----------- ---------------------
  `temperature`        Température de l'air  °C          Mesure instantanée

  `humidity`           Humidité relative     \%          0--100 %

  `pressure`           Pression              hPa         Niveau mer
                       atmosphérique                     

  `wind_speed`         Vitesse moyenne du    m/s         Mesurée sur 10
                       vent                              minutes

  `wind_direction`     Direction du vent     °           Azimut (0° = Nord)

  `gust`               Rafales de vent       m/s         Sur 10 minutes
                       maximales                         

  `rain_1h`            Précipitations        mm          
                       cumulées sur 1h                   

  `rain_24h`           Précipitations        mm          
                       cumulées sur 24h                  

  `cloud_cover`        Nébulosité totale     \%          Ciel couvert

  `visibility`         Visibilité            m           
                       horizontale                       

  `dew_point`          Point de rosée        °C          Calculé à partir T°
                                                         et humidité

  `snow_depth`         Hauteur de neige au   cm          Si dispo
                       sol                               

  `solar_radiation`    Rayonnement global    W/m²        Si dispo

  `observation_time`   Heure de la dernière  ISO 8601    UTC
                       mesure                            
  ----------------------------------------------------------------------------

⚠️ Les données disponibles dépendent de la station météo choisie (toutes
ne publient pas tous les attributs).

------------------------------------------------------------------------

## 🔄 Fréquence de mise à jour

-   Définie par l'utilisateur lors de la configuration (ex. toutes les
    10 minutes).\
-   Peut être modifiée en supprimant/recréant l'intégration.

------------------------------------------------------------------------

## 🖼 Exemple dans Lovelace

``` yaml
type: entities
title: Météo France
entities:
  - entity: sensor.meteo_lyon
    name: Météo Lyon
```

⚡ Tous les attributs peuvent être affichés via une carte **entities**,
**glance** ou intégrés dans **des graphiques** (Lovelace charts).

------------------------------------------------------------------------

## 📌 Notes

-   Cette intégration utilise les données publiques **Météo-France
    SYNOP**.\
-   Certains attributs peuvent être absents selon la station ou la
    disponibilité de l'API.\
-   Compatible avec **Home Assistant Green** et toute installation HA
    avec HACS.

------------------------------------------------------------------------

## 📄 Licence

MIT

# Prompt pour Agent IA - Projet Data Warehouse INSEA

## Contexte du Projet
Je travaille sur un projet de Data Warehouse pour analyser les avis clients des agences bancaires au Maroc via Google Maps. Tu vas m'aider à implémenter ce projet étape par étape en suivant une architecture moderne de données.

## Objectif Principal
Créer un pipeline de données complet pour collecter, traiter et analyser les avis Google Maps des agences bancaires marocaines, avec analyse de sentiment et modélisation de sujets.

## Stack Technique Requis
- **Collecte de données** : Python, Google Maps API, BeautifulSoup/Scrapy
- **Orchestration** : Apache Airflow
- **Stockage** : PostgreSQL (Data Warehouse)
- **Transformation** : DBT (Data Build Tool)
- **Visualisation** : Looker Studio
- **Contrôle de version** : GitHub

## Architecture Cible
```
Google Maps → Python Scraper → Airflow → PostgreSQL → DBT → Looker Studio
```

## Phases du Projet

### Phase 1: Collecte de Données
**Objectif** : Scraper les avis Google Maps des agences bancaires marocaines
**Livrables** :
- Script Python pour extraction via Google Maps API ou web scraping
- DAG Airflow pour automatisation quotidienne/hebdomadaire
- Stockage des données brutes en PostgreSQL

**Données à extraire** :
- Nom de la banque
- Nom de l'agence
- Localisation
- Texte de l'avis
- Note (rating)
- Date de l'avis

### Phase 2: Nettoyage et Transformation
**Objectif** : Nettoyer et enrichir les données
**Livrables** :
- Modèles DBT pour le nettoyage
- Analyse de sentiment (Positif/Négatif/Neutre)
- Extraction de sujets via NLP (LDA)
- Détection de langue

**Transformations requises** :
- Suppression des doublons
- Normalisation du texte
- Gestion des valeurs manquantes
- Classification par sentiment
- Extraction de topics

### Phase 3: Modélisation de Données
**Objectif** : Créer un schéma en étoile dans PostgreSQL
**Structure** :
- **Table de faits** : `fact_reviews`
- **Tables de dimensions** :
  - `dim_bank`
  - `dim_branch`
  - `dim_location`
  - `dim_sentiment`

### Phase 4: Analytics et Reporting
**Objectif** : Créer des dashboards dans Looker Studio
**Visualisations** :
- Tendances de sentiment par banque/agence
- Topics positifs et négatifs principaux
- Classement des agences par performance
- Métriques d'expérience client

### Phase 5: Déploiement et Automatisation
**Objectif** : Automatiser le pipeline complet
**Fonctionnalités** :
- Mise à jour automatique via Airflow
- Alertes en cas d'échec
- Monitoring du pipeline

## Instructions pour l'Agent IA

### Approche de Travail
1. **Commence toujours par me demander sur quelle phase nous travaillons**
2. **Propose une architecture détaillée avant de coder**
3. **Écris du code modulaire et bien documenté**
4. **Inclus la gestion d'erreurs et le logging**
5. **Respecte les bonnes pratiques de chaque outil**

### Format de Réponse Attendu
Pour chaque tâche :
1. **Explication de l'approche** (2-3 phrases)
2. **Code complet avec commentaires**
3. **Instructions de configuration/installation**
4. **Tests ou validation suggérés**
5. **Prochaines étapes recommandées**

### Considérations Spécifiques

#### Pour le Scraping
- Respecter les limites de taux de Google Maps
- Gérer les erreurs de connexion
- Implémenter un système de retry
- Sauvegarder les données progressivement

#### Pour Airflow
- Créer des DAGs modulaires
- Implémenter le monitoring
- Gérer les dépendances entre tâches
- Configurer les alertes

#### Pour DBT
- Créer des modèles testables
- Documenter les transformations
- Implémenter les tests de qualité
- Organiser les modèles par couches (staging, intermediate, marts)

#### Pour PostgreSQL
- Optimiser les index
- Partitionner les grandes tables si nécessaire
- Implémenter les contraintes d'intégrité
- Documenter le schéma

### Banques Cibles au Maroc
Focus sur les principales banques :
- Attijariwafa Bank
- Banque Populaire
- BMCE Bank
- Crédit Agricole du Maroc
- Banque Centrale Populaire
- CIH Bank
- Crédit du Maroc

### Questions à Me Poser
Quand tu as besoin de clarifications, pose-moi des questions sur :
- Les spécificités techniques souhaitées
- Les priorités entre les phases
- Les contraintes de performance
- Les détails de configuration

### Livrables Finaux Attendus
1. Scripts Python de collecte
2. DAGs Airflow
3. Modèles DBT
4. Schéma PostgreSQL
5. Dashboard Looker Studio
6. Documentation complète

## Première Action
**Commence par me dire sur quelle phase tu veux qu'on travaille en premier, et propose-moi une architecture détaillée pour cette phase avec les technologies spécifiques à utiliser.**

---

*Note : Ce projet suit une approche moderne de Data Engineering. N'hésite pas à suggérer des améliorations ou des alternatives si tu vois des optimisations possibles.*
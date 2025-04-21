# Real-Time Financial Data Streaming Pipeline using Kafka, Spark, Cassandra, and Grafana

## Contexte du Projet

Le projet consiste à surveiller et analyser en temps réel les données financières des marchés boursiers pour fournir des insights actionnables. En ingérant, traitant et visualisant les flux de données provenant de sources comme Finnhub, le projet permet de détecter des tendances, anticiper les fluctuations des prix, et offrir une visibilité quasi instantanée sur les mouvements des actifs financiers. Les outils modernes comme Kafka, Spark, Cassandra, et Grafana sont utilisés pour transformer les données brutes en tableaux de bord interactifs, facilitant ainsi la prise de décision pour les traders et analystes financiers.

## Objectifs

Le pipeline de données en temps réel a pour objectifs :
- Récupérer des symboles financiers via websocket Finnhub
- Consommer des données via Kafka
- Traiter les flux de données avec Spark Structured Streaming
- Stocker les données traitées dans Cassandra
- Visualiser les données en temps réel avec Grafana

## Étapes de Mise en Œuvre

### 1. **Data Source:**

- **Objectif** : Obtenir une liste exhaustive des symboles financiers pris en charge par Finnhub.
- **Détails** : Inclure des informations comme le symbole, le nom, le marché, la devise et le statut. Utiliser websocket pour récupérer les flux de données en temps réel.

### 2. **Data Ingestion:**

- **Objectif** : Consommer les données websocket et les envoyer vers Kafka.
- **Détails** : Implémenter un Producer Kafka pour se connecter à Finnhub, récupérer les données financières en temps réel et publier les messages vers un broker Kafka.

### 3. **Message Broker:**

- **Objectif** : Utiliser Kafka comme tampon de messages pour découpler l'ingestion et le traitement des données.
- **Détails** : Kafka stocke les données de manière distribuée et les distribue aux consommateurs. Zookeeper gère et coordonne le cluster Kafka.
- **Script** : Développer un script shell (`kafka-setup-k8s.sh`) pour initialiser les topics Kafka lors de l'initialisation des conteneurs dans Kubernetes.

### 4. **Stream Processing:**

- **Objectif** : Transformer les données en temps réel avec Spark Structured Streaming.
- **Détails** : Consommer les données depuis Kafka, les transformer et effectuer des calculs/agrégations en temps réel. Les résultats seront envoyés vers la base de données pour un stockage ultérieur.
- **Requêtes principales** :
  - **Transformation des Données Brutes** : Convertir les données brutes en un format structuré et exploitable.
  - **Agrégations Temporelles** : Calculer des moyennes mobiles, sommes cumulées, etc., toutes les 5 secondes pour des mises à jour en temps réel.

### 5. **Stockage des Données:**

- **Objectif** : Stocker les données traitées pour une consultation rapide et fiable.
- **Détails** : Après transformation et agrégation, les données sont stockées dans Cassandra. Le schéma de Cassandra est défini dans `cassandra-setup.cql` pour créer les keyspaces et tables nécessaires.
- **Déploiement** : Déployer Cassandra comme service dans Kubernetes, en s'assurant que le script `cassandra-setup.cql` initialise la base de données au démarrage.

### 6. **Visualization:**

- **Objectif** : Afficher les données agrégées en temps réel.
- **Détails** : Utiliser Grafana pour interroger et visualiser les données stockées dans Cassandra. Le plugin `HadesArchitect-Cassandra` est utilisé pour connecter Grafana à Cassandra.
- **Configuration** : Créer des dashboards Grafana pour afficher les indicateurs clés en temps réel.

### 7. **Orchestration & Infrastructure:**

- **Objectif** : Automatiser le déploiement et gérer les ressources tout en garantissant l’interopérabilité des composants.
- **Détails** : Kubernetes est utilisé pour déployer les services sous forme de pods, services et statefulsets. Terraform est utilisé pour provisionner les clusters Kubernetes et gérer le stockage et le réseau.

---

## Architecture du Projet

L'architecture du projet repose sur une infrastructure distribuée avec les technologies suivantes :
- **Kafka** pour le message broker
- **Spark Structured Streaming** pour le traitement en temps réel
- **Cassandra** pour le stockage des données
- **Grafana** pour la visualisation en temps réel
- **Kubernetes** pour l'orchestration des services

## Prérequis

Avant de commencer, assurez-vous que les composants suivants sont installés et configurés :
- Kafka
- Zookeeper
- Spark
- Cassandra
- Grafana
- Kubernetes et Terraform pour l'orchestration et la gestion des clusters

## Installation et Configuration

1. **Initialisation de Kafka et Zookeeper** :
   - Utilisez `kafka-setup-k8s.sh` pour configurer les topics Kafka dans Kubernetes.
   
2. **Déploiement de Cassandra** :
   - Déployez Cassandra en tant que service Kubernetes et exécutez `cassandra-setup.cql` pour créer le schéma de la base de données.

3. **Configuration de Grafana** :
   - Installez et configurez Grafana avec le plugin `HadesArchitect-Cassandra` pour se connecter à Cassandra.
   - Créez des dashboards pour visualiser les données financières en temps réel.

4. **Déploiement de Spark** :
   - Configurez Spark pour consommer les données depuis Kafka, effectuer les transformations et agrégations, puis les stocker dans Cassandra.

---

## Auteurs

- **Nom de l'Auteur** : Mohamed Abelchaguer
- **Organisation** : FinTech Solutions

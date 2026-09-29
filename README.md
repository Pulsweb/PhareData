<p align="center">
  <a href="https://www.pharedata.fr/">
    <img src="assets/phare-data-logo.png" alt="Logo Phare Data" width="160">
  </a>
</p>

<h1 align="center">Phare Data</h1>

<p align="center">
  <strong>La chaîne qui éclaire vos données.</strong><br>
  Les notebooks, scripts et ressources techniques présentés dans les épisodes de Phare Data, la chaîne communautaire francophone Data &amp; IA.
</p>

<p align="center">
  <a href="https://www.pharedata.fr/">Site web</a> ·
  <a href="https://www.youtube.com/@pharedata">YouTube</a> ·
  <a href="https://www.linkedin.com/company/111283551/">LinkedIn</a> ·
  <a href="https://www.pharedata.fr/articles">Articles</a> ·
  <a href="https://www.pharedata.fr/lexique">Lexique</a>
</p>

---

## À propos de Phare Data

Phare Data est une chaîne YouTube communautaire, en français, consacrée à la Data et à l'IA : Microsoft Fabric, Power BI, Databricks, Snowflake, Lakehouse, Data Warehouse, Data Mesh, gouvernance, FinOps, temps réel, IA générative et ontologies.

Le principe tient en trois mots : **des experts, des échanges, du concret.** Chaque épisode donne la parole à des praticiens qui partagent des projets réels, écrans à l'appui : chiffres, limites, incidents, réussites et compromis. Le but n'est pas de désigner une technologie gagnante, mais de comprendre dans quel contexte chaque choix devient le bon.

La chaîne s'adresse aux architectes, administrateurs Fabric, développeurs Power BI et responsables de plateformes Data qui préfèrent le retour d'expérience à la théorie. Un nouvel épisode est publié toutes les deux semaines.

Les épisodes sont organisés en six thèmes : [Microsoft Fabric](https://www.pharedata.fr/sujets/microsoft-fabric), [Power BI](https://www.pharedata.fr/sujets/power-bi), [FinOps Data](https://www.pharedata.fr/sujets/finops-data), [Gouvernance](https://www.pharedata.fr/sujets/gouvernance), [IA & Copilot](https://www.pharedata.fr/sujets/ia-copilot) et [Architecture Data](https://www.pharedata.fr/sujets/architecture-data).

## Ce que contient ce dépôt

Ce dépôt regroupe le code présenté pendant les épisodes, pour reproduire les démonstrations et les adapter à votre propre environnement. Chaque ressource est rattachée à l'épisode qui en explique le contexte, les choix et les limites.

| Épisode | Ressource | Type |
| --- | --- | --- |
| [Microsoft Fabric et Power BI : peut-on migrer une capacité vers une autre région Azure ?](https://www.pharedata.fr/videos/microsoft-fabric-et-power-bi-peut-on-migrer-une-capacite-vers-une-autre) | [`CrossRegionMigration-Assessment.ipynb`](CrossRegionMigration-Assessment.ipynb) | Notebook Fabric |
| | [`CrossRegionMigration-Migration.ipynb`](CrossRegionMigration-Migration.ipynb) | Notebook Fabric |
| [Votre modèle sémantique tiendra-t-il la charge ?](https://www.pharedata.fr/videos/votre-modele-semantique-tiendra-t-il-la-charge) | [`Load Test - MDX Format.py`](Load%20Test%20-%20MDX%20Format.py) | Script Python |

### Migration cross-région d'une capacité Microsoft Fabric / Power BI

▶️ [Voir l'épisode sur YouTube](https://www.youtube.com/watch?v=Vwgdz8OpZq8)

Il n'existe pas de bouton « déplacer ma capacité » : avant de migrer, il faut inventorier les objets et identifier ce qui peut être déplacé, recréé ou reconfiguré. Les deux notebooks s'appuient sur Semantic Link et [Semantic Link Labs](https://github.com/microsoft/semantic-link-labs).

- **[`CrossRegionMigration-Assessment.ipynb`](CrossRegionMigration-Assessment.ipynb)** : inventorie les capacités, workspaces et items du tenant, enregistre le résultat dans un Lakehouse (`lh_assessment`), puis crée un modèle sémantique (`sm_assessment`) et un rapport (`rep_assessment`) pour analyser le périmètre.
- **[`CrossRegionMigration-Migration.ipynb`](CrossRegionMigration-Migration.ipynb)** : réassigne tout ou partie des workspaces d'une capacité source vers une capacité cible, avec un traitement spécifique pour les modèles sémantiques au format de stockage *Large* :
  - **jusqu'à 10 Go** : passage temporaire au format *Small*, bascule du workspace, retour au format *Large*, puis actualisation ;
  - **au-delà de 10 Go** : sauvegarde `.abf`, purge des données (`clearValues`), bascule du workspace, puis restauration.

**Prérequis**

- Droits d'administrateur du tenant, pour lister l'ensemble des capacités, workspaces et items.
- Endpoint XMLA en lecture/écriture activé sur la capacité.
- Pour la sauvegarde et la restauration `.abf`, un compte de stockage ADLS Gen2 associé au workspace (voir [Sauvegarde et restauration des modèles sémantiques](https://learn.microsoft.com/en-us/fabric/enterprise/powerbi/service-premium-backup-restore-dataset) sur Microsoft Learn).

> [!IMPORTANT]
> Les identifiants de capacités, de workspaces et de modèles présents dans les notebooks proviennent de l'environnement de démonstration. Remplacez-les par les vôtres et validez la procédure sur un périmètre restreint avant toute migration.

### Test de charge d'un modèle sémantique Power BI

▶️ [Voir l'épisode sur YouTube](https://www.youtube.com/watch?v=1Ekpfl7S9F4)

Un modèle rapide avec un seul utilisateur peut atteindre ses limites lorsque des dizaines d'utilisateurs l'interrogent en même temps. L'épisode montre comment simuler cette charge avec des requêtes DAX et MDX, y compris celles générées par Excel et ses tableaux croisés dynamiques, et quelles métriques suivre : requêtes par seconde, consommation CPU et throttling de la capacité Fabric.

- **[`Load Test - MDX Format.py`](Load%20Test%20-%20MDX%20Format.py)** : convertit un export de requêtes MDX (`excel_mdx_queries.json`, champ `Query`) en un fichier `excel_mdx_queries_converted.json` au format `[{"query": "..."}]`, pour intégrer les requêtes Excel à un scénario de test de charge.

**Outils cités dans l'épisode**

- [Fabric Load Test Tool](https://github.com/microsoft/fabric-toolbox/tree/main/tools/FabricLoadTestTool) (microsoft/fabric-toolbox)
- [FabricDaxLoadTest](https://github.com/dbrownems/FabricDaxLoadTest)

## Utiliser les ressources

1. **Regardez l'épisode associé** : il explique le contexte, les hypothèses et les limites de chaque démonstration.
2. **Importez les notebooks** `.ipynb` dans un workspace Microsoft Fabric et exécutez-les dans un notebook PySpark. Le script Python s'exécute localement ou dans un notebook.
3. **Adaptez les paramètres** (identifiants, noms d'objets, chemins de fichiers) à votre environnement avant toute exécution.

## L'écosystème Phare Data

| Destination | Ce que vous y trouverez |
| --- | --- |
| [pharedata.fr](https://www.pharedata.fr/) | Le site de la chaîne : [vidéos](https://www.pharedata.fr/videos), [playlists](https://www.pharedata.fr/playlists), [invités](https://www.pharedata.fr/invites), [sujets](https://www.pharedata.fr/sujets) et recherche |
| [YouTube @pharedata](https://www.youtube.com/@pharedata) | L'ensemble des épisodes |
| [Articles](https://www.pharedata.fr/articles) | L'essentiel de chaque vidéo dans un format plus facile à lire |
| [Lexique](https://www.pharedata.fr/lexique) | Les notions abordées dans les épisodes |
| [LinkedIn](https://www.linkedin.com/company/111283551/) | L'actualité de la chaîne et des prochains épisodes |
| [Flux RSS](https://www.pharedata.fr/rss.xml) | Les nouvelles publications du site |
| [Blog Pulsweb](https://www.pulsweb.fr/) | Le blog de Romain Casteres, créateur de Phare Data |
| [GitHub Pulsweb](https://github.com/pulsweb) | Les autres projets open source de Pulsweb |

## Participer

Phare Data est une chaîne ouverte. Vous pouvez suggérer un sujet ou proposer de venir partager votre expérience lors d'un futur épisode via [LinkedIn](https://www.linkedin.com/company/111283551/) ou [YouTube](https://www.youtube.com/@pharedata).

Sur ce dépôt :

- signalez un bug ou suggérez une amélioration en ouvrant une [issue](https://github.com/Pulsweb/PhareData/issues) ;
- proposez une correction ou une adaptation d'un script via une pull request.

## Licence

Le code de ce dépôt est distribué sous licence MIT (voir [LICENSE](LICENSE)).
Les contenus publiés sur [pharedata.fr](https://www.pharedata.fr/) sont sous licence [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/deed.fr).

<sub>Les opinions exprimées dans les épisodes sont personnelles et ne représentent pas la position des employeurs des intervenants.</sub>

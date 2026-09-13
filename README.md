# pharedata

La chaîne qui éclaire vos données.

Ce dépôt regroupe l'ensemble des scripts, présentations et ressources nécessaires à
la préparation, l'enregistrement et la publication des épisodes de la chaîne YouTube
**Phare Data**.

## Organisation du dépôt

| Dossier | Contenu |
| --- | --- |
| `episodes/` | Un sous-dossier par épisode : script, checklist de production et notes |
| `scripts/` | Code des démonstrations : notebooks, requêtes SQL, scripts Python ou R |
| `presentations/` | Supports visuels affichés à l'écran : diaporamas, schémas, exports PDF |
| `ressources/` | Éléments réutilisables : jeux de données légers, visuels de la chaîne, sources |
| `modeles/` | Gabarits à copier au démarrage de chaque épisode |

Chaque dossier contient un `README.md` précisant ses conventions.

## Convention de nommage

Les épisodes sont identifiés par `EP000-titre-court`, où `000` est le numéro de
l'épisode et `titre-court` un intitulé en minuscules séparé par des tirets
(par exemple `EP012-jointures-sql`). Le même identifiant est réutilisé dans
`episodes/`, `scripts/` et `presentations/` afin de relier les éléments d'un
même épisode.

## Workflow d'un épisode

1. **Préparation** — créer `episodes/EP000-titre-court/`, y copier
   `modeles/script-episode.md` sous le nom `script.md` et
   `modeles/checklist-publication.md` sous le nom `checklist.md`, puis rédiger le script.
2. **Construction des supports** — ajouter le code dans `scripts/EP000-titre-court/`
   et le support visuel dans `presentations/`.
3. **Enregistrement** — dérouler la section « Enregistrement » de la checklist.
4. **Montage et publication** — dérouler les sections « Montage » et « Publication »,
   puis consigner les retours après diffusion.

## Fichiers volumineux

Les rushes, exports vidéo et jeux de données massifs ne sont pas versionnés
(voir `.gitignore`). Ils doivent être hébergés sur un stockage externe et
référencés par un lien dans les notes de l'épisode.

## Licence

Ce dépôt est distribué sous licence MIT (voir [LICENSE](LICENSE)).

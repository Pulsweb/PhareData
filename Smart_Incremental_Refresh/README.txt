SMART INCREMENTAL REFRESH · CODE DE RÉFÉRENCE v1.2
==================================================
Ce dossier contient le même code que la section 7 de la documentation PDF,
un fichier par cellule de notebook ou par script SQL. Copier depuis ces
fichiers plutôt que depuis le PDF (indentation Python garantie).

1_Warehouse                     Scripts à exécuter UNE FOIS dans l'éditeur SQL
                                du Warehouse, dans l'ordre 01, 02, 03.
2_SmartRefresh_DetectChanges    Notebook Python, 7 cellules (0, 0b, 1 à 5).
                                Un fichier = le contenu complet d'une cellule.
                                La cellule 0 doit être marquée « Toggle parameter cell ».
3_SmartRefresh_ExecuteRefresh   Notebook Python, 5 cellules (1 à 5).
                                C'est le SEUL notebook à lancer ou à planifier.
4_Exploitation                  Requêtes de suivi, corrections manuelles,
                                scénario de test, migration depuis la v1.

Les fichiers .sql des dossiers 2 et 3 commencent par %%tsql : ce sont des
cellules de notebook, pas des scripts pour l'éditeur SQL.

Repères dans le code :
  ◄ À ADAPTER        valeur propre à votre environnement, à remplacer
  ◄ NE PAS MODIFIER  le fonctionnement en dépend
Valeurs à remplacer partout : <NomDuWarehouse>, MON_MODELE,
<WORKSPACE_ID>, <SEMANTIC_MODEL_ID>, et les noms de tables d'exemple.

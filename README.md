# CyberPulse — plateforme de veille cybersécurité

Version prête à déposer dans un dépôt GitHub et à publier avec GitHub Pages. Elle collecte des flux RSS/Atom via GitHub Actions, publie un fichier JSON statique, permet d'ajouter des flux et de générer un rapport hebdomadaire Markdown ou HTML.

## Fonctions

- Tableau de bord et fil d'articles : alertes, incidents, vulnérabilités, fuites de données, phishing et actualités.
- Actualisation automatique programmée toutes les 6 heures via GitHub Actions, et exécution manuelle possible.
- Déduplication par URL et tri par date.
- Ajout de flux RSS/Atom dans l'interface et export/import JSON.
- Rapport hebdomadaire local (7 derniers jours) téléchargeable en Markdown ou HTML.
- Ajout manuel d'éléments locaux et export JSON.
- Hébergement statique GitHub Pages, sans serveur web ni base de données.

## Mise en ligne sur GitHub

1. Créez un dépôt GitHub, par exemple `cyberpulse`.
2. Décompressez ce dossier et déposez **tout son contenu** à la racine du dépôt (`index.html`, `sources.json`, `data/`, `scripts/`, `.github/`, `requirements.txt`, `README.md`).
3. Dans **Settings → Pages**, choisissez **Deploy from a branch**, branche `main`, dossier `/ (root)` puis enregistrez.
4. Dans **Settings → Actions → General**, vérifiez que les actions sont autorisées et que les workflows peuvent avoir la permission d'écrire dans le dépôt (si la politique de l'organisation le permet).
5. Ouvrez l'onglet **Actions**, sélectionnez **Actualiser la veille CyberPulse**, puis cliquez sur **Run workflow** pour la première collecte.
6. Attendez la fin du workflow puis rechargez le site Pages. Le flux de données sera mis à jour ensuite toutes les six heures environ.

Le nom du dépôt peut être différent ; les chemins sont relatifs au site (`./data/veille.json`).

## Ajouter un flux RSS durable

1. Dans CyberPulse, ouvrez **Flux RSS**, saisissez le nom, l'URL et la catégorie, puis cliquez sur Ajouter.
2. Cliquez sur **Exporter la configuration des flux (.json)**.
3. Ouvrez `sources.json` dans GitHub et ajoutez l'objet exporté à la liste (évitez les doublons). Exemple :

```json
{
  "name": "Nom de la source",
  "url": "https://exemple.org/rss.xml",
  "category": "alerte",
  "enabled": true
}
```

4. Validez le commit. Le workflow se déclenche automatiquement à la modification de `sources.json`.

Catégories prises en charge : `alerte`, `fuite`, `cve`, `phishing`, `actualite`. Les URL doivent être publiques et accessibles sans authentification. Le collecteur n'exécute pas le contenu des flux ; il récupère uniquement les métadonnées (titre, date, lien et résumé).

## Rapport hebdomadaire

Dans **Rapport de la semaine**, cliquez sur **Générer le résumé**, puis téléchargez le rapport en Markdown (`.md`) ou HTML (`.html`). La génération se fait dans le navigateur, à partir des éléments déjà chargés et des entrées locales.

## Limites importantes

- GitHub Pages est statique : l'interface seule ne peut pas déclencher un workflow ni partager les données locales d'un visiteur.
- Les flux ajoutés via l'interface sont enregistrés dans `localStorage` pour ce navigateur. Pour les intégrer à la collecte automatique, il faut les ajouter à `sources.json` dans le dépôt.
- La détection de fuites et la sévérité sont des heuristiques sur les titres et résumés ; elles peuvent être inexactes. Confirmer les faits sur les sources officielles.
- Le rapport est une synthèse des métadonnées RSS, pas une analyse complète des articles. Il ne faut pas l'utiliser comme qualification officielle sans relecture.
- La fréquence GitHub Actions dépend des quotas et de la disponibilité de GitHub ; les exécutions planifiées peuvent être décalées. L'actualisation automatique ne garantit pas que chaque source soit disponible à chaque cycle.
- Les entrées ajoutées manuellement dans l'interface ne sont pas visibles pour les autres utilisateurs et ne sont pas intégrées au JSON public sans action éditoriale dans le dépôt.

## Sources initiales

Les flux initiaux de `sources.json` sont des suggestions à vérifier au moment du déploiement. Vous pouvez désactiver une source avec `"enabled": false` ou en ajouter d'autres. Respectez les conditions d'utilisation et la charge raisonnable des sites sources.

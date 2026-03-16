

# "L'univers d'Arielle" (Dragon's Odyssey)

## Description

**Le Monde d'Arielle** est un jeu d'aventure en 2D développé en Python utilisant la bibliothèque Pygame. Le joueur incarne un personnage qui doit naviguer à travers différents niveaux, collecter des pièces, éviter des monstres et résoudre des défis chronométrés. Le jeu intègre des mécaniques de jeu évolutives, des contrôles via clavier ou manette, et une progression à travers 5 niveaux uniques.

Le jeu est inspiré par des classiques comme les jeux d'aventure et de plateforme, avec un focus sur la stratégie, les réflexes et la gestion du temps. Les cartes sont créées avec Tiled, permettant des environnements variés comme des arènes, labyrinthes, parcours et salles d'affrontement.

## Fonctionnalités Principales

- **Système de Niveaux** : 5 niveaux distincts avec des objectifs variés (collecte de pièces, parcours, affrontements). Chaque niveau introduit de nouvelles mécaniques et augmente la difficulté, avec un système de progression basé sur la réussite des niveaux précédents.

- **Mécaniques de Jeu** :
  - **Collecte de Pièces** : Les pièces servent à la fois de score (10 points par pièce normale) et de munitions pour les tirs. Elles sont essentielles pour progresser et débloquer des actions.
  - **Tir de Balles** : Le joueur peut tirer des balles pour combattre les monstres. La puissance des balles peut être renforcée aléatoirement (1-10 dégâts) en collectant des pièces dans certains niveaux.
  - **Murs Destructibles** : Utilisez des pièces pour détruire des murs stratégiques, ouvrant de nouveaux chemins. Coût variable selon le niveau (ex. -30 points par mur dans certains cas).
  - **Pièces Spéciales** : Certaines pièces offrent des effets temporaires comme bonus (vitesse, double saut, ralentissement du chrono) ou débuffs (réduction de vitesse, accélération du chrono).
  - **Système de Santé** : Le joueur et les monstres ont une barre de santé. Le joueur perd de la vie en cas de collision ; les monstres peuvent être vaincus en les tirant dessus.

- **IA des Monstres** : Les monstres ont des comportements dynamiques incluant poursuite intelligente (anticipation des mouvements du joueur), patrouille aléatoire, et effets de zone (traînées ralentissantes). Ils alternent entre modes agressif et passif selon le score du joueur, rendant le jeu imprévisible.

- **Contrôles** : Support complet du clavier et des manettes (PS4, Xbox 360, etc.) avec mapping automatique des boutons. Fonction hot-plug pour connecter/déconnecter des manettes en cours de jeu. Deadzone configurable pour éviter les dérives analogiques.

- **Menus** :
  - Menu principal avec options pour commencer, accéder aux niveaux, options, réinitialiser la progression, ou quitter.
  - Menu de niveaux avec progression sauvegardée et déblocage séquentiel.
  - Menu d'options pour ajuster les volumes musique/SFX et les contrôles.
  - Menu pause en jeu pour reprendre, retourner au menu principal ou quitter.

- **Sauvegarde de Progression** : Système de sauvegarde automatique dans le dossier `saves/`, permettant de débloquer les niveaux au fur et à mesure. Possibilité de réinitialiser la progression depuis le menu principal.

- **Effets Visuels** : Animations fluides des sprites (4 directions pour le joueur et les monstres), particules pour les impacts et effets spéciaux, barres de santé dynamiques, et rendu des cartes Tiled avec scrolling fluide.

- **Audio** : Musique de fond adaptative (changement selon la tension du jeu) et effets sonores pour les actions (collecte, tirs, collisions). Intégration via Pygame Mixer, avec contrôle des volumes dans les options.

## Installation et Exécution

### Prérequis

- Python 3.x
- Bibliothèques Python : `pygame`, `pytmx`, `pyscroll`

### Installation

1. Clonez le dépôt :

   ```bash
   git clone https://github.com/mulobearielle/le-monde-de-arielle.git
   cd le-monde-de-arielle
   ```

2. Installez les dépendances :

   ```bash
   pip install pygame pytmx pyscroll
   ```

3. Assurez-vous que les assets sont présents dans les dossiers `img/`, `maps/`, `song/`, etc.

### Exécution

Lancez le jeu avec :

```bash
python main.py
```

Le jeu s'ouvrira en mode plein écran adapté à votre résolution.

## Comment Jouer

### Contrôles

- **Clavier** :
  - Flèches directionnelles : Déplacement
  - Espace : Tir
  - Échap : Pause/Menu
- **Manette** :
  - Stick gauche : Déplacement
  - Bouton Croix (X) : Tir
  - Bouton Start : Pause
  - Mapping automatique pour PS4, Xbox, etc.

### Objectifs Généraux

Le jeu repose sur une combinaison de stratégie, de réflexes et de gestion du temps. Voici les objectifs principaux à maîtriser pour progresser :

- **Collecte de Pièces** : Les pièces sont au cœur du gameplay. Elles augmentent votre score (10 points par pièce) et servent de munitions pour tirer des balles. Collectez-en autant que possible pour renforcer vos capacités de combat et atteindre les seuils de victoire.

- **Gestion des Monstres** : Évitez les collisions avec les monstres pour préserver votre santé (3 vies maximum). Alternativement, combattez-les en tirant des balles chargées par les pièces. Observez leur IA : ils peuvent être en mode poursuite ou patrouille, et laisser des effets de zone.

- **Respect des Conditions de Victoire** : Chaque niveau a des critères spécifiques (ex. : collecter X pièces en Y secondes, atteindre une sortie, vaincre des ennemis). Le temps est souvent limité, rendant la gestion des ressources cruciale. Échouer signifie recommencer le niveau.

- **Utilisation Stratégique des Pièces** : Au-delà du score, les pièces permettent de détruire des murs pour ouvrir des chemins alternatifs. Cela peut révéler des raccourcis ou des pièces cachées, mais coûte des points – choisissez judicieusement pour optimiser votre progression.

- **Adaptation aux Mécaniques** : Les niveaux évoluent ; maîtrisez les pièces spéciales (bonus comme vitesse ou malus comme accélération du chrono) et les effets aléatoires. Combinez collecte, combat et navigation pour maximiser vos chances de victoire.

### Niveaux

Le jeu propose 5 niveaux progressifs, chacun introduisant de nouvelles mécaniques et défis. Voici un détail complet de chaque niveau :

1. **Niveau 1 : Arène - Bienvenue dans l'arène !**
   - **Objectif** : Collecter 8 pièces en 30 secondes tout en évitant le dragon.
   - **Conditions de victoire** : Obtenir 8 pièces (10 points chacune) avant la fin du temps.
   - **Conditions de défaite** : 3 collisions avec le dragon ou temps écoulé sans avoir 8 pièces.
   - **Mécaniques** : Évitement du monstre, collecte simple.
   - **Commandes** : Flèches directionnelles (clavier/manette).

2. **Niveau 2 : Labyrinthe - Labyrinthe destructible**
   - **Objectif** : Atteindre la sortie en détruisant les murs stratégiques.
   - **Conditions de victoire** : Détruire les murs (40 pts premier mur, +20 pts/mur supplémentaire) et atteindre la sortie dans le temps imparti.
   - **Conditions de défaite** : Temps écoulé avant d'atteindre la sortie.
   - **Mécaniques** : Murs destructibles utilisant des pièces, navigation labyrinthique.
   - **Commandes** : Flèches directionnelles (clavier/manette).

3. **Niveau 3 : Parcours - Couloir de la mort**
   - **Objectif** : Traverser le couloir piégé dans le temps imparti.
   - **Conditions de victoire** : Atteindre la fin du parcours à temps ; les pièces ouvrent des raccourcis.
   - **Conditions de défaite** : Temps écoulé avant la fin du parcours.
   - **Mécaniques** : Système aléatoire où chaque piège donne un bonus ou malus (vitesse, double saut, ralentissement du chrono, etc.) ; murs destructibles.
   - **Commandes** : Flèches directionnelles (clavier/manette).

4. **Niveau 4 : Affrontement - Chasse au boss**
   - **Objectif** : Éliminer toutes les vagues de monstres en 2 salles.
   - **Conditions de victoire** : Vider chaque salle de ses monstres et battre le boss final avant la fin du temps.
   - **Conditions de défaite** : Temps écoulé avant d'éliminer le boss.
   - **Mécaniques** : Collecte de pièces pour munitions ; tir de balles pour combattre ; pièces renforcent aléatoirement les balles (1-10 dégâts).
   - **Commandes** : Déplacement (flèches), Tir (Espace/F clavier / X manette).

5. **Niveau 5 : Final - Défi ultime**
   - **Objectif** : Combiner toutes les mécaniques en un seul défi massif.
   - **Conditions de victoire** : Atteindre la sortie en combinant destruction de murs stratégiques, collection de pièces-clés et élimination d'ennemis.
   - **Conditions de défaite** : Temps écoulé ou défaite par les ennemis.
   - **Mécaniques** : Toutes les mécaniques précédentes réunies ; pièces servent de score et munitions ; temps critique.
   - **Commandes** : Déplacement (flèches), Tir (Espace/F clavier / X manette).

## Structure du Projet

Voici un aperçu détaillé de la structure des fichiers et dossiers :

### Fichiers Principaux

- `main.py` : Point d'entrée du jeu, gestion des menus principaux et boucle principale.
- `Game.py` : Classe principale du jeu, gestion des niveaux, collisions, logique de jeu.
- `player.py` : Classe du joueur, animations, mouvements, tirs.
- `monster.py` : Classe des monstres, IA, santé, animations.
- `bullet.py` : Classe des balles/projectiles.
- `collectible.py` : Classe des objets collectibles (pièces normales et spéciales).
- `destructibleWall.py` : Classe des murs destructibles.
- `particle.py` : Système de particules pour effets visuels.
- `level_menu.py` : Menu de sélection des niveaux avec progression.
- `option.py` : Menu des options (volumes, contrôles).
- `summaries.py` : Textes d'introduction et résumés des niveaux.
- `gamePad.py` / `gamePad1.py` / `testGamePad.py` : Gestion des manettes, mapping des boutons, hot-plug.

### Dossiers

- `__pycache__/` : Cache compilé Python (ignoré par Git).
- `img/` : Images et sprites (joueur, monstres, balles, pièces, etc.). Contient aussi `img.zip` pour archivage.
- `maps/` : Cartes du jeu créées avec Tiled (.tmx pour les cartes, .tsx pour les tilesets).
  - `niveau1.tmx` à `niveau5.tmx` : Les 5 niveaux principaux.
  - Tilesets : `Nature.tsx`, `deuxieme niveau.tsx`, `labyrinthe.tsx`, `maison.tsx`.
- `dessin/` : Dessins ou concepts artistiques. Contient `dessin.zip`.
- `saves/` : Fichiers de sauvegarde de progression.
- `song/` : Musique et effets sonores.

### Fichiers Tiled

- `CARTE DU JEU.tiled-project` : Projet Tiled pour l'édition des cartes.
- `CARTE DU JEU.tiled-session` : Session Tiled sauvegardée.

### Autres

- `RapidWizard.pck` : Pack d'assets (probablement des sprites ou sons).

## Technologies Utilisées

- **Python** : Langage principal.
- **Pygame** : Moteur de jeu 2D.
- **Pytmx** et **Pyscroll** : Chargement et rendu des cartes Tiled.
- **Tiled** : Éditeur de cartes pour créer les niveaux.
- **Git** : Contrôle de version.

## Crédits

- Développé par [mulobearielle](https://github.com/mulobearielle) et [FredDev12](https://github.com/freddev12).
- Assets graphiques : Sprites personnalisés et packs comme RapidWizard.
- Musique : Fichiers dans `song/`.
- Inspirations : Jeux d'aventure classiques avec mécaniques de temps et stratégie.

## Licence

Ce projet est sous licence [MIT / GPL / etc.]. Voir le fichier LICENSE pour plus de détails.

## Contributions

Les contributions sont les bienvenues ! Ouvrez une issue ou une pull request sur GitHub.

---

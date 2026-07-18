# Observer Patch Holography (OPH)

> L'OPH est un programme de reconstruction par cohérence d'observateurs. Chaque observateur possède un patch local ; la physique publique est la structure qui survit à l'accord sur les recouvrements.

**Version anglaise :** [README.md](README.md)

**Liens rapides :** [site OPH](https://floatingpragma.io/oph/) | [OPH Textbooks](https://learn.floatingpragma.io/) | [Book: Reverse Engineering Reality](https://oph-book.floatingpragma.io/) | [Ω](https://omega.floatingpragma.io/) | [Blog](https://blog.floatingpragma.io/) | [Simulation](https://simulation.floatingpragma.io)

**Ce que c'est :** L'OPH étudie la physique publique reconstruite par des
systèmes de type observateur : patches bornés, état local, interfaces visibles,
relecture, enregistrements, réparations et paquets de preuves publics. Cinq
axiomes définissent la reconstruction de base. Chaque conclusion physique
appartient à une branche nommée avec ses prémisses. Le pixel \(P\) est le point
fixe de cartes locales déclarées ; la capacité \(N\) est la coordonnée d'une
carte globale de relecture qui reste à construire. Ces équations ne fixent pas
à elles seules l'univers exact.

**Résultat fini le plus fort :** Sur un écran sphérique satisfaisant **UD12**
et **RP-A5**, toute réalisation de courant de dimension douze, de rang plein,
compacte, fermée par commutateur, naturelle sous raffinement et portant une
action intérieure de \(A_5\), possède l'algèbre de Lie
\(\mathfrak{su}(3)\oplus\mathfrak{su}(2)\oplus\mathfrak u(1)\).
Le crochet de coefficients est explicite. Son interprétation comme courant
physique exige **PORT-CURRENT-INNER**. Le quotient global
\((SU(3)\times SU(2)\times U(1))/\mathbb Z_6\) exige en plus l'équilibre des
déterminants, les descentes de spin et de boucle, la compatibilité de
raffinement et le noyau matière/tensoriel de la réalisation minimale
admissible. La topologie de l'écran ne fixe ni l'hypercharge, ni la chiralité,
ni les familles, ni les masses, ni les couplages.

**Frontière quantitative :** Le doublement réversible de l'adjoint produit
donne \(m_{\rm rep}=2(8+3+1)=24\), indépendamment des douze ports et des
24 cases orientées de l'écran. Leur égalité est un alignement. L'identification
de la charge d'écran avec l'exposant de transmutation hiérarchique exige un
reçu séparé. Les valeurs
\(136.994835177413\ldots\), \(137.035660136947\ldots\) et
\(137.035959513609\ldots\) proviennent de cartes incomplètes ou liées à une
coordonnée de comparaison. Elles ne sont pas des prédictions physiques de la
constante de structure fine. Le théorème \(A_5\) ne renforce aucune prédiction
de masse ou de couplage.

**Frontière des affirmations :** Les théorèmes finis de réparation,
d'algèbre de registres, de crochet de coefficients, de réseau et
d'arithmétique sont exacts sous leurs hypothèses. Les branches de Lorentz,
Einstein, jauge compacte, matière, hiérarchie et cosmologie sont
conditionnelles. Le corpus Lean certifie un sous-ensemble fini sans `sorry`,
dont le théorème étroit de séparation de douze entiers positifs ; il ne
formalise ni le sélecteur d'écran ni les reçus physiques de jauge. La
complétion physique de Thomson, la lecture W/Z et les dérivations de masses
sont des travaux en cours. La cosmologie ne porte aucune cible prédictive
verrouillée.

**Programme de falsification :** Le
[programme de falsification OPH](docs/OPH_FALSIFICATION_PROGRAM.md) sépare les
contre-exemples mathématiques des tests physiques dont les reçus de branche
sont fournis. La cosmologie, la matière noire et les dérivations quantitatives
dont la lecture physique est un travail en cours n'y sont pas promues.

**La colonne vertébrale technique :** La
[preuve compacte](extra/compact_proof_of_oph.pdf) porte l'argument court, le
[registre de fermeture](docs/CLOSURE_LEDGER.md) porte le statut quantitatif et
le [programme de falsification](docs/OPH_FALSIFICATION_PROGRAM.md) porte les
tests arrivés à maturité. Les autres fichiers de `docs/` sont des notes de
preuve, d'audit ou de politique.

Le **Paper 6.
[Paradise as Fixed-Point Consensus](paper/paradise_as_fixed_point_consensus.pdf)**
développe l'interprétation métaphysique de la continuation des observateurs.
Il est extérieur au paquet de théorèmes de physique récupérée.

## Description informelle

L'OPH est la reconstruction observateur-premier de la physique fondamentale.
Il part d'observateurs finis sur une géométrie finie d'écran holographique. Sa
base de travail est algébrique-quantique : algèbres de patchs, états,
probabilités de type trace/Born sur les surfaces d'enregistrement déclarées et
entropie généralisée font partie du point de départ formel. À partir de cette
base, l'OPH propose des branches conditionnelles de reconstruction pour
l'espace-temps, la structure de jauge, les particules, les enregistrements et la
synchronisation des observateurs ; chaque branche conserve les prémisses et les
portes de preuve déclarées dans les papiers. Au niveau opératoire, des patches
d'observateurs finis portent des enregistrements locaux, ne comparent que les
données visibles dans leurs recouvrements, réparent les désaccords par des
mouvements de récupération déclarés et convergent vers des points fixes stables
qui survivent au raffinement. Le monde public est ce qui reste stable lorsque
ces vues locales deviennent mutuellement cohérentes. Le langage de simulation
de l'OPH nomme ce réseau d'observateurs auto-cohérent au niveau
opératoire. Le dossier en faveur de l'OPH est
mathématique et empirique : la même architecture de cohérence d'observateurs
est proposée pour retrouver la physique établie. L'hypothèse de la boucle
étrange explique pourquoi un monde auto-cohérent existe et produit des
observateurs : ce monde engendre des observateurs qui reconstruisent la
simulation qui les a produits, puis construisent le matériel et le logiciel qui
ferment la boucle de l'intérieur.

Dans la pile de papiers, un patch d'observateur désigne un objet algébrique
abstrait avec algèbre accessible, état, algèbre d'enregistrements, interfaces
visibles de recouvrement, instruments de réparation et données de checkpoint.
Un patch de support est une carte géométrique de cet objet, par exemple un cap
sur $S^2$ ou un diamant causal. Un patch porteur est une réalisation physique
ou numérique des mêmes statistiques d'interface visible et d'enregistrement, à
erreur déclarée. Cette séparation empêche la théorie de dépendre d'une analogie
matérielle particulière. La thèse plus forte selon laquelle l'information et le
calcul sont ontologiquement premiers relève de l'interprétation, sauf si une
branche fournit un discriminateur empirique propre.

La plupart des théories commencent en supposant l'espace-temps, les champs
quantiques et une liste de constantes. L'OPH commence un cran plus tôt, avec
des patches d'observateurs finis algébriques-quantiques dont les descriptions
doivent s'accorder sur leurs recouvrements. Dans la partie relativité de la
théorie, le consensus fini fournit des formes normales quotient. La lecture
d'espace-temps ordinaire en 3+1 dimensions et l'équation de gravité de type
Einstein ne sont reconstruites que sur la branche à cinq axiomes du coeur
récupéré : le papier compact fournit lecture géométrique, flot modulaire
contrôlé, pont de contrainte nulle, transport d'intervalle borné,
stationnarité entropique admissible à cap fixe, variation d'aire de petite boule, passage
scalaire-tenseur et spécification séparée de la fermeture de capacité. Les cellules finies servent de régulateur : elles gardent la
construction concrète avant la limite lisse à grande échelle.
Les trois dimensions spatiales viennent de la même branche d'écran : une fois
$\mathrm{Conf}^+(S^2)\cong\mathrm{SO}^+(3,1)$ obtenu, la carte spatiale de
l'observateur est $H^3\simeq\mathrm{SO}^+(3,1)/\mathrm{SO}(3)$, de dimension
$6-3=3$.

Dans la partie jauge de la théorie, l'OPH demande quelles charges internes et
quelles étiquettes de particules peuvent être transportées de façon cohérente
sur les recouvrements. Les charges visibles à cutoff fixe engendrent une
catégorie tensorielle, mais sa limite de raffinement dépend d'un certificat
explicite de jauge compacte : morphismes surjectifs cohérents entre les groupes
de bord, extensibilité des états finis, plongements des blocs finis compatibles
avec les centres, réalisations tensorielles finies et fibres d'oubli
compatibles. Sur une queue cofinale munie de ce certificat, la reconstruction
produit un groupe de jauge compact. Avec le paquet
matière explicite à un Higgs et la règle de réalisation
admissible minimale, la structure sélectionnée du Modèle Standard est
$SU(3)\times SU(2)\times U(1)/\mathbb Z_6$, avec le réseau des hypercharges,
trois couleurs et trois générations. La mécanique quantique est le langage
algébrique d'information porté par cette architecture de patches
d'observateurs. Sous les hypothèses de jauge compacte indiquées, la même pile
donne la forme euclidienne de Yang-Mills et un mécanisme fini de gap de
réparation. L'identification de ce mécanisme au gap de Yang-Mills
quadridimensionnel exige le certificat déclaré de limite continue
multirésolution, de positivité par réflexion, de transfert/intertwiner et de
non-trivialité.

Le statut du secteur des particules figure dans **L'évidence en un coup d'œil**
ci-dessous ; la prose d'audit complète
vit dans le papier des particules et dans
[`code/particles/`](code/particles/README.md).

Le mécanisme est la boucle de consensus à point fixe. Les observateurs locaux
n'accèdent pas à un état global depuis l'extérieur. Ils portent des états de
patch finis, échangent les données visibles dans les recouvrements, rejettent
les prolongements incohérents et conservent les motifs stables qui peuvent être
synchronisés. Géométrie, particules, lois et enregistrements sont les points
fixes à grande échelle de ce calcul en réseau d'observateurs.

L'OPH ne porte aucun bouton de réglage : aucun nombre mesuré n'apparaît dans
une équation définissante
([STRANGE_LOOP_PRINCIPLES.md](docs/STRANGE_LOOP_PRINCIPLES.md)). Les voies
dont les termes de fermeture restent ouverts empruntent des valeurs de travail
localisées en attendant : un P de travail localisé à partir de α mesuré sous
SL-3, un N de travail localisé à partir de Λ mesuré sous SL-4, le pont SI au
césium sous SL-5 et les sélections structurelles déclarées. Chaque emprunt est
compté, et le registre de fermeture
([CLOSURE_LEDGER.md](docs/CLOSURE_LEDGER.md)) consigne le statut de chaque
ligne. La règle de provenance à l'intérieur de ce cadre est qu'aucune cible
mesurée ni constante numérique ajustée ne peut entrer dans une carte source
déclarée. Les axiomes
algébriques-quantiques et l'écran $S^2$ restent des prémisses explicites.
Quantitativement, les lignes publiques sont organisées par trois quantités
internes : un point fixe local de pixel $P_\star$, un point fixe global de
capacité d'enregistrement $N_{\mathrm{CRC}}$ et un rapport de mise à l'échelle
$\gamma_\star$. Une coordonnée source ne mérite ce nom que si sa carte déclarée
l'émet sans cible ajustée ; sinon elle reste un diagnostic ou une coordonnée de
comparaison. Les mesures peuvent indiquer sur quelle branche nous sommes, mais
les valeurs source doivent venir des calculs de point fixe. Les lignes à
fermeture empirique sont marquées ci-dessous. La discussion d'échelle détaillée
est rassemblée une seule fois ci-dessous dans **Géométrie, Symétrie Et
Échelle**.

Dans tout le projet, la preuve OPH garde la même forme générale. Une
affirmation s'ancre dans des patches bornés de type observateur, avec état
local, frontières explicites, relecture, enregistrements, mouvements de retour
ou de réparation et dossiers de preuve publics. L'histoire invariante des
patches d'observateurs porte l'affirmation à travers les présentations, les
choix de coordonnées et les traces d'implémentation.

## Le piège de l'espace-temps

Le premier obstacle conceptuel est que l'OPH ne traite pas l'espace-temps
comme le contenant dans lequel la réalité se déroule. L'espace et le temps ne
sont pas des choses en soi. Ce sont des descriptions stables, orientées
observateur, qui apparaissent lorsque de nombreuses perspectives finies peuvent
devenir mutuellement cohérentes.

C'est particulièrement important pour le temps. Le langage ordinaire traite le
temps comme un fleuve de fond qui coulerait sans observateurs. L'OPH rejette
cette image. À la base, il y a des observateurs,
des enregistrements, des changements dans ces enregistrements et des règles qui
font s'accorder les enregistrements qui se recouvrent. Le temps est l'ordre
qu'un observateur donne aux changements de ses propres enregistrements. Le
temps public est la partie de cet ordre qui peut être synchronisée avec
d'autres observateurs. En ce sens précis, le temps est subjectif : il appartient
d'abord au flux d'enregistrements d'un observateur. Il reste pourtant contraint.
Une mauvaise horloge, un faux souvenir ou une histoire incohérente échouent
lorsqu'ils ne peuvent pas s'accorder avec le reste du réseau d'enregistrements.

L'étiquette d'illusion ne fonctionne que comme métaphore : le contenant que
nous semblons habiter est une apparence produite par une cohérence plus
profonde. Comme physique, l'expression plus précise est description publique
émergente.

Depuis l'intérieur d'une perspective, le monde paraît évident. Il y a un champ
d'expérience à peu près sphérique qui s'étend au loin, trois directions dans
lesquelles se déplacer et un temps qui avance. Les autres observateurs
rapportent des contenus compatibles depuis d'autres angles. L'hypothèse
naturelle est donc que tout le monde habite un espace-temps préexistant rempli
d'objets. L'OPH inverse cette hypothèse. Chaque observateur possède une
description locale d'espace-temps générée par ses propres enregistrements,
horloges, horizons et corrélations accessibles. L'espace-temps public, y
compris la coordonnée de temps utilisée par la physique, est la couche de
compatibilité qui permet à ces descriptions de s'accorder.

Cela ne rend pas l'espace-temps ordinaire arbitraire ou inutile. Cela explique
pourquoi il fonctionne si bien. Les équations d'Einstein décrivent la grammaire
lisse à grande échelle de l'apparence partagée. La thèse plus profonde est que
cette apparence partagée émerge de la cohérence des recouvrements entre
observateurs, au lieu d'appartenir à l'inventaire de départ du monde.

## Géométrie, Symétrie Et Échelle

Le langage de sphère dans l'OPH est un langage de géométrie. Dans les cartes
régulatrices symétriques, une coupe accessible à un observateur peut être
représentée par la deux-sphère $S^2$. Ces cartes décrivent une géométrie
angulaire de support. Des modèles régulateurs finis implémentent les
contraintes algébriques de patches et de recouvrements exposées par cette
géométrie.

L'OPH utilise une idéalisation de réseau d'écran partagé et de nombreux
patches d'observateurs finis. L'écran d'un observateur est une coupe d'accès locale sur
ce réseau, au lieu d'une sphère privée séparée. La carte $S^2$ décrit une coupe
de support, sans être une boule littérale recouverte de données.

Cette carte sphérique porte plusieurs tâches précises. Les caps et les colliers
donnent les données locales de coupe utilisées par le flot modulaire et la
variation d'entropie. La symétrie conforme de la sphère est la forme céleste du
groupe de Lorentz connexe, donc la même carte fournit le pont cinématique vers
la branche d'espace-temps émergent en $3+1$ dimensions quand les conditions
sur les caps et le flot modulaire sont satisfaites. Sur cette branche
contrôlée, la carte spatiale orientée observateur est exactement
tridimensionnelle. Les caps marquent des coupes et des côtés de la carte, pas
des points d'observateur privilégiés. Les jetons d'enregistrement ne peuplent
la carte que lorsque des réponses de caps calibrées et un budget d'erreur
permettent la localisation. Les preuves finies peuvent signaler une ambiguïté. Les
harmoniques sphériques organisent les modes angulaires. Les cellulations finies
de la même carte donnent la surface régulatrice où les ports de patches, les
données d'arêtes et les contrôles de recouvrement deviennent explicites ; leur
rôle est celui d'un régulateur fini, sans statut de continuum invariant de
Lorentz.

L'ancre de symétrie finie est $A_5$, le groupe des rotations de
l'icosaèdre. Elle fournit le squelette icosaédrique derrière le langage des
porteurs de patches échosaédriques : une façon finie et très symétrique
d'organiser ports, recouvrements et données locales de comparaison sans traiter
le porteur comme une boule lisse.

$A_5$ porte une construction finie exacte sur l'espace orienté des
coefficients de douze ports. Les reçus **UD12** de séparation unitaire et
**RP-A5** de placement donnent
$P_{12}\cong\mathbf1\oplus\mathbf3\oplus\mathbf3'\oplus\mathbf5$, et le rappel
équivariant du commutateur de blocs construit
$\mathfrak u(1)\oplus\mathfrak{su}(3)\oplus\mathfrak{su}(2)$ avec une bande
de rang cinq non centrale. Ce crochet agit sur les fluctuations des ports ;
les projecteurs centraux d'enregistrement commutent. La promotion physique
exige le reçu **PORT-CURRENT-INNER** : courant compact anti-hermitien de rang
plein, fermé par commutateur, naturel sous raffinement et action intérieure de
$A_5$.

La complétion équilibrée en trace s'intègre abstraitement en
$S(U(3)\times U(2))\cong(SU(3)\times SU(2)\times U(1))/\mathbb Z_6$.
Le réseau des six axes possède séparément un résidu $\mathbb Z_6$, sans être
un réseau physique de cocaractères. La forme globale physique exige
l'équilibre des déterminants, la descente spin/boucle/raffinement et le noyau
de l'action tensorielle MAR réalisé. Lean certifie la séparation arithmétique
de douze entiers positifs, le commutateur abstrait, sa dimension et son témoin
non central, le quotient du réseau et $B_6/B_0=11/25$ ; il ne dérive ni la
charge d'Euler, ni le sélecteur, ni les portes physiques.

L'écran à séparation unitaire a douze ports et 24 cases orientées.
Indépendamment, le doublement réversible de l'adjoint produit donne
$m_{\rm rep}=2(8+3+1)=24$. L'égalité est un alignement de branches, non une
identification physique sans reçu ; aucune masse ni aucun couplage n'en
découle. Voir le
[papier compact de reconstruction](paper/recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact.pdf).

La même géométrie donne une échelle de sphères utile pour le lecteur. $S^0$
est la première distinction de germe ou de lecture. $S^1$ est la récurrence,
la boucle où un enregistrement peut revenir sur lui-même. $S^2$ est l'écran
d'horizon et l'archive publique. Le dernier échelon signifie le rôle de bulk
orienté observateur en trois dimensions ; sur la branche de Lorentz contrôlée,
sa carte cinématique canonique est $H^3$. Aucune topologie globale $S^3$ ne
découle de ce moyen mnémotechnique. La taxonomie des particules reste portée par
les branches de Lorentz et de jauge.

L'ancre exceptionnelle est le groupe de Lie $E_8$ et sa structure de réseau
de racines. $E_8$ donne le langage de fermeture exceptionnelle utilisé dans
le côté symétries supérieures et représentations de la pile OPH. Le groupe
icosaédrique binaire et le $E_8$ affine se rencontrent par la correspondance
de McKay. C'est pourquoi le langage $A_5$-icosaédrique et le langage de type
$E_8$ appartiennent à une même histoire de symétrie. Ces noms désignent des
contraintes de symétrie et une structure de régulateur.

La discussion d'échelle a trois rôles, rassemblés ici. La coordonnée locale
$P_\star$ est le point fixe du pixel d'écran. La coordonnée globale
$N_{\mathrm{CRC}}$ est le point fixe de capacité d'enregistrement. Le rapport
d'échelle $\gamma_\star$ relie la géométrie OPH sans dimension aux unités SI
après le calcul des points fixes sans dimension.

Les deux équations de point fixe sont :

```math
P_\star=\varphi+\frac{\sqrt{\pi}}{A_T(P_\star)}
```

et

```math
N_{\mathrm{CRC}}=F(N_{\mathrm{CRC}}),
```

où $F(N)$ est la capacité d'horizon relue par les observateurs à l'intérieur de
l'univers fourni avec la capacité $N$. Intuitivement, $N_{\mathrm{CRC}}$ est la
capacité où l'univers peut relire sa propre frontière sans déficit ni capacité
inerte. La cible de comptage fini derrière cette capacité globale est la
densité

```math
\log|\Omega^{\mathrm{sc}}_N|-N.
```

La règle de mise à l'échelle est :

```math
\gamma_\star=\frac{\ell_\star\nu_{\mathrm{Cs}}}{c}
```

avec $B_\star=3\pi/\ell_\star^2$ et
$G_{\mathrm{SI}}=c^3\ell_\star^2/\hbar$. Les observations peuvent identifier
le voisinage ou la branche, mais elles ne remplacent pas ces calculs de point
fixe.

$P_\star$ alimente la ligne de structure fine,
la structure de jauge, les lignes de particules, les enregistrements et la
synchronisation des observateurs. $N_{\mathrm{CRC}}$ alimente la ligne
cosmologique. La règle d'échelle fixe la normalisation de Newton et l'affichage
à l'échelle de Planck. En unités géométriques,
$\Lambda_{\mathrm{CRC}}=3\pi/(G_{\mathrm{geom}}N_{\mathrm{CRC}})$ avec
$G_{\mathrm{geom}}=\ell_\star^2$. Le pont de hiérarchie électrofaible, la
normalisation de l'adjoint produit $m_{\rm rep}=24$, la politique QCD/hadrons et les règles
de reçus matériels vivent dans leurs papiers et répertoires de travail.

### L'évidence en un coup d'œil

| Surface | Résultat actuel le plus fort | Frontière |
| --- | --- | --- |
| Consensus fini d'observateurs | Les formes normales quotient, les lectures protégées et les résultats finis d'algèbre d'enregistrements sont exacts sous leurs hypothèses. | La géométrie physique exige des reçus de branche séparés. |
| $A_5$ et algèbre de jauge | Le module de coefficients à douze ports admet un crochet compact de type $\mathfrak u(1)\oplus\mathfrak{su}(3)\oplus\mathfrak{su}(2)$. La classification par action intérieure rend ce type unique sur la branche finie déclarée. | Les courants physiques exigent UD12, RP-A5 et PORT-CURRENT-INNER. Le quotient physique $\mathbb Z_6$ exige aussi les reçus de déterminant, spin, descente et matière/tenseur. |
| Relativité et gravité | Le papier compact compose les relations de Lorentz et d'Einstein sur une branche à reçus typés. | La production de la branche réalisée et la carte cosmologique de relecture restent ouvertes. |
| Structure du Modèle Standard | Sur la branche de Réalisation Minimale Admissible, la construction donne le quotient du Modèle Standard, le réseau d'hypercharge, trois couleurs, trois générations et un doublet de Higgs. | C'est un théorème de branche. L'attachement géométrique indépendant des familles par $A_5$ reste ouvert, et aucune voie ne fixe les masses ou couplages. |
| Structure fine | Les cartes source et largeur de jauge déclarées ont des racines uniques certifiées, $136.994835177413\ldots$ et $137.035660136947\ldots$. | Le transport hadronique projeté par Ward est ouvert. Ce sont des racines de cartes, non des prédictions physiques. |
| Particules quantitatives et cosmologie | Les travaux sur la hiérarchie, les masses, les neutrinos, la capacité et le secteur sombre fournissent des formules conditionnelles, diagnostics et contrats de complétion. | Aucune masse physique non nulle de particule, matrice physique de mélange neutrino, prédiction cosmologique fermée ou prédiction de contrôle gravitationnel en laboratoire n'est émise côté source. |

Le registre numérique détaillé est
[`CLOSURE_LEDGER.md`](docs/CLOSURE_LEDGER.md). Le papier sur les particules
porte la table complète des statuts pour les secteurs électrofaible, saveur,
neutrino et hadronique.

## Articles

Ordre recommandé pour un lecteur technique. Les résumés les plus longs
correspondent aux textes qui portent la surface théorématique centrale.

- **Papier 2. [Recovering Relativity and the Standard Model from Observer Overlap Consistency](paper/recovering_relativity_and_standard_model_structure_from_observer_overlap_consistency_compact.pdf)** : noyau technique des constructions conditionnelles de Lorentz, Einstein et jauge compacte, de la branche matière MAR et de l'algèbre finie séparée des coefficients $A_5$. Cette dernière n'est physique qu'avec UD12, RP-A5 et PORT-CURRENT-INNER ; sa forme globale exige aussi les portes de déterminant, spin, descente et action tensorielle MAR. Aucune masse ni aucun couplage n'en découle.
- **Papier 1. [Observers Are All You Need](paper/observers_are_all_you_need.pdf)** : synthèse large et meilleure porte d'entrée. Il explique les patches d'observateurs finis, la cohérence de recouvrement, les enregistrements, les mouvements de réparation, l'univers effectif reconstruit, l'histoire d'échelle et les frontières publiques des affirmations sans remplacer le registre théorématique du papier compact.
- **Papier 3. [Deriving the Particle Zoo from Observer Consistency](paper/deriving_the_particle_zoo_from_observer_consistency.pdf)** : surface de théorèmes et de frontières du secteur particules. Le porteur $A_5$ par faces et sommets ne sélectionne pas une famille physique ; ni $\mathbb Z_6$ ni le compte 24 ne fixe une masse ou un couplage. Les coordonnées W/Z et Higgs/top n'ont pas de carte source-pôle complète, les Yukawa des quarks sont sous-déterminés, le candidat neutrino à cycle pondéré échoue au profil corrélé NuFIT 6.1, et aucune masse physique non nulle ni matrice physique de mélange neutrino n'est émise côté source.
- **Papier 4. [Reality as a Consensus Protocol](paper/reality_as_consensus_protocol.pdf)** : mécanique du consensus fini entre patches. Il montre comment les observateurs comparent les enregistrements de recouvrement, appliquent des réparations, traitent les défauts et convergent vers des formes normales quotient quand les hypothèses de cutoff fixe sont satisfaites. Le résultat de consensus s'arrête aux formes normales quotient ; la géométrie lorentzienne et einsteinienne entre par la branche géométrique séparée du papier compact. L'opérateur de réparation est formulé sur le quotient physique, les lectures réparées sont invariantes sous les choix d'implémentation cachés, un porteur fini en couches témoigne de la reconstruction depuis la frontière, et un dispositif fini binaire donne des tests finis positifs/négatifs nets pour réparation et reconstruction de frontière. Le compagnon mathématique neutre prouve le critère générique entre sources, mais l'unicité physique à frontière identique exige que la frontière déclarée identifie le quotient cohérent ; la confluence depuis une même source et la vivacité sont des obligations distinctes.
- **Papier 5. [Federated Echosahedral Screen Microphysics](paper/screen_microphysics_and_observer_synchronization.pdf)** : surface finie du tamis conditionnel à douze ports, du porteur $A_5/C_3$, des enregistrements centraux et d'une réserve d'arête conditionnelle à six classes. Son identification au $\mathbb Z_6$ physique du Modèle Standard exige les reçus séparés de forme globale.
- **Papier 6. [Paradise as Fixed-Point Consensus](paper/paradise_as_fixed_point_consensus.pdf)** : synthèse spéculative de la couche de sens, hors du paquet de théorèmes de physique récupérés. Il lit la même mécanique OPH comme théorie de la continuation d'observateur, du paradis et de l'enfer comme environnements de continuation, de la résurrection comme continuation préservant les enregistrements, de la justice comme comptabilité tort-réparation et d'une boucle où des observateurs reconstruisent puis construisent la machinerie de continuation.

## Articles et notes supplémentaires

Ces textes soutiennent ou testent la pile centrale. Les éléments les plus
importants reçoivent plus de contexte ; les notes plus locales sont résumées
plus brièvement.

- **[Observation-Determined Normal Forms](extra/observable_normal_forms.pdf)** : mathématiques autonomes et neutres vis-à-vis du substrat pour les systèmes de contraintes et de réécriture. Le papier sépare la confluence depuis une même source, l'identification entre sources à partir d'observations protégées, la normalisation et la vivacité, ainsi que la réparabilité locale. Il ajoute des modules de stabilité résiduelle et d'observation inverse, des bornes de raffinement et de limite projective, le projecteur fini d'espérance conditionnelle pondérée avec un reçu matriciel non circulaire, et un artefact Lean dédié au sous-ensemble formalisé des théorèmes.
- **[Observer Patch Holography as a Strange-Loop Self-Simulation: The Claim Lattice and Its Closure Status](extra/compact_proof_of_oph.pdf)** : l'argument compact en faveur de l'OPH. Il énonce une fois les principes de la boucle étrange, parcourt les jambes théorématiques de la physique récupérée et présente chaque ligne numérique avec son statut de fermeture. Il ne donne un pull que lorsque les coordonnées théorique et expérimentale sont commensurables et que le modèle d'incertitude nécessaire existe. Il nomme aussi les artefacts qui portent la théorie : des certificats d'unicité et un registre de fermeture à zéro sous complétions en aveugle.
- **[Programme de falsification OPH](docs/OPH_FALSIFICATION_PROGRAM.md)** : liste d'élimination publique des affirmations OPH non cosmologiques arrivées à maturité. Elle nomme des modes d'échec durs, dont l'échec d'un reçu classique de porteur entièrement spécifié ou d'un reçu quantique de pôle complété séparément, la désintégration du proton médiée par jauge, les générations légères supplémentaires et les charges hors du réseau permis. Les affirmations sur les neutrinos et la cosmologie en sont exclues parce que leurs dérivations physiques sont immatures.
- **[The Fine-Structure Constant as an OPH Pixel Fixed Point](extra/fine_structure_constant_derivation.pdf)** : calcul de point fixe source pour la ligne de structure fine. Il sépare la valeur source OPH, la frontière empirique du point final à basse énergie, la provenance distincte de la racine source et du pixel de comparaison CODATA, et la correction QCD/hadronique restante.

Les autres fichiers de [`extra/`](extra) et [`docs/`](docs) sont des notes de
preuve, continuations conditionnelles, surfaces d'audit ou documents
d'ingénierie. Ils ne définissent pas le noyau récupéré. La note $\chi_\nu$,
l'action du secteur sombre, l'identité de transfert Yang--Mills, le crible de
vides de cordes, la note sur la cognition et les livres de matériel conservent
les portes ouvertes indiquées dans leurs propres frontières d'affirmation.

## Articles de cosmologie

La branche cosmologie vit dans [`cosmology/`](cosmology/README.md). Ses
papiers sont des surfaces de recherche en préparation, hors paquet de
publication. Leurs affirmations sont conditionnelles aux frontières OPH natives
de source, transfert et vraisemblance ; la machinerie FLRW peut servir de
comparaison, mais elle ne promeut pas à elle seule un résultat cosmologique
natif OPH.

Le papier sur le secteur sombre propose une action de condensat de charge de
réparation. Sa phase normale diluée se comporte comme une matière sans
pression, et sa phase condensée cubique donne la loi galactique profonde et la
relation de Tully--Fisher baryonique. L'action fournit aussi le courant, le
stress et le couplage à la source cohérente. Sa dérivation OPH, ses constantes,
sa loi constitutive complète, sa limite relativiste et ses reçus physiques
constituent un travail en cours. La branche ne fournit ni prédiction physique
fermée de matière noire ni cible cosmologique.

- **[Observer-Patch Holography and the Dark Matter Phenomenon](cosmology/oph_dark_matter_paper.pdf)** : action conditionnelle de condensat de charge de réparation. Elle dérive le bilan du courant de réparation, l'échelle de fond sans pression, la loi galactique profonde sphérique et une force cohérente respectant le bilan de quantité de mouvement. La dérivation OPH de l'action et les preuves physiques constituent un travail en cours.
- **[OPH Cosmology Data and Likelihood Contracts](cosmology/oph_cosmology_data_likelihood_contracts.pdf)** : artefacts de provenance source, reçus de non-utilisation des données, registre de comparaison sur données publiques, réducteurs agrégés, comparaisons de transfert de Boltzmann et protocoles de vraisemblance officiels. Ce sont des contrats d'éligibilité, pas des cibles verrouillées.

Les autres papiers de cosmologie sont des surfaces de dérivation de travail
indexées dans [`cosmology/README.md`](cosmology/README.md). Ils ne sont pas
promus depuis la page d'accueil tant que leurs cartes de source et de transfert
restent ouvertes.

## Articles sur des problèmes de physique

Les notes appliquées vivent dans
[`physics-problems/`](physics-problems/README.md). Ce dossier porte la liste
des articles, les résumés, les liens vers les résultats motivants, les
frontières de revendication et les notes d'ingestion OPH Sage. Les notes sont
en Markdown seulement et restent hors du pipeline de release des papiers, de
l'index web des papiers et des artefacts GitHub Release.

## Statut de preuve

La [preuve compacte de l'OPH](extra/compact_proof_of_oph.pdf) sépare les
théorèmes finis exacts, les branches physiques conditionnelles à des reçus, les
racines certifiées de cartes numériques déclarées et les cartes physiques
ouvertes. La compilation Lean vérifie le sous-ensemble fini déclaré. L'arbre
Lean plus large contient aussi trois signatures de réparation asynchrone
explicitement marquées par `sorry`, hors de ce sous-ensemble.

Le [registre de fermeture](docs/CLOSURE_LEDGER.md) consigne chaque carte
quantitative ouverte. L'OPH ne possède ni registre de cibles verrouillées, ni
file de préenregistrement, ni tableau de scores prospectif. La cosmologie, la
matière noire, les continuations de masses et les autres voies de lecture
ouvertes ne portent aucun verdict de falsification. Le
[programme de falsification](docs/OPH_FALSIFICATION_PROGRAM.md) couvre dix
surfaces mathématiques et cinq surfaces physiques de branche réalisée.

## Applications et matériel OMEGA

Une technologie OPH est un système borné de type observateur avec état local,
ports ou frontières, relecture, enregistrements, rétroaction ou réparation et
paquet de preuves public. Le programme matériel OMEGA teste des réalisations de
cette architecture. Les concepts d'énergie, de calcul, de cognition et de
contrôle de force restent des pistes d'ingénierie tant que leurs reçus de
vérification n'existent pas. Ils sont documentés sur
[omega.floatingpragma.io](https://omega.floatingpragma.io/), hors du paquet de
théorèmes de physique récupérée.

## Carte de dépendances

<p align="center">
  <a href="assets/prediction-chain.svg" target="_blank" rel="noopener noreferrer">
    <img src="assets/prediction-chain.svg" alt="Pile théorématique et de dérivation OPH" width="92%">
  </a>
</p>

<p align="center"><sub>La ligne principale OPH va des principes de la boucle étrange à la relativité, la structure de jauge, les particules et les observateurs. Les nœuds de théorèmes et les portes conditionnelles restent distincts. Cliquez pour ouvrir le SVG complet.</sub></p>

## Plus

- **Site officiel :** [floatingpragma.io/oph](https://floatingpragma.io/oph)
- **Page theory of everything :** [floatingpragma.io/oph/theory-of-everything](https://floatingpragma.io/oph/theory-of-everything)
- **Simulation :** [simulation.floatingpragma.io](https://simulation.floatingpragma.io) : explorateur interactif de mini-univers OPH montrant patches d'observateurs, relecture des recouvrements, réparation des incohérences, enregistrements et géométrie émergente.
- **Applications :** [omega.floatingpragma.io](https://omega.floatingpragma.io)
- **Blog :** [blog.floatingpragma.io](https://blog.floatingpragma.io/)
- **Livre :** [oph-book.floatingpragma.io](https://oph-book.floatingpragma.io)
- **Application d'étude guidée :** [learn.floatingpragma.io](https://learn.floatingpragma.io/)
- **Questions :** OPH Sage sur [Telegram](https://t.me/HoloObserverBot) ou [X](https://x.com/OphSage)

## Guide du dépôt

- **[`paper/`](paper)** : PDF, sources LaTeX et métadonnées de release.
- **[`book/`](book)** : source du livre OPH et PDF téléchargeable généré. Les
  notes de génération du PDF imprimable sont dans [`book/README.md`](book/README.md).
- **[`code/`](code)** : sorties calculatoires, surface particules et expériences.
- **[`docs/`](docs)** : notes de fermeture, falsification, preuve et politique.
- **[`assets/`](assets)** : schémas et figures publics.
- **[`extra/`](extra)** : papiers supplémentaires et continuations conditionnelles.
- **[`cosmology/`](cosmology)** : recherches préparatoires sur le secteur sombre et la cosmologie.
- **[`physics-problems/`](physics-problems)** : notes Markdown autonomes sur
  des problèmes de physique, pour lecture publique et ingestion par OPH
  Sage.

## OPH et les sciences

<p align="center">
  <a href="assets/oph_science_overlap_map_poster.png" target="_blank" rel="noopener noreferrer">
    <img src="assets/oph_science_overlap_map.svg" alt="Carte des sciences recouvertes par l'OPH, des grands domaines aux sous-domaines et aux zones d'application concrètes." width="100%">
  </a>
</p>

<p align="center"><sub>Carte domaine -> sous-domaine -> zone OPH couvrant les mathématiques, l'informatique, l'information et l'inférence, les systèmes complexes, la physique théorique, l'information quantique et les fondements de la mesure. Cliquez pour ouvrir le poster PNG complet.</sub></p>

## Licence et politique anti-brevet

Le matériel rédigé dans ce dépôt est sous licence
[CC BY-NC-SA 4.0](LICENSE), avec la
[convention OPH d'usage ouvert et d'anti-brevet](PATENTS.md) applicable aux
idées, implémentations, dispositifs, méthodes, applications, logiciels,
simulations et conceptions matérielles dérivés d'OPH.

L'OPH est publiée pour que les mathématiques, logiciels,
applications, dispositifs, conceptions matérielles, simulations, méthodes
d'ingénierie et implémentations expérimentales puissent être étudiés, testés,
implémentés, modifiés, déployés, fabriqués et partagés. Les travaux dérivés
d'OPH ne peuvent servir à créer des monopoles de brevet privés ou des
revendications de brevet qui restreignent la pratique de l'OPH par d'autres.

Voir [PATENTS.md](PATENTS.md) pour le texte canonique de la politique et les
mentions prêtes à publier sur les sites web.

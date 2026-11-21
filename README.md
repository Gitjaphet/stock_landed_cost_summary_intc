# INTC Landed Cost Summary

Module Odoo 19 qui ajoute un onglet **« Récapitulatif »** aux coûts logistiques (*landed costs*) : pour chaque produit d'un arrivage, on voit **combien coûte vraiment une pièce** une fois la douane, le transport et les autres frais ajoutés.

![Odoo 19](https://img.shields.io/badge/Odoo-19.0-714B67)
![Python](https://img.shields.io/badge/Python-3.11-3776AB)
![Inventory](https://img.shields.io/badge/Odoo-Inventory-875A7B)
![License](https://img.shields.io/badge/License-LGPL--3-blue)

## Le problème

En standard, l'onglet « Correction de valorisation » d'Odoo affiche **une ligne par produit et par frais**. Avec 10 produits et 3 frais, cela fait 30 lignes : impossible de lire rapidement le coût de revient d'une pièce.

## Ce que fait le module

Un nouvel onglet **« Récapitulatif »** affiche un tableau simple :

| Produit | Qté | Achat / pièce | Coût de revient / pièce | Douane / pièce | Transport / pièce | … | Total |
|---|---|---|---|---|---|---|---|

- **Une ligne par produit**, même si le produit apparaît dans plusieurs mouvements.
- **Une colonne par type de frais** (créée automatiquement selon les frais saisis).
- **Coût de revient / pièce** = prix d'achat + tous les frais, divisé par la quantité.
- Une ligne **« Total du lot »** en bas du tableau.
- Montants affichés dans la **devise de la société**.

Le tableau est calculé à l'affichage : rien n'est stocké en base et **aucune écriture comptable n'est modifiée**.

## Prérequis

| Élément | Détail |
|---|---|
| Odoo | 19.0 |
| Module requis | `stock_landed_costs` |

## Installation

```bash
# 1. Cloner le module dans le dossier des addons personnalisés
cd /chemin/vers/vos/addons
git clone https://github.com/Gitjaphet/stock_landed_cost_summary_intc.git

# 2. Ajouter ce dossier à addons_path dans odoo.conf, puis redémarrer Odoo

# 3. Installer le module (ou depuis Applications, après mise à jour de la liste)
python odoo-bin -c odoo.conf -d <base> -i stock_landed_cost_summary_intc --stop-after-init
```

## Utilisation

1. **Inventaire → Opérations → Coûts logistiques** : créer un coût logistique, choisir les réceptions et ajouter les frais (douane, transport…).
2. Cliquer sur **Calculer**.
3. Ouvrir l'onglet **« Récapitulatif »**.

## Structure du dépôt

```
stock_landed_cost_summary_intc/
├── models/stock_landed_cost.py         Regroupement par produit et construction du tableau
├── views/stock_landed_cost_views.xml   Onglet « Récapitulatif »
└── .github/workflows/deploy.yml        Déploiement automatique
```

## Déploiement

Chaque `push` sur `main` lance GitHub Actions (test → deploy) : le code est mis à jour sur le serveur, puis Odoo redémarre.

## Auteur

Développé par **Japhet Valeureux BEZANAKA** pour [INTC Madagascar](https://intc.mg).

Licence : LGPL-3.

# artificium_production_maintenance — Intégration Production-Maintenance SAPE

**Version :** 18.0.1.0  
**Auteur :** EURL ARTIFICIUM  
**Client :** SARL SAPE Messerghine  
**Catégorie :** Manufacturing/Integration  
**Licence :** LGPL-3  
**Cahier des charges couvert :** Module PRODUCTION + Module MAINTENANCE — Intégration et notifications automatiques

---

## 1. Objectif

Ce module répond aux exigences croisées des cahiers des charges **"Production"** et **"Maintenance"** qui requièrent :
- Des **notifications automatiques** au responsable production lors de maintenances préventives
- La gestion des **arrêts de production** liés aux interventions de maintenance
- Le **reporting des arrêts** par équipe, cause, et impact
- Des **KPI** de performance production-maintenance

---

## 2. Dépendances

| Module Odoo | Rôle |
|-------------|------|
| `base` | Modèles de base |
| `mrp` | Ordres de fabrication (`mrp.production`), ateliers (`mrp.workcenter`) |
| `maintenance` | Demandes de maintenance (`maintenance.request`), équipements |
| `mail` | Notifications email, activités, chatter |
| `hr` | Ressources humaines |

---

## 3. Modèles de Données

### 3.1 `production.stop` — Arrêt de Production (nouveau modèle)

| Champ | Type | Description |
|-------|------|-------------|
| `name` | Char | Référence automatique (séquence) |
| `state` | Selection | `draft` / `scheduled` / `in_progress` / `done` / `cancel` |
| `maintenance_request_id` | Many2one | Demande de maintenance liée |
| `equipment_id` | Many2one | Équipement concerné (obligatoire) |
| `production_order_id` | Many2one | Ordre de fabrication impacté |
| `production_team_id` | Many2one | Atelier/Équipe (mrp.workcenter) |
| `scheduled_date` | Datetime | Date programmée (obligatoire) |
| `actual_start_date` | Datetime | Début réel de l'arrêt |
| `actual_end_date` | Datetime | Fin réelle de l'arrêt |
| `duration` | Float | Durée planifiée (heures) |
| `actual_duration` | Float | Durée réelle calculée (heures) |
| `reason` | Selection | Motif : Maintenance préventive / Curative / Panne / Changement de série / Manque matière / Problème qualité / Autre |
| `reason_description` | Text | Description libre du motif |
| `impact_production` | Selection | Impact : Aucun / Mineur / Majeur / Critique |
| `responsible_id` | Many2one | Responsable |
| `maintenance_team_id` | Many2one | Équipe maintenance |
| `company_id` | Many2one | Société |
| `notes` | Text | Notes |

### 3.2 Extension `maintenance.request`

Champs ajoutés sur les demandes de maintenance Odoo :

| Champ | Type | Description |
|-------|------|-------------|
| `affects_production` | Boolean | Cette maintenance nécessite un arrêt production |
| `production_manager_id` | Many2one | Responsable production à notifier |
| `production_team_id` | Many2one | Atelier/Équipe concerné |
| `scheduled_production_stop` | Boolean | Arrêt programmé créé |
| `production_stop_duration` | Float | Durée estimée d'arrêt (heures) |
| `production_orders_ids` | Many2many | Ordres de fabrication affectés |
| `production_stop_id` | Many2one | Arrêt de production lié |
| `notification_sent` | Boolean | Notification déjà envoyée |
| `priority_level` | Selection | Faible / Moyenne / Haute / Critique |

### 3.3 Extension `maintenance.equipment`

Ajout d'informations production sur les équipements : atelier, criticité production, impact en cas de panne.

### 3.4 Extension `mrp.production`

Ajout de liens vers les demandes de maintenance et arrêts liés à un ordre de fabrication.

---

## 4. Fonctionnalités

### 4.1 Notification Automatique au Responsable Production

**Méthode `action_notify_production()`** sur `maintenance.request` :
1. Vérifie que `affects_production = True` et qu'un responsable production est défini
2. Envoie l'email via le template `email_template_maintenance_notification`
3. Crée une **activité** assignée au responsable production avec les détails de l'intervention
4. Marque `notification_sent = True`

**Déclenchement automatique :** lors de l'écriture de `schedule_date` sur une demande marquée `affects_production`.

### 4.2 Création d'un Arrêt de Production

**Méthode `action_schedule_production_stop()`** :
1. Crée un enregistrement `production.stop` lié à la demande de maintenance
2. Pré-remplit équipement, atelier, date programmée, durée
3. Notifie automatiquement le responsable production
4. Ouvre la fiche de l'arrêt créé

### 4.3 Cycle de Vie de l'Arrêt de Production

```
Brouillon → Programmé → En cours → Terminé
                ↓
             Annulé
```

- **`action_schedule()`** — Programme l'arrêt
- **`action_start()`** — Démarre (enregistre `actual_start_date`)
- **`action_done()`** — Termine (enregistre `actual_end_date`, calcule `actual_duration`)
- **`action_cancel()`** — Annule
- **`action_draft()`** — Remet en brouillon

### 4.4 Calcul de la Durée Réelle

`actual_duration` est calculé automatiquement : `(actual_end_date - actual_start_date)` en heures.

### 4.5 Template Email de Notification

Template `email_template_maintenance_notification` envoyé au responsable production avec :
- Nom de la maintenance
- Date planifiée
- Équipement concerné
- Durée estimée d'arrêt
- Lien vers la demande de maintenance

---

## 5. Vues et Menus

| Vue | Description |
|-----|-------------|
| Arrêts de Production | Liste et formulaire `production.stop` |
| Demandes Maintenance (étendu) | Onglet "Impact Production" ajouté |
| Formulaire Équipement (étendu) | Informations production ajoutées |
| Ordre de Fabrication (étendu) | Lien vers maintenances/arrêts |

**Menu principal :** Maintenance > Production-Maintenance > ...  
- Arrêts de Production  
- Demandes avec impact production  
- Tableau de bord KPI

---

## 6. Données Initiales

| Données | Description |
|---------|-------------|
| `email_templates.xml` | Template email notification responsable production |

---

## 7. Sécurité

| Groupe | Accès |
|--------|-------|
| `maintenance.group_equipment_manager` | Accès complet |
| `mrp.group_mrp_user` | Lecture |
| `mrp.group_mrp_manager` | Accès complet |

---

## 8. Conformité Cahier des Charges

| Exigence CdC | Module | Implémentée | Détail |
|--------------|--------|-------------|--------|
| Notification automatique au responsable production lors de maintenances préventives | PRODUCTION + MAINTENANCE | ✅ | `action_notify_production()` + email template + activité |
| Planification arrêts de production liés aux maintenances | PRODUCTION | ✅ | Modèle `production.stop` avec cycle de vie complet |
| Arrêts de production par équipe/cause | PRODUCTION | ✅ | Champs `reason`, `production_team_id`, `impact_production` |
| Reporting des arrêts (KPI, durées) | PRODUCTION | ✅ | `actual_duration`, filtres par équipe/cause/état |
| Gestion des interventions avec fiches détaillées | MAINTENANCE | ✅ | Extension `maintenance.request` |
| Intégration Production-Maintenance | MAINTENANCE | ✅ | Many2many `production_orders_ids` + `production_stop_id` |
| Reporting arrêts de production journalier par équipe et codes d'arrêt | QUALITÉ | ✅ | Vue liste filtrée par date/équipe/motif |

---

## 9. Installation

```bash
docker exec sapemesserghine-app odoo --stop-after-init -d sapemesserghine \
  -i artificium_production_maintenance \
  --addons-path=/mnt/extra-addons,/usr/lib/python3/dist-packages/odoo/addons
```

**Prérequis installés :** `mrp`, `maintenance`, `mail`

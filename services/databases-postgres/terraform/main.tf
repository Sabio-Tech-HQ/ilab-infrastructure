# --- New Master Superuser ---
resource "postgresql_role" "jthairu" {
  name      = "jthairu"
  login     = true
  password  = var.db_password
  superuser = true
}

# PACS database
resource "postgresql_database" "pacs" {
  name       = "pacs"
  owner      = "pacs"
}

# Airflow database - Updated owner to airflow
resource "postgresql_database" "airflow" {
  name       = "airflow"
  owner      = "airflow"
}

# Vitals database - Updated owner to vitals
resource "postgresql_database" "vitals" {
  name       = "vitals"
  owner      = "vitals"
}

locals {
  media_apps = ["radarr", "sonarr", "lidarr"]
  # Added app_users to manage the others via loop for uniformity
  app_users  = ["pacs", "airflow", "vitals"]
}

# Create App Users (pacs, airflow, vitals) with replication
resource "postgresql_role" "app_roles" {
  for_each    = toset(local.app_users)
  name        = each.key
  login       = true
  replication = true
  password    = var.app_db_passwords[each.key]
}

# Create Media Users with replication
resource "postgresql_role" "media_users" {
  for_each    = toset(local.media_apps)
  name        = each.key
  login       = true
  replication = true # Enabled per your requirement
  password    = var.media_dbs_password 
}

# Create Media Databases - Main DBs
resource "postgresql_database" "media_dbs_main" {
  for_each = toset(local.media_apps)
  name     = "${each.key}_main"
  owner    = postgresql_role.media_users[each.key].name
}

# Create Media Databases - Log DBs
resource "postgresql_database" "media_dbs_log" {
  for_each = toset(local.media_apps)
  name     = "${each.key}_log"
  owner    = postgresql_role.media_users[each.key].name
}


# Revoke connection rights from everyone except the owner and jthairu
resource "postgresql_grant" "revoke_public_access" {
  for_each    = toset(concat(
    ["pacs", "airflow", "vitals"],
    [for s in local.media_apps : "${s}_main"],
    [for s in local.media_apps : "${s}_log"]
  ))
  database    = each.value
  role        = "public"
  object_type = "database"
  privileges  = [] 

  # Force Terraform to wait for the database to exist
  depends_on = [
    postgresql_database.pacs,
    postgresql_database.airflow,
    postgresql_database.vitals,
    postgresql_database.media_dbs_main,
    postgresql_database.media_dbs_log
  ]
}
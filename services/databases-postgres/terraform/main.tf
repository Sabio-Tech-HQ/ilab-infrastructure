# --- New Master Superuser ---
resource "postgresql_role" "jthairu" {
  name      = "jthairu"
  login     = true
  password  = var.db_password
  superuser = true
}

resource "postgresql_role" "vaultwarden" {
  name     = "vaultwarden"
  login    = true
  password = var.vaultwarden_db_password
}

resource "postgresql_database" "vaultwarden" {
  name  = "vaultwarden"
  owner = postgresql_role.vaultwarden.name
}



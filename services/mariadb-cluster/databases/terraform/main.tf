# --- MariaDB Logical Resources (Databases & Users) ---

resource "mysql_database" "pacs" {
  name                  = "pacs"
  default_character_set = "utf8mb4"
  default_collation     = "utf8mb4_general_ci"
}

resource "mysql_user" "pacs" {
  user               = "pacs"
  host               = "10.10.10.%"
  plaintext_password = var.pacs_password
}

resource "mysql_grant" "pacs_pacs" {
  user       = mysql_user.pacs.user
  host       = mysql_user.pacs.host
  database   = mysql_database.pacs.name
  privileges = ["ALL PRIVILEGES"]
}

resource "mysql_user" "jthairu" {
  user               = "jthairu"
  host               = "10.10.10.%"
  plaintext_password = var.pacs_password
}

resource "mysql_grant" "jthairu_pacs" {
  user       = mysql_user.jthairu.user
  host       = mysql_user.jthairu.host
  database   = mysql_database.pacs.name
  privileges = ["ALL PRIVILEGES"]
}
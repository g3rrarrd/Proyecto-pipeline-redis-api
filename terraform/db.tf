resource "azurerm_postgresql_flexible_server" "pgserver" {
  name = "serverpg-exp-${var.project}-${var.enviroment}"
  location = var.location_db
  resource_group_name = azurerm_resource_group.proyecto2.name
  version = "14"

  administrator_login = var.sql_user
  administrator_password = var.password_sql

  sku_name = "B_Standard_B1ms"
  storage_mb = 32768
  backup_retention_days = 7
  geo_redundant_backup_enabled = false

  zone = "1"
  tags = var.tags
}

resource "azurerm_postgresql_flexible_server_database" "db-pipeline" {
  name = "db-exp-${var.project}-${var.enviroment}"
  server_id = azurerm_postgresql_flexible_server.pgserver.id
  
  charset = "UTF8"
  collation = "en_US.utf8"

  
}
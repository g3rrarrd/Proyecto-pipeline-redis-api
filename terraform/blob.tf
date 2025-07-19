resource "azurerm_storage_account" "storage" {
  name = "stblb${var.project}${var.enviroment}"
  resource_group_name = azurerm_resource_group.proyecto2.name
  location = var.location
  account_tier = "Standard"
  account_replication_type = "LRS"

  tags = var.tags
}

resource "azurerm_storage_container" "blb_container" {
  name = "blbcontainer-${var.project}-${var.enviroment}"
  storage_account_id = azurerm_storage_account.storage.id
  container_access_type = "private"
  
}
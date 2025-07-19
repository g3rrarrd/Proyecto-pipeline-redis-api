resource "azurerm_container_registry" "container_registry" {
  name                = "acrexp${var.project}${var.enviroment}"
  resource_group_name = azurerm_resource_group.proyecto2.name
  location            = var.location
  sku                 = "Basic"

  admin_enabled = true

  tags = var.tags
  
  
}
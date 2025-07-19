resource "azurerm_redis_cache" "redis_cache" {
  name                = "redis-${var.project}-${var.enviroment}"
  location            = var.location
  resource_group_name = azurerm_resource_group.proyecto2.name
  capacity            = 1
  family              = "C"
  sku_name            = "Basic"
  
  tags = var.tags
  
}
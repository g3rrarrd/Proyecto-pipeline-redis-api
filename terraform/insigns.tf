resource "azurerm_application_insights" "app_insights" {
  name                = "appinsights-${var.project}-${var.enviroment}"
  location            = var.location
  resource_group_name = azurerm_resource_group.proyecto2.name
  application_type    = "web"

  tags = var.tags
  
}
resource "azurerm_data_factory" "etl" {
  name = "df-exp-${var.project}-${var.enviroment}"
  location = var.location
  resource_group_name = azurerm_resource_group.proyecto2.name 
}
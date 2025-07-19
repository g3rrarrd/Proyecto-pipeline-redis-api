resource "azurerm_service_plan" "sp-pipeline" {
  name = "sp-${var.project}-${var.enviroment}"
  location = var.location
  resource_group_name = azurerm_resource_group.proyecto2.name
  sku_name = "F1"
  os_type = "Linux"

  tags = var.tags
}

resource "azurerm_linux_web_app" "webapp" {
  name = "webapp-${var.project}-${var.enviroment}"
  location = var.location
  resource_group_name = azurerm_resource_group.proyecto2.name
  service_plan_id = azurerm_service_plan.sp-pipeline.id

  site_config {
    always_on = false
    application_stack {
      docker_registry_url = "https://index.docker.io"
      docker_image_name = "nginx:latest"
    }
  }

  app_settings = {
    WEBSITES_PORT = "80"
  }

  tags = var.tags
}
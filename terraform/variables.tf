variable "subscription_id" {
    type = string
    description = "The Azure subscription ID"
}

variable "location" {
    type = string
    description = "The location to delpoy the resources"
    default = "EastUS"
}

variable "location_db" {
    type = string
    description = "The location to delpoy the resources"
    default = "CentralUS"
}

variable "project" {
    type = string
    description = "The Name of the project"
    default = "pipeline"
}

variable "enviroment" {
    type = string
    description = "The type of enviroment"
    default = "dev"
}

variable "tags" {
    type = map(string)
    description = "The tags of the project"
    default = {
      enviroment = "dev",
      date = "Jul-2025",
      createdBy = "Terraform"
    }
}

variable "sql_user" {
  type = string
  description = "Uer of sql login"
}

variable "password_sql" {
  type = string
  description = "Password of sql login"
}
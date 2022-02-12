terraform {
  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 2.13.0"
    }
  }
}

variable "selenium_webdriver_port" {
  description = "port to listen on host for selenium webdriver communication"
  type        = string
  default     = "4444"
}

variable "selenium_chrome_version" {
  description = "exact tagged vresion of chrome to use, see https://hub.docker.com/r/selenium/standalone-chrome/tags for options"
  type        = string
  default     = "latest"
}

provider "docker" {}

resource "docker_image" "standalone-chrome" {
  name         = "selenium/standalone-chrome:latest"
  keep_locally = false
}

resource "docker_container" "standalone-chrome" {
  image = docker_image.standalone-chrome.latest
  name  = "standalone-chrome"
  ports {
    internal = 4444
    external = var.selenium_webdriver_port
  }
}

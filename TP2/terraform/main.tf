# Configure the Microsoft Azure Provider
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~>2.0"
    }
  }
}
provider "azurerm" {
  features {}
}

# Create a resource group if it doesn't exist
resource "azurerm_resource_group" "resource_group" {
  name     = "${var.name_prefix}resource_group"
  location = var.resources_location

  tags = {
    environment = var.environement_name
  }
}

# Create virtual network
resource "azurerm_virtual_network" "virtual_network" {
  name                = "${var.name_prefix}virtual_network"
  address_space       = ["10.0.0.0/16"]
  location            = var.resources_location
  resource_group_name = azurerm_resource_group.resource_group.name

  tags = {
    environment = var.environement_name
  }
}

# Create subnet
resource "azurerm_subnet" "subnet" {
  name                 = "${var.name_prefix}subnet"
  resource_group_name  = azurerm_resource_group.resource_group.name
  virtual_network_name = azurerm_virtual_network.virtual_network.name
  address_prefixes     = ["10.0.1.0/24"]
}

# Create public IPs
resource "azurerm_public_ip" "public_ip" {
  name                = "${var.name_prefix}public_ip"
  location            = var.resources_location
  resource_group_name = azurerm_resource_group.resource_group.name
  allocation_method   = "Dynamic"

  tags = {
    environment = var.environement_name
  }
}

# Create Network Security Group and rule
resource "azurerm_network_security_group" "security_group" {
  name                = "${var.name_prefix}security_group"
  location            = var.resources_location
  resource_group_name = azurerm_resource_group.resource_group.name

  security_rule {
    name                       = "SSH"
    priority                   = 1001
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "Tcp"
    source_port_range          = "*"
    destination_port_range     = "22"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    environment = var.environement_name
  }
}

# Create network interface
resource "azurerm_network_interface" "network_interface" {
  name                = "${var.name_prefix}network_interface"
  location            = var.resources_location
  resource_group_name = azurerm_resource_group.resource_group.name

  ip_configuration {
    name                          = "network_interface_configuration"
    subnet_id                     = azurerm_subnet.subnet.id
    private_ip_address_allocation = "Dynamic"
    public_ip_address_id          = azurerm_public_ip.public_ip.id
  }

  tags = {
    environment = var.environement_name
  }
}

# Connect the security group to the network interface
resource "azurerm_network_interface_security_group_association" "nic_sg_assoc" {
  network_interface_id      = azurerm_network_interface.network_interface.id
  network_security_group_id = azurerm_network_security_group.security_group.id
}

# Create (and display) an SSH key
resource "tls_private_key" "ssh_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Create virtual machine
resource "azurerm_linux_virtual_machine" "hadoop_spark_vm" {
  name                  = "${var.name_prefix}hadoop_spark_vm"
  location              = var.resources_location
  resource_group_name   = azurerm_resource_group.resource_group.name
  network_interface_ids = [azurerm_network_interface.network_interface.id]
  size                  = var.vm_size

  os_disk {
    name                 = "${var.name_prefix}hadoop_spark_vm_disk"
    caching              = "ReadWrite"
    storage_account_type = "StandardSSD_LRS"
  }

  # https://github.com/Azure/azure-cli/issues/13320#issuecomment-669733537
  source_image_reference {
    publisher = "canonical"
    offer     = "0001-com-ubuntu-server-focal"
    sku       = "20_04-lts"
    version   = "latest"
  }

  computer_name                   = "hadoop-spark-vm"
  admin_username                  = "azureuser"
  disable_password_authentication = true

  admin_ssh_key {
    username   = "azureuser"
    public_key = tls_private_key.ssh_key.public_key_openssh
  }

  tags = {
    environment = var.environement_name
  }
}
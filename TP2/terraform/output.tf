output "tls_private_key" {
  value     = tls_private_key.ssh_key.private_key_pem
  sensitive = true
}

output "public_ip_address" {
  value = azurerm_linux_virtual_machine.hadoop_spark_vm.public_ip_address
}


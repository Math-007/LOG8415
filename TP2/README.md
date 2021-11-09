# TP2

## Terraform

### Create VM:
```bash
cd terraform
az login
terraform init
terraform apply
```

### SSH in VM
```bash
terraform output -raw tls_private_key > key.pem
chmod 400 key.pem
ip=$(terraform output -raw public_ip_address)
ssh azureuser@$ip -i key.pem
```

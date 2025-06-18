terraform {
  backend "s3" {
    bucket = ""
    key    = ""
    region = ""
  }
}

provider "aws" {
  region = "us-east-1"
}

# Generate a new SSH key pair
resource "tls_private_key" "ec2_key" {
  algorithm = "RSA"
  rsa_bits  = 4096
}

# Create AWS key pair from generated key
resource "aws_key_pair" "deployer" {
  key_name   = "generated-key"
  public_key = tls_private_key.ec2_key.public_key_openssh
}

# Security Group for RDS
resource "aws_security_group" "db_sg" {
  name        = "db-sg"
  description = "Security group for RDS PostgreSQL instance"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [aws_security_group.app_sg.id]
    description = "PostgreSQL access from EC2 app server"
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }
}

# RDS DB
resource "aws_db_instance" "mydb" {
  identifier          = "myapp-db"
  engine              = "postgres"
  instance_class      = "db.t3.micro"
  allocated_storage   = 20
  db_name             = var.db_name_dev
  username            = var.db_user_dev
  password            = var.db_password_dev
  skip_final_snapshot = true
  publicly_accessible = false
  # Security groups
  vpc_security_group_ids = [aws_security_group.db_sg.id]

}

# Security Group for EC2
resource "aws_security_group" "app_sg" {
  name = "app-sg"

  ingress {
    from_port = 22
    to_port   = 22
    protocol  = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # SSH
  }

  egress {
    from_port = 0
    to_port   = 0
    protocol  = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "app" {
  ami           = "ami-0f88e80871fd81e91"
  instance_type = "t2.micro"
  key_name      = aws_key_pair.deployer.key_name
  vpc_security_group_ids = [aws_security_group.app_sg.id]

  tags = {
    Name = "myapp-ec2"
  }

  user_data = <<-EOF
              #!/bin/bash
              yum update -y
              yum install -y docker git
              service docker start
              usermod -a -G docker ec2-user
              chkconfig docker on
              dnf install postgresql15 -y
              sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
              sudo chmod +x /usr/local/bin/docker-compose
              EOF
}

# Outputs
output "ec2_ip" {
  value = aws_instance.app.public_ip
}

output "rds_endpoint" {
  value = aws_db_instance.mydb.address
}

output "private_key_pem" {
  value     = tls_private_key.ec2_key.private_key_pem
  sensitive = true
}
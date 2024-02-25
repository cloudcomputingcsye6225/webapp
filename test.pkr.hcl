packer {
  required_plugins {
    googlecompute = {
      source  = "github.com/hashicorp/googlecompute"
      version = ">= 1.0.0"
    }
  }
}

variable   "project_id" {
  type        = string
  description = "Your project id"
  default     = "packer-demo-project-414723"
}

variable "credentials_file" {
  type        = string
  description = "Your service account credentials in JSON format"
  default     = null
}

source "googlecompute" "google-custom-image" {
  project_id          = var.project_id
  source_image_family = "centos-stream-8"
  image_name          = "custom-image"
  image_family        = "custom-image-family"
  zone                = "us-central1-a"
  ssh_username        = "packer"
  use_internal_ip     = false
  credentials_file    = var.credentials_file
}

build {
  sources = ["source.googlecompute.google-custom-image"]

  provisioner "file" {
    source      = "./webapp.zip"
    destination = "/home/packer/"
  }

  provisioner "shell" {
    inline = [
      "sudo groupadd csye6225",
      "sudo useradd -m -s /bin/false -G csye6225 csye6225 -g csye6225",
      "sudo chown csye6225:csye6225 /home/packer/webapp.zip",
      "sudo mv /home/packer/webapp.zip /home/csye6225/",
      "sudo yum install -y unzip",
      "sudo -u csye6225 bash -c 'cd /home/csye6225/ && unzip webapp.zip && rm webapp.zip && chmod +x *.sh'"
    ]
  }
  provisioner "shell" {
    environment_vars = [
      "MYSQL_USER=advaith",
      "MYSQL_PASSWORD=helloworld",
      "MYSQL_DATABASE=mydb",
      "MYSQL_HOST=localhost",
      "MYSQL_PORT=3306"
    ]
    inline = [
      "sudo /home/csye6225/update_libraries_centos.sh",
      "sudo -E /home/csye6225/create_database_centos.sh",
      "sudo /home/csye6225/disable_selinux.sh"
    ]
  }
  provisioner "shell" {
    environment_vars = [
      "MYSQL_USER=advaith",
      "MYSQL_PASSWORD=helloworld",
      "MYSQL_DATABASE=mydb",
      "MYSQL_HOST=localhost",
      "MYSQL_PORT=3306"
    ]
    inline = [

      "sudo cp /home/csye6225/csye6225.service /etc/systemd/system/",
      "sudo chown root:root /etc/systemd/system/csye6225.service",
      "sudo chmod 744 /etc/systemd/system/csye6225.service",
      "sudo -u csye6225 bash -c 'cd /home/csye6225/ && python3 -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt --no-cache-dir'",
      "sudo setenforce 0",
      "sudo systemctl daemon-reload",
      "sudo systemctl start csye6225",
      "sudo systemctl enable csye6225",
      "sudo systemctl status csye6225",
      "journalctl -xe"
    ]
  }

}

## Documentations
# https://registry.terraform.io/providers/hashicorp/google/latest/docs
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/compute_instance
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/storage_bucket
# https://registry.terraform.io/providers/hashicorp/google/latest/docs/resources/bigquery_dataset
# https://registry.terraform.io/providers/apache/airflow/latest/docs/resources/connection
# https://registry.terraform.io/providers/DrFaust92/airflow/latest

# Define the required providers
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.15.0"
    }
    airflow = {
      source  = "DrFaust92/airflow"
      version = "0.14.0"
    }
  }
}

# Define the provider
provider "google" {
  credentials = file(var.credentials_path)
  project     = var.project_name
  region      = var.gcp_region
}



# Create the VM instance
resource "google_compute_instance" "parma-elt-vm" {
  name         = var.gcp_vm_name
  machine_type = var.gcp_vm_machine_type
  zone         = var.gcp_vm_zone
  boot_disk {
    initialize_params {
      image = var.gcp_vm_image
      size  = var.gcp_vm_size
    }
  }
  network_interface {
    network = var.gcp_vm_network
    access_config {
    }
  }
}

# Install Python Anaconda on the VM
resource "null_resource" "install_anaconda" {
  depends_on = [google_compute_instance.parma-elt-vm]

  connection {
    type        = var.connection_type
    user        = file(var.ssh-username)
    private_key = file(var.ssh-private-key)
    host        = google_compute_instance.parma-elt-vm.network_interface[0].access_config[0].nat_ip
  }

  provisioner "remote-exec" {
    inline = [
      "cd /tmp",
      "curl https://repo.anaconda.com/archive/Anaconda3-2020.02-Linux-x86_64.sh --output anaconda.sh",
      "sha256sum anaconda.sh",
      "bash anaconda.sh -b -p $HOME/anaconda3", // Install Anaconda into the specified directory
      "export PATH=\"$HOME/anaconda3/bin:$PATH\"", // Add Anaconda to the PATH temporarily for this session
      "conda --version"
    ]
  }
}


# Install Docker to VM Ubuntu 20.04
resource "null_resource" "install_docker" {
    depends_on = [google_compute_instance.parma-elt-vm, null_resource.install_anaconda]

    connection {
      type        = var.connection_type
      user        = file(var.ssh-username)
      private_key = file(var.ssh-private-key)
      host        = google_compute_instance.parma-elt-vm.network_interface[0].access_config[0].nat_ip
    }

    provisioner "remote-exec" {
      inline = [
        "sudo apt-get update",
        "sudo apt-get install -y apt-transport-https ca-certificates curl software-properties-common",
        "curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg",
        "echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu focal stable' | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null",
        "sudo apt-get update",
        "sudo apt-get install -y docker-ce docker-ce-cli containerd.io",
        "sudo systemctl start docker",
        "sudo systemctl enable docker",
        "sudo usermod -aG docker ${file(var.ssh-username)}",
        "docker --version"
      ]
    }
}

# Install Docker Compose to VM Ubuntu 20.04
resource "null_resource" "install_docker_compose" {
    depends_on = [google_compute_instance.parma-elt-vm, null_resource.install_docker]

    connection {
      type        = var.connection_type
      user        = file(var.ssh-username)
      private_key = file(var.ssh-private-key)
      host        = google_compute_instance.parma-elt-vm.network_interface[0].access_config[0].nat_ip
    }

    provisioner "remote-exec" {
      inline = [
        "sudo curl -L https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose",
        "sudo chmod +x /usr/local/bin/docker-compose",
        "docker-compose --version"
      ]
    }
}

# Run the Docker Compose file in the VM
resource "null_resource" "run_docker_compose" {
  depends_on =  [null_resource.install_docker, null_resource.install_docker_compose]

  connection {
    type        = var.connection_type
    user        = file(var.ssh-username)
    private_key = file(var.ssh-private-key)
    host        = google_compute_instance.parma-elt-vm.network_interface[0].access_config[0].nat_ip
  }

    provisioner "remote-exec" {
      inline = [
        "mkdir -p airflow-parma",
        "curl -LfO 'https://airflow.apache.org/docs/apache-airflow/2.8.1/docker-compose.yaml' && mv docker-compose.yaml airflow-parma/",
        "cd airflow-parma",
        "echo AIRFLOW_UID=50000 >> .env",
        "sudo systemctl enable docker",
        "sudo systemctl start docker",
        "sudo docker-compose -f /home/${file(var.ssh-username)}/airflow-parma/docker-compose.yaml up -d"]
    }
  }



# Install Terraform on GCP VM
resource "null_resource" "install_terraform" {
  depends_on = [google_compute_instance.parma-elt-vm, null_resource.install_docker, null_resource.install_docker_compose, null_resource.run_docker_compose]

  connection {
    type        = var.connection_type
    user        = file(var.ssh-username)
    private_key = file(var.ssh-private-key)
    host        = google_compute_instance.parma-elt-vm.network_interface[0].access_config[0].nat_ip
  }

  provisioner "remote-exec" {
    inline = [
      "sudo snap install terraform --classic",
      "terraform --version"
    ]
  }
}


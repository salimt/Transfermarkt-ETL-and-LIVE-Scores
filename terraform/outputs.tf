output "external_ip" {
  value       = google_compute_instance.parma-elt-vm.network_interface[0].access_config[0].nat_ip
  description = "The external IP address"
}
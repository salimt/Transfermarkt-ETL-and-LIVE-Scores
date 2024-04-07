# Transfermarkt Analytics Pipeline (Extract, Load, Transform)

## Overview

This project implements an ELT (Extract, Load, Transform) pipeline for processing football data from Transfermarkt using various technologies such as Python, Airflow, GCP Storage Bucket, GCP BigQuery, dbt, GCP VM, Terraform and Docker.

## Pipeline Diagram
![](https://i.imgur.com/g2yi9Qm.jpeg)

## Airflow Tasks
![](https://i.imgur.com/rxfQgk9.png)

## Technologies Used
- **Python:** Used for web scraping, making API calls, and general purpose scripting.
- **Airflow:** Orchestrating and scheduling the pipeline tasks.
- **GCP Storage Bucket:** Storing raw and intermediate data.
- **GCP BigQuery:** Data warehouse for storing transformed data and performing analytics.
- **GCP VM:** Utilized for hosting Docker containers running Airflow, as well as for provisioning BigQuery datasets and buckets using Terraform.
- **Terraform:** Infrastructure as Code (IaC) for provisioning GCP resources.
- **Docker:** Containerization for easier deployment and portability.


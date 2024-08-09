# Transfermarkt Analytics Pipeline (ELT: Extract, Load, Transform)

## Overview

This project implements a comprehensive ELT (Extract, Load, Transform) pipeline for processing football data sourced from Transfermarkt. The pipeline utilizes various technologies such as Python, Airflow, Google Cloud Platform (GCP) services including Storage Bucket and BigQuery, as well as additional tools such as dbt, Docker, Terraform, and GCP Virtual Machines. It also includes dbt for machine learning and performance analysis. This allows for predictive modeling using algorithms like linear regression and XGBoost, enabling insights into player values and market trends. Additionally, dbt facilitates performance evaluation to optimize pipeline efficiency and productivity, enhancing data-driven decision-making in football analytics. By orchestrating these technologies together, the pipeline enables the extraction of football data, its transformation into structured datasets, and its loading into a BigQuery data warehouse for advanced analytics and reporting.

## Data

The pipeline processes three main types of football data from Transfermarkt:

- **Player Profiles:** This dataset contains approximately _131,000_ rows and provides detailed information about football players.
  
- **Player Market History:** With around _635,000_ rows, this dataset tracks the market value history of players over time, providing insights into trends and fluctuations in player valuations.
  
- **Player Stats:** This dataset comprises approximately _1,600,000_ rows and includes various statistical metrics related to player performance on the field, such as goals scored, assists, and minutes played.

## Pipeline Diagram

![Pipeline Diagram](https://i.imgur.com/g2yi9Qm.jpeg)

The diagram illustrates the flow of data through the ELT pipeline, from data extraction to loading into BigQuery. Each component in the pipeline plays a specific role in processing the data and facilitating its transformation.

## Airflow Tasks

![Airflow Tasks](https://i.imgur.com/rxfQgk9.png)

The Airflow DAG (Directed Acyclic Graph) orchestrates the pipeline tasks, breaking down the process into individual steps that are executed in a coordinated manner. Each task performs a specific function, such as data extraction, transformation, or loading, contributing to the overall data processing workflow.

## Technologies Used

The following technologies are employed in the implementation of the pipeline:

- **Python:** Utilized for asynchronous web scraping, making API calls to Transfermarkt, and general-purpose scripting for data processing.
  
- **Airflow:** Orchestrates and schedules the pipeline tasks, ensuring the smooth execution of each step in the data processing workflow.
  
- **GCP Storage Bucket:** Stores raw and intermediate data generated during the extraction and transformation phases of the pipeline.
  
- **GCP BigQuery:** Serves as the data warehouse for storing transformed data and performing advanced analytics using SQL queries.
  
- **GCP Virtual Machines:** Hosts Docker containers running Airflow and provides infrastructure for executing pipeline tasks.
  
- **Terraform:** Implements Infrastructure as Code (IaC) for provisioning GCP resources, ensuring consistency and reproducibility.
  
- **Docker:** Enables containerization of pipeline components for easier deployment, scalability, and portability across different environments.

- **dbt (Data Build Tool):** Used for data transformation and modeling, allowing for the creation of structured datasets, business logic layers, and predictive analytics. Linear regression and XGBoost models are employed for player value analysis and prediction.


## Contributors

- salimt

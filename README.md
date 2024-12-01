# Backend Service

This backend service is designed for managing user authentication, organization membership, cluster resource allocation, and deployment scheduling. It optimizes deployment priority, resource utilization, and successful deployment rates.

---

## Table of Contents

1. [Features](#features)  
2. [Prerequisites](#prerequisites)  
3. [Setup and Installation](#setup-and-installation)  
4. [Running the Service with Docker](#running-the-service-with-docker)  
5. [API contracts](#api-contracts)  
6. [UML and Sequence Diagrams](#uml-and-sequence-diagrams)  
7. [Run Tests](#run-tests)

---

## Features
- User Authentication (JWT-based)  
- Organization Membership Management  
- Cluster Resource Allocation  
- Deployment Scheduling  

---

## Prerequisites
- Docker & Docker Compose  
- Python 3.8+ 

---

## Setup and Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/vishalsiwach59/Backend-Service.git
   cd backend-service
   ```
2. activate virtualenv:
    ```bash
    source venv/bin/activate 
    ```

## Running the Service with Docker

1. setup db, redis, worker and service
    ```bash
    docker-compose up -d 
    ```
2. setup tables and RBAC roles
    ```bash
    python create_tables.py
    ```
3. service is running at localhost:5000

## API contracts

https://docs.google.com/document/d/199BJX3POZlvBxu-pt-N9QC_RQj2iLZHPO77tlXEhRuk/edit?usp=sharing


## UML and Sequence Diagrams
![Untitled (1)](https://github.com/user-attachments/assets/beef9fa3-79c5-42d4-9b69-0b7cbf13bb6f)

<img width="914" alt="Screenshot 2024-12-01 at 7 42 19 PM" src="https://github.com/user-attachments/assets/65e221bb-ea04-48ea-a7e8-9f512e197ebe">


## Run Tests
1. run tests with pytest
    ```bash
    pytest servicetests
    ```
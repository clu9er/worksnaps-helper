
# Worksnaps Helper

## Project Description
Worksnaps Helper is a project designed to quickly retrieve and generate reports on projects from the Worksnaps platform. It leverages Docker to containerize the application and ensures that all dependencies are managed seamlessly. The tool simplifies the process of generating detailed project summaries, helping users track their project activities more efficiently.

## Prerequisites
To run the Worksnaps Helper project, you need to have the following installed:

1. **Docker**: Docker is required to create and manage containers for the project. You can download Docker from [Docker's official website](https://www.docker.com/products/docker-desktop) and follow the installation instructions for your operating system.

## Running the Project
To start the project, use Docker Compose to build and run the containers in detached mode. Execute the following command in the root directory of the project:

```sh
docker-compose up -d
```

This command will:

- Build the Docker images as specified in the `docker-compose.yml` file.
- Start the containers defined in the configuration.
- Run the application in detached mode (in the background).

By following these steps, you will have the Worksnaps Helper Bot running and accessible for generating project reports.

# Use the official Docker Hub Postgres image
FROM postgres

# Set the working directory
WORKDIR /var/lib/postgresql/data

# Set the required environment variable
ENV POSTGRES_PASSWORD=@irBnbRegulation

# Expose the port postgres runs on
EXPOSE 5432

# Copy the local file to the container's filesystem
COPY . .

# Use the official Docker Hub Postgres image
FROM postgres:latest



# Copy the local file to the container's filesystem
COPY airbnb_db_creator.sql /docker-entrypoint-initdb.d/

# Expose the port postgres runs on
EXPOSE 5432

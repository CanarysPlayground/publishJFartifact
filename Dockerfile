# Dockerfile
FROM openjdk:17-alpine
COPY target/my-app-1.0-SNAPSHOT.jar /app/my-app.jar
ENTRYPOINT ["java", "-jar", "/app/my-app.jar"]

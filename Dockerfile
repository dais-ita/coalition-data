FROM maven:3.5

# Get latest CE-Store
RUN git clone https://github.com/ce-store/ce-store

# Install dependencies
WORKDIR ce-store
RUN mvn install

# Copy CE code and configuration
COPY dais-ce src/main/webapp/ce/dais
COPY local_projects.json src/main/webapp/ui/json/local_projects.json

CMD ["mvn", "tomcat:run"]
# Image for a NYU Lab development environment
FROM rofrano/nyu-devops-base:sp25

# Set up the Python development environment
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN sudo python -m pip install --upgrade pip pipenv && \
    sudo pipenv install --system --dev

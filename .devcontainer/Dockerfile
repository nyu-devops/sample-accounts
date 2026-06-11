##################################################
# Image for a Python 3 development environment
##################################################
# cSpell: disable
FROM quay.io/rofrano/nyu-devops-base:su26

# Set up the Python development environment
WORKDIR /app
COPY Pipfile Pipfile.lock ./
RUN sudo python -m pip install --upgrade pip pipenv && \
    sudo pipenv install --system --dev

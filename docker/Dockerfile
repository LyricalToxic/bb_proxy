FROM python:3.11


RUN apt-get update && apt-get install -y curl wget gnupg2 systemd gettext-base cron vim

SHELL ["/bin/bash", "-l", "-c"]

RUN /usr/local/bin/python -m pip install --upgrade pip &&\
    curl -sSL https://install.python-poetry.org | python3 - \
#    && source $HOME/.poetry/env \
    &&  echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
RUN pip install plumbum



RUN set -eu && \
    wget -qO- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.1/install.sh | bash && \
    export NVM_DIR="$HOME/.nvm" && \
    [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh" && \
    [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion" && \
    nvm install 13.6.0 && \
    npm install -g pm2@5.0.0


ENTRYPOINT ["/bin/bash", "-l", "-c", "python /home/app/docker/setup.py"]
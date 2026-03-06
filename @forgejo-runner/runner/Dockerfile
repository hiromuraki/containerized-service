FROM code.forgejo.org/forgejo/runner:12

COPY ./command.sh /bin/command.sh

USER root
RUN chmod +x /bin/command.sh

USER 1000
FROM debian:bullseye

# cabal and mueval
RUN apt-get update && apt-get install -y cabal-install && apt-get clean
RUN cabal update
# Runtime dependencies which aren't installed along with mueval itself
RUN cabal install --lib containers mtl hint random show simple-reflect QuickCheck
RUN cabal install mueval
ENV PATH=$PATH:/root/.cabal/bin

# python 3
RUN apt-get install -y python3
COPY ./mueffler.py /usr/bin/mueffler.py

CMD [ "mueffler.py" ]

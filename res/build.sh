NAME=$(pwd | rev | cut -d/ -f1 | rev).tar.gz

tar -czvf $NAME .

AUDIO=$1
PATH=/var/www/django/ipp
SYSPATH=/opt/envs/ipp/bin

$SYSPATH/python3 $PATH/transcribir.py $AUDIO



webservice --backend=kubernetes python3.10 shell
mkdir -p $HOME/www/python
python3 -m venv $HOME/www/python/venv
source $HOME/www/python/venv/bin/activate
pip install --upgrade pip wheel
exit
webservice --backend=kubernetes python3.11 start
"""Init file with common constants and functions for client and server files."""

from io import StringIO
import cowsay
import os

jgsbat = cowsay.read_dot_cow(StringIO("""
$the_cow = <<EOC;
    ,_                    _,
    ) '-._  ,_    _,  _.-' (
    )  _.-'.|\\--//|.'-._  (
     )'   .'\\/o\\/o\\/'.   `(
      ) .' . \\====/ . '. (
       )  / <<    >> \\  (
        '-._/``  ``\\_.-'
  jgs     __\\'--'//__
         (((""`  `"")))
EOC
"""))

weapons = {'sword': 10, 'spear': 15, 'axe': 20}

prompt = ':->'

path_doc = str(os.path.dirname(__file__) + '/../docs/build/html/index.html')
path_transl = str(os.path.dirname(__file__) + '/../po')

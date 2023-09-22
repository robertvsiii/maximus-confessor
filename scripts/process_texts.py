import json

from tesserae.db import TessMongoConnection
from tesserae.db.entities import Match, Text, Token, Unit
from tesserae.utils import TessFile
from tesserae.tokenizers import GreekTokenizer, LatinTokenizer
from tesserae.unitizer import Unitizer
from tesserae.matchers.sparse_encoding import SparseMatrixSearch

corpus = 'maximus'
if corpus == 'maximus':
    metafile = '/home/administrador/maximus-confessor/data/maximus_texts.json'
elif corpus == 'greek':
    metafile = '/home/administrador/maximus-confessor/data/text_metadata_greek.json'

# Set up the connection and clean up the database
connection = TessMongoConnection('127.0.0.1', 27017, None, None, db='tesserae_cb')

with open(metafile, 'r') as f:
    text_meta = json.load(f)

texts = []
for t in text_meta:
    texts.append(Text.json_decode(t))
result = connection.insert(texts)
print('Inserted {} texts.'.format(len(result.inserted_ids)))

for text in texts:
    tessfile = TessFile(text.path, metadata=text)
    tokenizer = GreekTokenizer(connection) if tessfile.metadata.language == 'greek' else LatinTokenizer(connection)
    try:
        tokens, tags, features = tokenizer.tokenize(tessfile.read(), text=tessfile.metadata)
        result = connection.insert(features)
        result = connection.insert(tokens)
    except:
        print(text.title+' too large!')

    #unitizer = Unitizer()
    #lines, phrases = unitizer.unitize(tokens, tags, tessfile.metadata)
    #try:
    #    result = connection.insert(lines + phrases)
    #except:
    #    print(text.title+' too large!')
print(text.title+' is last text')
print('done')
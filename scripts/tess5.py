import json

from tesserae.db import TessMongoConnection
from tesserae.db.entities import Match, Text, Token, Unit
from tesserae.utils import TessFile
from tesserae.tokenizers import GreekTokenizer, LatinTokenizer
from tesserae.unitizer import Unitizer
from tesserae.matchers import AggregationMatcher
from tesserae.matchers.sparse_encoding import SparseMatrixSearch

connection = TessMongoConnection('127.0.0.1', 27017, None, None, 'tesstest')

with open('text_metadata.json', 'r') as f:
    text_meta = json.load(f)

texts = []
for t in text_meta:
    texts.append(Text.json_decode(t))
result = connection.insert(texts)

for text in texts:
    tessfile = TessFile(text.path, metadata=text)
    tokenizer = GreekTokenizer(connection) if tessfile.metadata.language == 'greek' else LatinTokenizer(connection)
    tokens, tags, features = tokenizer.tokenize2(tessfile.read(), text=tessfile.metadata)
    result = connection.insert(features)

    unitizer = Unitizer()
    lines, phrases = unitizer.unitize(tokens, tags, tessfile.metadata)
    result = connection.insert(lines + phrases)
    print('Inserted {} units out of {}.'.format(len(result.inserted_ids), len(lines + phrases)))
    result = connection.insert(tokens)
    print('Inserted {} tokens out of {}.'.format(len(result.inserted_ids), len(tokens)))

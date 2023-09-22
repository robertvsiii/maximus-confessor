import pandas as pd
from tesserae.db import TessMongoConnection
from tesserae.utils.calculations import get_text_frequencies

connection_cb = TessMongoConnection('127.0.0.1', 27017, None, None, db='tesserae_cb')
texts = connection_cb.find('texts')
freqs = pd.DataFrame()
for text in texts:
    freqs=freqs.join(get_text_frequencies(connection_cb,str(text.id)),how='outer')
freqs = freqs.fillna(value=0).astype('int64')

freqs.to_excel('frequencies.xlsx')
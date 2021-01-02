# REQUIRES:
#   pycryptdome: python -m pip install pycryptodome
#   protobuf: python -m pip install protobuf

from utils.keys import KeyScheduler as ks
import utils.parser as parser
from multiprocessing import Pool
from multiprocessing import cpu_count 


key_scheduler = ks()

tek = b'\xfd=\xf1\xb1%\xa2\x1a(\xf1\xd7to\xd5\xa4e8'

rpi1 = key_scheduler.tek_to_rpi(tek, 2656789)
print(rpi1.hex())
res = b';e3:S\x83\xd8\xc4\xd64Fr\xa1Ic\xde' 
print(res.hex())
assert rpi1 == res, "rpi is wrong"


rpi2 = key_scheduler.tek_to_rpi(tek, 2656788)
print(rpi2.hex())
res = b'\x93\x86\xbe\xadj\x02\x12\xd6 \\f]\xb6L\xcf\xe4'
print(res.hex())
assert rpi2 == res, "rpi is wrong"




aem = key_scheduler.decrypt_associated_metadata(tek, rpi2, b'\xa4\xe4H\x9c')
print(aem.hex)
#res = ""
#assert aem == res, "aem is wrong"


aem = key_scheduler.decrypt_associated_metadata(tek, rpi1, b'=\x16p1')
print(aem.hex)
#res = ""
#assert aem == res, "aem is wrong"

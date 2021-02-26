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
res = b';e3:S\x83\xd8\xc4\xd64Fr\xa1Ic\xde' 
assert rpi1 == res, 'Expected RPI of {} but got {}.'.format(res,rpi1)

rpi2 = key_scheduler.tek_to_rpi(tek, 2656788)
res = b'\x93\x86\xbe\xadj\x02\x12\xd6 \\f]\xb6L\xcf\xe4'
assert rpi2 == res, 'Expected RPI of {} but got {}.'.format(res,rpi2)

tek2 = b'\xa4\xae\xf7\x91\xc0\xaa2b\xca\xdfI\x93\x07\xec\xa7\xee'
rpi3 = key_scheduler.tek_to_rpi(tek2 ,2680461)
res = b'\xc35d`\xec\x99\xf6\xd1\x9aRy\x187\xd7S?'
assert rpi3 == res, 'Expected RPI of {} but got {}.'.format(res,rpi3)

tek3 = b'\xa4\xae\xf7\x91\xc0\xaa2b\xca\xdfI\x93\x07\xec\xa7\xee'
rpi4 = key_scheduler.tek_to_rpi(tek3, 2680463)
res = b'\xc9\x1e\x9e\xd7\x12\xd9\xb5\x17\xf8\xb2\xe6\xfc\x03\xf5\xff\xa7'
assert rpi4 == res, 'Expected RPI of {} but got {}.'.format(res,rpi4)

print('All TEK derivation tests successful.')

AEM_TEST_FORMAT_STRING = 'Version: {}.{}. Power Level: {}'

v_major,v_minor, pl = key_scheduler.decrypt_associated_metadata(tek, rpi2, b'\xa4\xe4H\x9c')
print(AEM_TEST_FORMAT_STRING.format(v_major,v_minor, pl))
assert v_major == 1, 'Expected major version of {}, but got {}.'.format(3, v_major)
assert v_minor == 1, 'Expected minor version of {}, but got {}.'.format(0, v_minor)
assert pl <= 128 and pl >= -128, 'Wrong transmission power level. Expected {}, but got {}.'.format("value between -128 and 128", pl)
#assert aem == res, 'aem is wrong'

v_major,v_minor, pl = key_scheduler.decrypt_associated_metadata(tek, rpi1, b'=\x16p1')
print(AEM_TEST_FORMAT_STRING.format(v_major,v_minor, pl))
assert v_major == 1, 'Expected major version of {}, but got {}.'.format(0, v_major)
assert v_minor == 1, 'Expected minor version of {}, but got {}.'.format(0, v_minor)
assert pl <= 128 and pl >= -128, 'Wrong transmission power level. Expected {}, but got {}.'.format("value between -128 and 128", pl)
#res = ''
#assert aem == res, 'aem is wrong'

v_major,v_minor, pl = key_scheduler.decrypt_associated_metadata(tek2, rpi3, b'\xa2Y\xa9w')
print(AEM_TEST_FORMAT_STRING.format(v_major,v_minor, pl))
assert v_major == 1, 'Expected major version of {}, but got {}.'.format(1, v_major)
assert v_minor == 1, 'Expected minor version of {}, but got {}.'.format(0, v_minor)
assert pl <= 128 and pl >= -128, 'Wrong transmission power level. Expected {}, but got {}.'.format("value between -128 and 128", pl)

v_major,v_minor, pl = key_scheduler.decrypt_associated_metadata(tek3, rpi4, b'\xaeo\xa6/')
print(AEM_TEST_FORMAT_STRING.format(v_major,v_minor, pl))
assert v_major == 1, 'Expected major version of {}, but got {}.'.format(2, v_major)
assert v_minor == 1, 'Expected minor version of {}, but got {}.'.format(1, v_minor)
assert pl <= 128 and pl >= -128, 'Wrong transmission power level. Expected {}, but got {}.'.format("value between -128 and 128", pl)

print('All AEM tests successful.')

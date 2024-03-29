from utils.ccrypt import CryptoHelper as c
import struct

class KeyScheduler:
    """ Functions for Key Scheduling
    """
    def __init__(self):
        self.crypto = c()
    
    def tek_to_rpi(self, tke: bytes,en_interval_number: int) -> bytes:
        """Key Schedule for deriving the Rolling Proximity Identifier (RPI) from the Temporary Exposure Key (TEK)

        Args:
            tke (bytes): The Temporary Exposure Key to generate a Rolling Proximity Identifier for.
            en_interval_number (int): Given ENIntervalNumber as input for the RPI derivation.

        Returns:
            bytes: A byte representation of the RPI.
        """
        rpik = self.crypto.hkdf(tke,None,'EN-RPIK'.encode('utf-8'),16)
        enin = en_interval_number.to_bytes(4,'little')
        padded_data = bytes().join([bytes('EN-RPI','utf-8'), bytes.fromhex('00 00 00 00 00 00'), enin])
        rpi = self.crypto.aes_ecb_encryption(rpik, padded_data)
        
        return rpi

    def decrypt_associated_metadata(self, tke: bytes, rpi: bytes, aem: bytes):
        #TODO implement length checks
        aemk = self.crypto.hkdf(tke,None,'EN-AEMK'.encode('utf-8'),16)
        data = self.crypto.aes_ctr_decryption(aemk, rpi, aem)
        
        version_major_bitmap = 192
        version_minor_bitmap = 48
        version_major = (data[0] & version_major_bitmap) >> 6
        version_minor = (data[0] & version_minor_bitmap) >> 4

        return version_major,version_minor, int.from_bytes(data[1:2],'big', signed=True)
        #TODO Split into 4 bytes
        # A 4 byte Associated Encrypted Metadata that contains the following (LSB first):
        #i. Byte 0 — Versioning. 
        #   • Bits 7:6 — Major version (01). 
        #   • Bits 5:4 — Minor version (00). 
        #   • Bits 3:0 — Reserved for future use.

        #ii. Byte 1 — Transmit power level.
        #   • This is the measured radiated transmit power of Bluetooth Advertisement packets, and is used to improve distance approximation. The range of this field shall be -127 to +127 dBm.
        #iii. Byte 2 — Reserved for future use. 
        #iv. Byte 3 — Reserved for future use. 
    
    
    def dam_all(self, tke: bytes, rpi: bytes, aem: bytes):
        aemk = self.crypto.hkdf(tke,None,'EN-AEMK'.encode('utf-8'),16)
        data = self.crypto.aes_ctr_decryption(aemk, rpi, aem)
        return data
    
    def eam_all(self, tke: bytes, rpi: bytes, daem: bytes):
        aemk = self.crypto.hkdf(tke,None,'EN-AEMK'.encode('utf-8'),16)
        data = self.crypto.aes_ctr_encryption(aemk, rpi, daem)
        return data
        

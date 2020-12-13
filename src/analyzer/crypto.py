import time
import numpy
import Crypto.Cipher.AES as AES
import Crypto.Util.Padding as pad

class CryptoHelper:
    """Cryptographical Helper Functions for Exposure Notification key scheduling.
    """
    def en_interval_number(self, timestamp: time) -> numpy.uint32:
        """This function provides a number for each 10 minute time window that’s shared between all devices participating in the protocol. These time windows are derived from timestamps in Unix Epoch Time.

        Args:
            timestamp (time): timestamp in Unix Epoch Time and returns a 32-bit unsigned litte-endian value.

        Returns:
            uint32:  a 32-bit (uint32_t) unsigned little-endian value. 
        """
        seconds = time.time()
        intervalNumber = seconds / (60 * 10)
        return numpy.uint32(intervalNumber)

    def aes_ecb_encryption(key: bytes, data: bytes) -> bytes:
        """AES-128-ECB (Electronic Codebook Mode) Encryption of 16 bytes data.

        Args:
            key (bytes): 128 bit = 16 byte Key.
            data (bytes): 128 bit = 16 byte Data.

        Raises:
            ValueError: Raise exception if Args length is not 16 byte.

        Returns:
            bytes: AES-128 encryption data as bytes value of input data.
        """
        if len(key) != 16 | len(data) != 16:
            raise ValueError("Key and data requires length of 16 bytes.")
        
        cipher = AES.new(key,AES.MODE_ECB)
        enc_data = cipher.encrypt(data)
        return enc_data
    
    def hkdf: 
        raise NotImplementedError
# Test  
c = CryptoHelper()
value = c.en_interval_number(time.localtime()
print(value)
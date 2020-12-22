import time
import Crypto.Cipher.AES as AES
import Crypto.Util.Padding as pad
import Crypto.Protocol.KDF as KDF
import Crypto.Hash.SHA256 as SHA256

class CryptoHelper:
    """Cryptographical Helper Functions for Exposure Notification key scheduling.
    """
    def en_interval_number(self, timestamp: time) -> bytes:
        """
        This function provides a number for each 10 minute time window that’s shared between all devices participating in the protocol. These time windows are derived from timestamps in Unix Epoch Time.

        Args:
            timestamp (time): timestamp in Unix Epoch Time and returns a 32-bit unsigned litte-endian value.

        Returns:
            uint32:  a 32-bit unsigned little-endian value. 
        """
        seconds = time.time()
        intervalNumber = seconds / (60 * 10)
        return int(intervalNumber).to_bytes(4,'little')

    def aes_ecb_encryption(self, key: bytes, data: bytes) -> bytes:
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
    
    def hkdf(self,key_master_secret: bytes, salt: bytes, info: str, output_length: int) -> bytes:
        """Derive one or more keys from a master secret using the HMAC-based KDF defined in RFC5869.

        Args:
            key_master_secret (bytes): The unguessable value used by the KDF to generate the other keys. It must be a high-entropy secret, though not necessarily uniform. It must not be a password.
            salt (bytes): A non-secret, reusable value that strengthens the randomness extraction step. Ideally, it is as long as the digest size of the chosen hash. If empty, a string of zeroes in used.
            info (str): Identifier describing what the keys are used for.
            output_length (int): The length in bytes of every derived key.

        Returns:
            [type]: A byte string or a tuple of byte strings.
        """
        key = KDF.HKDF(key_master_secret, output_length, salt, SHA256, 1, info)
        return key

    def aes_ctr_decryption(self, key: bytes, iv: bytes, data: bytes) -> bytes:
        """Decryption of AES-CTR encrypted data.

        Args:
            key (bytes): [description]
            iv (bytes): [description]
            data (bytes): [description]

        Returns:
            bytes: [description]
        """
        cipher = AES.new(key, AES.MODE_CBC, initial_value=iv)
        return cipher.decrypt(data) 

    

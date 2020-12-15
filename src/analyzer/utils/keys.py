from utils.crypto import CryptoHelper as c

class KeyScheduler:
    """ Functions for Key Scheduling
    """
    def tek_to_rpi(self, tke: bytes,en_interval_number: int) -> bytes:
        """Key Schedule for deriving the Rolling Proximity Identifier (RPI) from the Temporary Exposure Key (TEK)

        Args:
            tke (bytes): The Temporary Exposure Key to generate a Rolling Proximity Identifier for.
            en_interval_number (int): Given ENIntervalNumber as input for the RPI derivation.

        Returns:
            bytes: A byte representation of the RPI.
        """
        crpt = c()
        rpik = crpt.hkdf(tke,None,"EN-RPIK".encode("utf-8"),16)
        enin = en_interval_number.to_bytes(4,'little')
        padded_data = bytes().join([bytes("EN-RPI","utf-8"), bytes.fromhex("00 00 00 00 00 00"), enin])
        rpi = crpt.aes_ecb_encryption(rpik, padded_data)
        
        return rpi
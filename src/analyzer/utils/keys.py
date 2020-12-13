from utils.crypto import CryptoHelper as c

class KeyScheduler:
    """ Functions for Key Scheduling
    """
    def tek_to_rpi(tke: bytes, time: timestamp) -> bytes:
        """Key Schedule for deriving the Rolling Proximity Identifier (RPI) from the Temporary Exposure Key (TEK)

        Args:
            tke (bytes): The Temporary Exposure Key to generate a Rolling Proximity Identifier for.
            time (timestamp): The time to derive an ENIntervalNumber as input for the RPI derivation.

        Returns:
            bytes: A byte representation of the RPI.
        """
        rpik = c.hkdf(tke,None,"EN-RPIK".encode("utf-8"),16)
        enin = en_interval_number(time)
        padded_data = bytes().join([bytes("EN-RPI","utf-8"), bytes.fromhex("00 00 00 00 00 00"), enin])
        rpi = c.aes_ecb_encryption(rpik, padded_data)
        
        return rpi
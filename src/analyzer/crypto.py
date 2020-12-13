import time
import numpy

class CryptoHelper:
    """Cryptographical Helper Functions for Exposure Notification key scheduling 
    """
    def eNIntervalNumber(self, timestamp: time) -> numpy.uint32:
        """This function provides a number for each 10 minute time window that’s shared between all devices participating in the protocol. These time windows are derived from timestamps in Unix Epoch Time.

        Args:
            timestamp (time): timestamp in Unix Epoch Time and returns a 32-bit unsigned litte-endian value

        Returns:
            uint32:  a 32-bit (uint32_t) unsigned little-endian value. 
        """
        seconds = time.time()
        intervalNumber = seconds / (60 * 10)
        return numpy.uint32(intervalNumber)

# Test  
c = CryptoHelper()
value = c.eNIntervalNumber(time.localtime(2545925769))
print(value)


import threading
import time
from settings import rlog

class TokenBucket:
    """
    A Token Bucket Rate Limiter implementation.

    This class implements the Token Bucket algorithm for rate limiting. It maintains a bucket
    with a fixed number of tokens and refills the bucket with tokens at a specified time interval.
    Each time a token is consumed, the bucket loses one token. If no tokens are available, consumption
    is denied until the bucket is refilled.

    Attributes:
        bucketsize (int): The maximum number of tokens the bucket can hold.
        refill_time (int): The time interval in seconds between refills.
        tokensleft (int): The current number of tokens in the bucket.
        lock (threading.Lock): A lock to synchronize access to the bucket (thread safety).
    """

    def __init__(self, bucketsize: int = 10, refill_time: int = 60):
        """
        Initializes the TokenBucket with the specified size and refill time.

        Args:
            bucketsize (int): The size of the token bucket (default 10).
            refill_time (int): The time in seconds between each refill (default 60 seconds).
        """
        self.bucketsize: int = bucketsize
        self.refill_time: int = refill_time
        self.tokensleft: int = bucketsize
        self.lock: threading.Lock = threading.Lock()  # Ensures thread-safe access to tokens
        self._start_refill_thread()

    def _start_refill_thread(self) -> None:
        """
        Starts a background thread that refills the token bucket periodically.
        """
        refill_thread = threading.Thread(target=self._refill)
        refill_thread.daemon = True
        refill_thread.start()

    def _refill(self) -> None:
        """
        Periodically refills the token bucket with tokens at the specified refill time interval.
        
        This method runs in a separate background thread and continuously refills the bucket
        after each `refill_time` period.
        """
        while True:
            time.sleep(self.refill_time)
            with self.lock:
                rlog.info("Refilling Token Bucket")
                self.tokensleft = self.bucketsize

    def consume(self) -> bool:
        """
        Attempts to consume a token from the bucket.

        If a token is available (tokensleft > 0), one token is consumed, and the method returns True.
        If no tokens are available, the method returns False.

        Returns:
            bool: True if a token was consumed, False if the bucket is empty.
        """
        with self.lock:  # Ensure safe access to `tokensleft`
            if self.tokensleft == 0:
                return False
            rlog.debug("Consumed token")
            self.tokensleft -= 1
            return True

# rate-limiter

In a network system, a rate limiter is used to control the rate of traffic sent by a client or aservice. In the HTTP world, a rate limiter limits the number of client requests allowed to besent over a specified period. If the API request count exceeds the threshold defined by therate limiter, all the excess calls are blocked.

## Algorithms
1. Token bucket
2. Leaking bucket 
3. Fixed window counter
4. Sliding window log
5. Sliding window counter

### Token bucket
1. Used by Amazon, Stripe
2. Contianer as pre-defined capacity, once full no more tokens are added

### Leaky Bucket
1. Similar to Token bucket
2. Based on FIFO
3. When request comes it checks if queue is empty
    1. If empty adds to queue
    2. Else drops the request
4. Requests are processed at fixed rate
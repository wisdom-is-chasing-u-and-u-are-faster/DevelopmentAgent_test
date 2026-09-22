-- reserve_stock.lua
-- Atomic stock reservation script for Redis 7
-- KEYS[1] = stock:available:{variant_id}
-- KEYS[2] = res:{reservation_id}
-- ARGV[1] = quantity to reserve
-- ARGV[2] = TTL in seconds (600s)
-- ARGV[3] = customer_id
-- ARGV[4] = variant_id

local stock_key = KEYS[1]
local res_key = KEYS[2]
local qty = tonumber(ARGV[1])
local ttl = tonumber(ARGV[2])
local customer_id = ARGV[3]
local variant_id = ARGV[4]

local current_stock = tonumber(redis.call('GET', stock_key) or "0")
if current_stock < qty then
    return 0 -- Insufficient stock
end

-- Decrement stock atomically
redis.call('DECRBY', stock_key, qty)

-- Store reservation metadata
redis.call('HSET', res_key,
    'variant_id', variant_id,
    'customer_id', customer_id,
    'quantity', qty,
    'created_at', redis.call('TIME')[1]
)
redis.call('EXPIRE', res_key, ttl)

return 1 -- Success

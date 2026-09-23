package repository

import (
	"sync"
	"time"
)

type CacheItem struct {
	Value      interface{}
	Expiration time.Time
}

type InMemLRUCache struct {
	mu    sync.RWMutex
	items map[string]CacheItem
	ttl   time.Duration
}

func NewInMemLRUCache(ttl time.Duration) *InMemLRUCache {
	return &InMemLRUCache{
		items: make(map[string]CacheItem),
		ttl:   ttl,
	}
}

func (c *InMemLRUCache) Get(key string) (interface{}, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()
	item, found := c.items[key]
	if !found || time.Now().After(item.Expiration) {
		return nil, false
	}
	return item.Value, true
}

func (c *InMemLRUCache) Set(key string, val interface{}) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.items[key] = CacheItem{
		Value:      val,
		Expiration: time.Now().Add(c.ttl),
	}
}

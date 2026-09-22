import Redis, { Cluster } from 'ioredis';
import fs from 'fs';
import path from 'path';

let redisClient: Redis | Cluster;
let luaSha: string = '';

export function getRedisClient(): Redis | Cluster {
  if (!redisClient) {
    const host = process.env.REDIS_HOST || '127.0.0.1';
    const port = parseInt(process.env.REDIS_PORT || '6379', 10);
    redisClient = new Redis({ host, port });
  }
  return redisClient;
}

export async function reserveStockLuaSha(): Promise<string> {
  if (!luaSha) {
    const client = getRedisClient();
    const luaPath = path.join(__dirname, '../scripts/reserve_stock.lua');
    const luaScript = fs.readFileSync(luaPath, 'utf8');
    luaSha = await client.script('LOAD', luaScript) as string;
  }
  return luaSha;
}

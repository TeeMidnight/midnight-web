# server_status.py
import aiohttp
import asyncio
from aiohttp import web
import json
import time

MASTER_SERVER_URL = "https://master2.ddnet.org/ddnet/15/servers.json"

cache = {
    "data": [],
    "last_fetch": 0,
    "ttl": 15
}

session: aiohttp.ClientSession = None

async def fetch_servers_from_master():
    """从 DDNet 主服务器异步获取并筛选服务器列表"""
    try:
        async with session.get(MASTER_SERVER_URL, timeout=8) as resp:
            if resp.status != 200:
                print(f"HTTP {resp.status}: 无法获取服务器列表")
                return []

            data = await resp.json()
            servers = data.get("servers", [])
            filtered = []

            for sv in servers:
                info = sv.get("info", {})
                name = info.get("name", "")
                if "Mid·Night" in name:
                    # 提取第一个 UDP 地址
                    ip_port = "未知"
                    for addr in sv.get("addresses", []):
                        if addr.startswith("tw-"):
                            try:
                                ip_port = addr.split("://")[1]
                                break
                            except:
                                continue

                    game_type = info.get("game_type", "未知")
                    num_players = len(info.get("clients", []))
                    max_players = info.get("max_players", 16)
                    map_name = info.get("map", {}).get("name", "未知")

                    filtered.append({
                        "name": name,
                        "game_type": game_type,
                        "num_players": num_players,
                        "max_players": max_players,
                        "map_name": map_name,
                        "ip_port": ip_port,
                        "avatar_url": f"/static/img/servers/{game_type.lower()}.png"
                    })

            # 按玩家数降序排序
            filtered.sort(key=lambda x: x["num_players"], reverse=True)
            return filtered

    except asyncio.TimeoutError:
        print("请求超时")
    except Exception as e:
        print(f"获取服务器列表失败: {e}")
    return []


async def get_server_list() -> list[dict]: 
    """
    获取服务器列表数据（带缓存）
    """
    now = time.time()
    if now - cache["last_fetch"] < cache["ttl"]:
        print("使用缓存数据")
        return cache["data"]

    print("正在更新服务器列表...")
    new_list = await fetch_servers_from_master()
    cache["data"] = new_list
    cache["last_fetch"] = now
    return new_list

async def init():
    global session
    session = aiohttp.ClientSession()

async def shutdown():
    global session
    await session.close()


# =============== 测试 ===============
async def test():
    await init()
    servers = await get_server_list()
    print("\n筛选出的服务器:")
    for s in servers:
        print(f"{s['name']} | {s['map_name']} | {s['num_players']}/{s['max_players']} | {s['game_type']} | {s['ip_port']}")
    await shutdown()

if __name__ == '__main__':
    asyncio.run(test())